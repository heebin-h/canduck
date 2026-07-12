// TB6612FNG 휠 모터 제어 (N20 ×2).
// arduino-esp32 2.x LEDC API 기준 (platformio espressif32@^6.7.0).
// DevKit 단독에서도 GPIO 출력뿐이라 무해 — 프로토콜 테스트 가능.

#include "motor.h"
#include "pins.h"

namespace canduck {

namespace {

constexpr uint8_t LEDC_CH_A = 0;
constexpr uint8_t LEDC_CH_B = 1;
constexpr uint32_t PWM_FREQ = 20000;  // 20kHz — 가청 노이즈 회피
constexpr uint8_t PWM_RES_BITS = 8;   // duty 0~255
constexpr int16_t DUTY_MAX = 255;

void apply_channel(uint8_t in1, uint8_t in2, uint8_t ledc_ch, int16_t value) {
    if (value > 0) {
        digitalWrite(in1, HIGH);
        digitalWrite(in2, LOW);
        ledcWrite(ledc_ch, (uint32_t)value);
    } else if (value < 0) {
        digitalWrite(in1, LOW);
        digitalWrite(in2, HIGH);
        ledcWrite(ledc_ch, (uint32_t)(-value));
    } else {
        // coast: IN1=IN2=LOW, duty 0
        digitalWrite(in1, LOW);
        digitalWrite(in2, LOW);
        ledcWrite(ledc_ch, 0);
    }
}

}  // namespace

void motor_init() {
    pinMode(PIN_MOTOR_AIN1, OUTPUT);
    pinMode(PIN_MOTOR_AIN2, OUTPUT);
    pinMode(PIN_MOTOR_BIN1, OUTPUT);
    pinMode(PIN_MOTOR_BIN2, OUTPUT);
    ledcSetup(LEDC_CH_A, PWM_FREQ, PWM_RES_BITS);
    ledcSetup(LEDC_CH_B, PWM_FREQ, PWM_RES_BITS);
    ledcAttachPin(PIN_MOTOR_PWMA, LEDC_CH_A);
    ledcAttachPin(PIN_MOTOR_PWMB, LEDC_CH_B);
    motor_stop();
}

bool motor_set(int16_t left, int16_t right) {
    if (left < -DUTY_MAX || left > DUTY_MAX) return false;
    if (right < -DUTY_MAX || right > DUTY_MAX) return false;
    apply_channel(PIN_MOTOR_AIN1, PIN_MOTOR_AIN2, LEDC_CH_A, left);
    apply_channel(PIN_MOTOR_BIN1, PIN_MOTOR_BIN2, LEDC_CH_B, right);
    return true;
}

void motor_stop() {
    apply_channel(PIN_MOTOR_AIN1, PIN_MOTOR_AIN2, LEDC_CH_A, 0);
    apply_channel(PIN_MOTOR_BIN1, PIN_MOTOR_BIN2, LEDC_CH_B, 0);
}

}  // namespace canduck
