// UART 프로토콜 파서. docs/architecture.md 의 명령 표를 구현.
//   '>' 접두 = RPi → ESP32 명령
//   '<' 접두 = ESP32 → RPi 응답/이벤트

#include "comm.h"
#include "servo_ctrl.h"
#include "poses.h"
#include "motor.h"
#include "vbat.h"

namespace canduck {

namespace {

char line_buf[COMM_LINE_MAX];
size_t line_len = 0;
bool line_overflow = false;  // true면 다음 '\n'까지 버림

// 정수 토큰 엄격 파싱. atoi와 달리 "abc"/"12x"는 실패, 범위 밖은 실패 (int16_t 랩어라운드 방지).
bool parse_long(const char* s, long lo, long hi, long& out) {
    if (!s || !*s) return false;
    char* end = nullptr;
    long v = strtol(s, &end, 10);
    if (*end != '\0' || v < lo || v > hi) return false;
    out = v;
    return true;
}

constexpr long DEG_LO = INT16_MIN, DEG_HI = INT16_MAX;  // 각도 범위 판정은 servo_* 가 함
constexpr long DUR_LO = 0, DUR_HI = UINT16_MAX;

void send_ack(const char* original) {
    Serial.print("< ACK ");
    Serial.println(original);
}

void dispatch(char* line) {
    // 첫 토큰이 명령
    char* cmd = strtok(line, " \t");
    if (!cmd) return;

    if (strcmp(cmd, "PING") == 0) {
        Serial.println("< PONG");
        return;
    }

    if (strcmp(cmd, "HEAD") == 0) {
        char* yaw_s = strtok(nullptr, " \t");
        char* pitch_s = strtok(nullptr, " \t");
        char* dur_s = strtok(nullptr, " \t");
        if (!yaw_s || !pitch_s || !dur_s) {
            emit_event_err(CmdResult::ParseError, "HEAD needs yaw pitch dur");
            return;
        }
        long yaw, pitch, dur;
        if (!parse_long(yaw_s, DEG_LO, DEG_HI, yaw) || !parse_long(pitch_s, DEG_LO, DEG_HI, pitch) ||
            !parse_long(dur_s, DUR_LO, DUR_HI, dur)) {
            emit_event_err(CmdResult::ParseError, "HEAD bad number");
            return;
        }
        if (servo_head_move(yaw, pitch, dur)) {
            send_ack("HEAD");
        } else {
            emit_event_err(CmdResult::OutOfRange, "HEAD range");
        }
        return;
    }

    if (strcmp(cmd, "ARM") == 0) {
        char* side_s = strtok(nullptr, " \t");
        char* sh_s = strtok(nullptr, " \t");
        char* el_s = strtok(nullptr, " \t");
        char* dur_s = strtok(nullptr, " \t");
        if (!side_s || !sh_s || !el_s || !dur_s) {
            emit_event_err(CmdResult::ParseError, "ARM needs side shoulder elbow dur");
            return;
        }
        long sh, el, dur;
        if (!parse_long(sh_s, DEG_LO, DEG_HI, sh) || !parse_long(el_s, DEG_LO, DEG_HI, el) ||
            !parse_long(dur_s, DUR_LO, DUR_HI, dur)) {
            emit_event_err(CmdResult::ParseError, "ARM bad number");
            return;
        }
        if (servo_arm_move(side_s[0], sh, el, dur)) {
            send_ack("ARM");
        } else {
            emit_event_err(CmdResult::OutOfRange, "ARM side/range");
        }
        return;
    }

    if (strcmp(cmd, "LEG") == 0) {
        char* side_s = strtok(nullptr, " \t");
        char* ang_s = strtok(nullptr, " \t");
        char* dur_s = strtok(nullptr, " \t");
        if (!side_s || !ang_s || !dur_s) {
            emit_event_err(CmdResult::ParseError, "LEG needs side angle dur");
            return;
        }
        long ang, dur;
        if (!parse_long(ang_s, DEG_LO, DEG_HI, ang) || !parse_long(dur_s, DUR_LO, DUR_HI, dur)) {
            emit_event_err(CmdResult::ParseError, "LEG bad number");
            return;
        }
        if (servo_leg_move(side_s[0], ang, dur)) {
            send_ack("LEG");
        } else {
            emit_event_err(CmdResult::OutOfRange, "LEG side/range");
        }
        return;
    }

    if (strcmp(cmd, "MOTOR") == 0) {
        char* l_s = strtok(nullptr, " \t");
        char* r_s = strtok(nullptr, " \t");
        if (!l_s || !r_s) {
            emit_event_err(CmdResult::ParseError, "MOTOR needs left right");
            return;
        }
        long l, r;
        if (!parse_long(l_s, INT16_MIN, INT16_MAX, l) || !parse_long(r_s, INT16_MIN, INT16_MAX, r)) {
            emit_event_err(CmdResult::ParseError, "MOTOR bad number");
            return;
        }
        if (motor_set(l, r)) {
            send_ack("MOTOR");
        } else {
            emit_event_err(CmdResult::OutOfRange, "MOTOR -255~255");
        }
        return;
    }

    if (strcmp(cmd, "QUERY") == 0) {
        char* what = strtok(nullptr, " \t");
        if (!what) {
            emit_event_err(CmdResult::ParseError, "QUERY needs imu/touch/vbat");
            return;
        }
        if (strcmp(what, "vbat") == 0) {
            emit_event_vbat(vbat_read_mv());
        } else {
            // imu/touch는 W4 (PCB + 센서 실장) 이후 구현
            emit_event_err(CmdResult::I2CFail, "not implemented until W4");
        }
        return;
    }

    if (strcmp(cmd, "POSE") == 0) {
        char* name = strtok(nullptr, " \t");
        if (!name) {
            emit_event_err(CmdResult::ParseError, "POSE needs name");
            return;
        }
        if (poses_trigger(name)) {
            send_ack("POSE");
        } else {
            emit_event_err(CmdResult::UnknownPose, name);
        }
        return;
    }

    if (strcmp(cmd, "STOP") == 0) {
        poses_abort();  // 시퀀스부터 끊어야 다음 tick에 키프레임이 재발사되지 않음
        servo_stop_all();
        motor_stop();
        send_ack("STOP");
        return;
    }

    if (strcmp(cmd, "ENABLE") == 0) {
        char* arg = strtok(nullptr, " \t");
        if (!arg) {
            emit_event_err(CmdResult::ParseError, "ENABLE needs 0/1");
            return;
        }
        bool en = atoi(arg) != 0;
        servo_set_enable(en);
        if (!en) motor_stop();  // OE#는 서보만 게이트 — 모터는 여기서 정지
        send_ack("ENABLE");
        return;
    }

    emit_event_err(CmdResult::ParseError, cmd);
}

}  // namespace

void comm_init() {
    Serial.begin(CANDUCK_UART_BAUD);
    line_len = 0;
    emit_event_boot(CANDUCK_FW_VERSION);
}

void comm_loop() {
    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\r') continue;
        if (c == '\n') {
            line_buf[line_len] = '\0';
            if (!line_overflow && line_len > 0 && line_buf[0] == '>') {
                dispatch(line_buf + 1);  // '>' 접두 제거
            }
            line_len = 0;
            line_overflow = false;
            continue;
        }
        if (line_overflow) continue;  // 넘친 라인의 나머지는 '\n'까지 폐기 (꼬리 오실행·ERR 반복 방지)
        if (line_len < COMM_LINE_MAX - 1) {
            line_buf[line_len++] = c;
        } else {
            line_len = 0;
            line_overflow = true;
            emit_event_err(CmdResult::ParseError, "line overflow");
        }
    }
}

void emit_event_tap(char axis, int16_t intensity) {
    Serial.printf("< TAP %c %d\n", axis, intensity);
}

void emit_event_shake(int16_t intensity) {
    Serial.printf("< SHAKE %d\n", intensity);
}

void emit_event_touch(uint8_t channel, bool state) {
    Serial.printf("< TOUCH %u %d\n", channel, state ? 1 : 0);
}

void emit_event_done(const char* cmd) {
    Serial.print("< DONE ");
    Serial.println(cmd);
}

void emit_event_vbat(uint16_t millivolts) {
    Serial.printf("< VBAT %u\n", millivolts);
}

void emit_event_err(CmdResult code, const char* msg) {
    Serial.printf("< ERR %u %s\n", (unsigned)code, msg ? msg : "");
}

void emit_event_boot(const char* version) {
    Serial.printf("< BOOT %s\n", version);
}

}  // namespace canduck
