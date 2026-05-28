// UART 프로토콜 파서. docs/architecture.md 의 명령 표를 구현.
//   '>' 접두 = RPi → ESP32 명령
//   '<' 접두 = ESP32 → RPi 응답/이벤트

#include "comm.h"
#include "servo_ctrl.h"
#include "poses.h"

namespace canduck {

namespace {

char line_buf[COMM_LINE_MAX];
size_t line_len = 0;

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
        int yaw = atoi(yaw_s);
        int pitch = atoi(pitch_s);
        int dur = atoi(dur_s);
        if (servo_head_move(yaw, pitch, dur)) {
            send_ack("HEAD");
        } else {
            emit_event_err(CmdResult::OutOfRange, "HEAD range");
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
        servo_stop_all();
        send_ack("STOP");
        return;
    }

    if (strcmp(cmd, "ENABLE") == 0) {
        char* arg = strtok(nullptr, " \t");
        if (!arg) {
            emit_event_err(CmdResult::ParseError, "ENABLE needs 0/1");
            return;
        }
        servo_set_enable(atoi(arg) != 0);
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
            if (line_len > 0 && line_buf[0] == '>') {
                dispatch(line_buf + 1);  // '>' 접두 제거
            }
            line_len = 0;
            continue;
        }
        if (line_len < COMM_LINE_MAX - 1) {
            line_buf[line_len++] = c;
        } else {
            line_len = 0;  // 오버플로 시 라인 폐기
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
