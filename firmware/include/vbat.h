#pragma once

#include <Arduino.h>
#include "pins.h"

namespace canduck {

// ADC 12bit, 0~3.3V, 분압 20K/10K → 입력은 실제 V_bat * (10/30) = V_bat/3
// DevKit 단독(분압 미연결)에서는 플로팅 값이 나옴 — 프로토콜 테스트용으로 무해.
inline uint16_t vbat_read_mv() {
    // analogReadMilliVolts = eFuse 캘리브레이션 반영 (선형 raw 환산은 수백 mV 오차)
    return (uint16_t)(analogReadMilliVolts(PIN_VBAT_SENSE) * 3);
}

}  // namespace canduck
