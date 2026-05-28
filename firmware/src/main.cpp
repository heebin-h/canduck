// canduck firmware entrypoint.
// 책임: UART 명령 파싱 → 서보/포즈 dispatch. 센서 폴링 후 이벤트 보고.
// 행동 결정 로직은 RPi 측 FSM에서 담당, 펌웨어는 dumb actuator.

#include <Arduino.h>
#include "pins.h"
#include "comm.h"
#include "servo_ctrl.h"
#include "poses.h"

using namespace canduck;

static uint32_t last_tick_ms = 0;
static uint32_t last_vbat_ms = 0;

static void tick_telemetry() {
    uint32_t now = millis();
    if (now - last_vbat_ms < 1000) return;
    last_vbat_ms = now;
    int raw = analogRead(PIN_VBAT_SENSE);
    // ADC 12bit, 0~3.3V, 분압 20K/10K → 입력은 실제 V_bat * (10/30) = V_bat/3
    // V_bat_mV = raw * 3300 / 4095 * 3
    uint16_t mv = (uint16_t)((uint32_t)raw * 3300UL * 3UL / 4095UL);
    emit_event_vbat(mv);
}

void setup() {
    comm_init();
    servo_init();
    poses_init();
    // 부팅 직후 서보 출력 비활성. RPi가 ENABLE 1 보내면 active.
    servo_set_enable(false);
}

void loop() {
    comm_loop();

    uint32_t now = millis();
    if (now - last_tick_ms >= 10) {
        last_tick_ms = now;
        poses_tick();
        servo_tick();
    }

    tick_telemetry();
}
