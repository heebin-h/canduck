#pragma once

#include <Arduino.h>

namespace canduck {

void poses_init();
void poses_tick();
bool poses_trigger(const char* name);
void poses_abort();  // 활성 시퀀스 즉시 중단 (STOP 경로)

}  // namespace canduck
