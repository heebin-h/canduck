#pragma once

#include <Arduino.h>

namespace canduck {

void servo_init();
void servo_tick();  // main loop 10ms 마다 호출, easing 보간 진행

bool servo_head_move(int16_t yaw_deg, int16_t pitch_deg, uint16_t duration_ms);
bool servo_arm_move(char side, int16_t shoulder_deg, int16_t elbow_deg, uint16_t duration_ms);
bool servo_leg_move(char side, int16_t angle_deg, uint16_t duration_ms);

void servo_stop_all();
void servo_set_enable(bool enable);  // PCA9685 OE# 핀 제어

// 채널별 raw 위치 설정 (포즈 엔진이 사용)
void servo_set_channel(uint8_t ch, int16_t target_deg, uint16_t duration_ms);

// 모든 채널이 모션 완료했는지
bool servo_all_idle();

}  // namespace canduck
