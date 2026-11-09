#pragma once

#include <Arduino.h>

namespace canduck {

void motor_init();

// left/right: -255~255, 부호 = 방향, 0 = coast 정지.
bool motor_set(int16_t left, int16_t right);

void motor_stop();

}  // namespace canduck
