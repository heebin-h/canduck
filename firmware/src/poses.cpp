// 사전 정의 포즈 시퀀스. 각 포즈는 (시간, 액션) 키프레임 리스트.
// FSM은 RPi 측에서 운영, 여기는 단순 시퀀스 플레이어.

#include "poses.h"
#include "servo_ctrl.h"
#include "comm.h"
#include <string.h>

namespace canduck {

namespace {

struct Keyframe {
    uint32_t at_ms;        // 시퀀스 시작 기준 시각
    uint8_t channel;       // PCA9685 채널 (0xFF = end-of-sequence)
    int16_t target_deg;
    uint16_t duration_ms;
};

struct Pose {
    const char* name;
    const Keyframe* frames;
};

// === IDLE: 중립 자세 ===
constexpr Keyframe POSE_IDLE_FRAMES[] = {
    { 0, CH_HEAD_YAW, 0, 500 },
    { 0, CH_HEAD_PITCH, 0, 500 },
    { 0, CH_ARM_L_SHOULDER, 0, 500 },
    { 0, CH_ARM_L_ELBOW, 0, 500 },
    { 0, CH_ARM_R_SHOULDER, 0, 500 },
    { 0, CH_ARM_R_ELBOW, 0, 500 },
    { 0, CH_LEG_L_SWING, 0, 500 },
    { 0, CH_LEG_R_SWING, 0, 500 },
    { 0xFFFFFFFF, 0xFF, 0, 0 },
};

// === HEADACHE: 양손 머리 옆 + 머리 격렬 흔들기 5초 ===
constexpr Keyframe POSE_HEADACHE_FRAMES[] = {
    // t=0~500: 팔 들기
    {    0, CH_ARM_L_SHOULDER,  60, 500 },
    {    0, CH_ARM_R_SHOULDER, -60, 500 },
    // t=500~1000: 팔꿈치 굽혀 손이 머리 옆으로
    {  500, CH_ARM_L_ELBOW,  80, 500 },
    {  500, CH_ARM_R_ELBOW, -80, 500 },
    // t=1000~5000: 머리 좌우 흔들기 (8회)
    { 1000, CH_HEAD_YAW,  30, 250 },
    { 1250, CH_HEAD_YAW, -30, 250 },
    { 1500, CH_HEAD_YAW,  30, 250 },
    { 1750, CH_HEAD_YAW, -30, 250 },
    { 2000, CH_HEAD_YAW,  30, 250 },
    { 2250, CH_HEAD_YAW, -30, 250 },
    { 2500, CH_HEAD_YAW,  25, 300 },
    { 2800, CH_HEAD_YAW, -25, 300 },
    { 3100, CH_HEAD_YAW,  20, 350 },
    { 3450, CH_HEAD_YAW, -20, 350 },
    { 3800, CH_HEAD_YAW,  10, 400 },
    { 4200, CH_HEAD_YAW, -10, 400 },
    { 4600, CH_HEAD_YAW,   0, 400 },
    // t=5000~5500: 팔 내림
    { 5000, CH_ARM_L_ELBOW, 0, 500 },
    { 5000, CH_ARM_R_ELBOW, 0, 500 },
    { 5000, CH_ARM_L_SHOULDER, 0, 500 },
    { 5000, CH_ARM_R_SHOULDER, 0, 500 },
    { 0xFFFFFFFF, 0xFF, 0, 0 },
};

// === SHAKE: 단순 머리 좌우 흔들기 ===
constexpr Keyframe POSE_SHAKE_FRAMES[] = {
    {    0, CH_HEAD_YAW,  35, 200 },
    {  200, CH_HEAD_YAW, -35, 300 },
    {  500, CH_HEAD_YAW,  35, 300 },
    {  800, CH_HEAD_YAW, -35, 300 },
    { 1100, CH_HEAD_YAW,   0, 400 },
    { 0xFFFFFFFF, 0xFF, 0, 0 },
};

// === HAPPY: 점프 모션 + 머리 끄덕 ===
constexpr Keyframe POSE_HAPPY_FRAMES[] = {
    {    0, CH_LEG_L_SWING,  40, 200 },
    {    0, CH_LEG_R_SWING, -40, 200 },
    {    0, CH_HEAD_PITCH, -20, 200 },
    {  200, CH_LEG_L_SWING, -20, 200 },
    {  200, CH_LEG_R_SWING,  20, 200 },
    {  200, CH_HEAD_PITCH,  10, 200 },
    {  400, CH_LEG_L_SWING,   0, 300 },
    {  400, CH_LEG_R_SWING,   0, 300 },
    {  400, CH_HEAD_PITCH,   0, 300 },
    { 0xFFFFFFFF, 0xFF, 0, 0 },
};

// === SLEEP: 머리 떨굼 ===
constexpr Keyframe POSE_SLEEP_FRAMES[] = {
    { 0, CH_HEAD_PITCH, 35, 1500 },
    { 0xFFFFFFFF, 0xFF, 0, 0 },
};

constexpr Pose POSES[] = {
    { "idle",      POSE_IDLE_FRAMES },
    { "headache",  POSE_HEADACHE_FRAMES },
    { "shake",     POSE_SHAKE_FRAMES },
    { "happy",     POSE_HAPPY_FRAMES },
    { "sleep",     POSE_SLEEP_FRAMES },
};
constexpr size_t POSES_N = sizeof(POSES) / sizeof(POSES[0]);

const Keyframe* active_frames = nullptr;
const char* active_name = nullptr;
uint32_t active_start_ms = 0;
size_t next_kf_idx = 0;

}  // namespace

void poses_init() {
    active_frames = nullptr;
    next_kf_idx = 0;
}

bool poses_trigger(const char* name) {
    for (size_t i = 0; i < POSES_N; ++i) {
        if (strcmp(POSES[i].name, name) == 0) {
            active_frames = POSES[i].frames;
            active_name = POSES[i].name;
            active_start_ms = millis();
            next_kf_idx = 0;
            return true;
        }
    }
    return false;
}

void poses_abort() {
    active_frames = nullptr;
    active_name = nullptr;
}

void poses_tick() {
    if (!active_frames) return;
    uint32_t elapsed = millis() - active_start_ms;

    while (true) {
        const Keyframe& kf = active_frames[next_kf_idx];
        if (kf.channel == 0xFF) {
            // 시퀀스 종료 sentinel
            if (servo_all_idle()) {
                emit_event_done(active_name);
                active_frames = nullptr;
                active_name = nullptr;
            }
            return;
        }
        if (elapsed < kf.at_ms) return;  // 아직 이 키프레임 시각 아님
        servo_set_channel(kf.channel, kf.target_deg, kf.duration_ms);
        ++next_kf_idx;
    }
}

}  // namespace canduck
