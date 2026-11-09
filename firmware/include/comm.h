#pragma once

#include <Arduino.h>

namespace canduck {

constexpr size_t COMM_LINE_MAX = 128;

enum class CmdResult : uint8_t {
    Ok = 0,
    ParseError = 1,
    OutOfRange = 2,
    I2CFail = 3,
    UnknownPose = 5,
};

void comm_init();
void comm_loop();

// 이벤트 송신 헬퍼 (ESP32 → RPi)
void emit_event_tap(char axis, int16_t intensity);
void emit_event_shake(int16_t intensity);
void emit_event_touch(uint8_t channel, bool state);
void emit_event_done(const char* cmd);
void emit_event_vbat(uint16_t millivolts);
void emit_event_err(CmdResult code, const char* msg);
void emit_event_boot(const char* version);

}  // namespace canduck
