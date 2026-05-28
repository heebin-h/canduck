#pragma once

#include <Arduino.h>

namespace canduck {

void poses_init();
void poses_tick();
bool poses_trigger(const char* name);
bool poses_active();

}  // namespace canduck
