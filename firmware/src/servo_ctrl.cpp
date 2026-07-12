// PCA9685를 통한 서보 제어. 채널별 easing 보간 엔진.
// 호출: setup() 에서 servo_init(), loop()에서 servo_tick() 10ms 주기.

#include "servo_ctrl.h"
#include "pins.h"
#include "comm.h"
#include <Adafruit_PWMServoDriver.h>
#include <Wire.h>

namespace canduck {

namespace {

constexpr uint8_t NUM_CH = 16;
constexpr uint16_t PCA_FREQ = 50;  // 50Hz 표준 서보
constexpr uint16_t PWM_MIN = 102;  // ~0.5ms (4096 카운트 기준 50Hz)
constexpr uint16_t PWM_MAX = 512;  // ~2.5ms
constexpr int16_t ANGLE_MIN = -90;
constexpr int16_t ANGLE_MAX = 90;

Adafruit_PWMServoDriver pca(0x40);

// DevKit 단독(PCA9685 미장착)에서도 프로토콜/보간 로직을 테스트할 수 있게
// 부재 시 I2C 쓰기만 생략하는 dry-run 모드. ACK/DONE 흐름은 동일하게 동작.
bool pca_present = false;

inline void pca_write(uint8_t ch, uint16_t pwm) {
    if (pca_present) pca.setPWM(ch, 0, pwm);
}

struct ChannelState {
    int16_t start_deg = 0;
    int16_t target_deg = 0;
    uint32_t start_ms = 0;
    uint16_t duration_ms = 0;
    bool moving = false;
};

ChannelState channels[NUM_CH];

// easeInOutCubic
float ease(float t) {
    if (t < 0.5f) return 4.0f * t * t * t;
    float p = -2.0f * t + 2.0f;
    return 1.0f - p * p * p * 0.5f;
}

uint16_t deg_to_pwm(int16_t deg) {
    if (deg < ANGLE_MIN) deg = ANGLE_MIN;
    if (deg > ANGLE_MAX) deg = ANGLE_MAX;
    long span = PWM_MAX - PWM_MIN;
    long offset = ((long)(deg - ANGLE_MIN) * span) / (ANGLE_MAX - ANGLE_MIN);
    return (uint16_t)(PWM_MIN + offset);
}

}  // namespace

void servo_init() {
    pinMode(PIN_PCA9685_OE, OUTPUT);
    digitalWrite(PIN_PCA9685_OE, HIGH);  // 부팅 시 출력 disable (안전)

    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
    Wire.setClock(400000);

    // 주소 probe로 장착 여부 판정
    Wire.beginTransmission(0x40);
    pca_present = (Wire.endTransmission() == 0);

    if (pca_present) {
        pca.begin();
        pca.setOscillatorFrequency(27000000);
        pca.setPWMFreq(PCA_FREQ);
    } else {
        emit_event_err(CmdResult::I2CFail, "PCA9685 absent - servo dry-run");
    }

    for (uint8_t i = 0; i < NUM_CH; ++i) {
        channels[i] = ChannelState{};
        pca_write(i, deg_to_pwm(0));
    }
}

void servo_set_enable(bool enable) {
    digitalWrite(PIN_PCA9685_OE, enable ? LOW : HIGH);
}

void servo_set_channel(uint8_t ch, int16_t target_deg, uint16_t duration_ms) {
    if (ch >= NUM_CH) return;
    ChannelState& s = channels[ch];
    // 현재 위치를 보간 기반으로 추정 (단순화: target_deg를 직전 명령의 그것으로 가정)
    s.start_deg = s.target_deg;
    s.target_deg = target_deg;
    s.start_ms = millis();
    s.duration_ms = duration_ms == 0 ? 1 : duration_ms;
    s.moving = true;
}

void servo_tick() {
    uint32_t now = millis();
    for (uint8_t i = 0; i < NUM_CH; ++i) {
        ChannelState& s = channels[i];
        if (!s.moving) continue;
        uint32_t elapsed = now - s.start_ms;
        if (elapsed >= s.duration_ms) {
            pca_write(i, deg_to_pwm(s.target_deg));
            s.moving = false;
            continue;
        }
        float t = (float)elapsed / (float)s.duration_ms;
        float eased = ease(t);
        int16_t cur = s.start_deg + (int16_t)(eased * (s.target_deg - s.start_deg));
        pca_write(i, deg_to_pwm(cur));
    }
}

bool servo_head_move(int16_t yaw_deg, int16_t pitch_deg, uint16_t duration_ms) {
    if (yaw_deg < ANGLE_MIN || yaw_deg > ANGLE_MAX) return false;
    if (pitch_deg < ANGLE_MIN || pitch_deg > ANGLE_MAX) return false;
    servo_set_channel(CH_HEAD_YAW, yaw_deg, duration_ms);
    servo_set_channel(CH_HEAD_PITCH, pitch_deg, duration_ms);
    return true;
}

bool servo_arm_move(char side, int16_t shoulder_deg, int16_t elbow_deg, uint16_t duration_ms) {
    uint8_t sh, el;
    if (side == 'L' || side == 'l') { sh = CH_ARM_L_SHOULDER; el = CH_ARM_L_ELBOW; }
    else if (side == 'R' || side == 'r') { sh = CH_ARM_R_SHOULDER; el = CH_ARM_R_ELBOW; }
    else return false;
    servo_set_channel(sh, shoulder_deg, duration_ms);
    servo_set_channel(el, elbow_deg, duration_ms);
    return true;
}

bool servo_leg_move(char side, int16_t angle_deg, uint16_t duration_ms) {
    uint8_t ch;
    if (side == 'L' || side == 'l') ch = CH_LEG_L_SWING;
    else if (side == 'R' || side == 'r') ch = CH_LEG_R_SWING;
    else return false;
    servo_set_channel(ch, angle_deg, duration_ms);
    return true;
}

void servo_stop_all() {
    for (uint8_t i = 0; i < NUM_CH; ++i) {
        channels[i].moving = false;
        pca_write(i, deg_to_pwm(0));
    }
}

bool servo_all_idle() {
    for (uint8_t i = 0; i < NUM_CH; ++i) {
        if (channels[i].moving) return false;
    }
    return true;
}

}  // namespace canduck
