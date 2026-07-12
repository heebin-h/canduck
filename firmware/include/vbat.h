#pragma once

#include <Arduino.h>
#include "pins.h"

namespace canduck {

// ADC 12bit, 0~3.3V, 분압 20K/10K → 입력은 실제 V_bat * (10/30) = V_bat/3
// DevKit 단독(분압 미연결)에서는 플로팅 값이 나옴 — 프로토콜 테스트용으로 무해.
inline uint16_t vbat_read_mv() {
    int raw = analogRead(PIN_VBAT_SENSE);
    return (uint16_t)((uint32_t)raw * 3300UL * 3UL / 4095UL);
}

}  // namespace canduck
