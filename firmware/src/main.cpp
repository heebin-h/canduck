// canduck firmware entrypoint.
// 책임: UART 명령 파싱 → 서보/포즈 dispatch. 센서 폴링 후 이벤트 보고.
// 행동 결정 로직은 RPi 측 FSM에서 담당, 펌웨어는 dumb actuator.

#include <Arduino.h>
#include "pins.h"
#include "comm.h"
#include "servo_ctrl.h"
#include "poses.h"
#include "motor.h"
#include "vbat.h"

using namespace canduck;

static uint32_t last_tick_ms = 0;
static uint32_t last_vbat_ms = 0;

static void tick_telemetry() {
    uint32_t now = millis();
    if (now - last_vbat_ms < 1000) return;
    last_vbat_ms = now;
    emit_event_vbat(vbat_read_mv());
}

void setup() {
    comm_init();
    servo_init();
    motor_init();
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
