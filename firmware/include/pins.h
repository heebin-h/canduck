#pragma once

// ESP32-S3 GPIO 매핑 (Board B HAT 기준)
// 변경 시 schematic-spec.md와 동기화 필수.

#define PIN_UART_TX        43  // → RPi RX (GPIO15)
#define PIN_UART_RX        44  // ← RPi TX (GPIO14)

#define PIN_I2C_SDA         5  // PCA9685, INA219(전송 시 RPi 측이 마스터)
#define PIN_I2C_SCL         6

#define PIN_PCA9685_OE      4  // active low (LOW = 출력 enable)

#define PIN_MOTOR_AIN1      7
#define PIN_MOTOR_AIN2      8
#define PIN_MOTOR_PWMA      9
#define PIN_MOTOR_BIN1     10
#define PIN_MOTOR_BIN2     11
#define PIN_MOTOR_PWMB     12

#define PIN_VBAT_SENSE      1  // ADC1_CH0, 분압 후 입력 (20K/10K)

// PCA9685 채널 할당 (0~15)
#define CH_HEAD_YAW         0
#define CH_HEAD_PITCH       1
#define CH_ARM_L_SHOULDER   2
#define CH_ARM_L_ELBOW      3
#define CH_ARM_R_SHOULDER   4
#define CH_ARM_R_ELBOW      5
#define CH_LEG_L_SWING      6
#define CH_LEG_R_SWING      7
// CH 8~15: 예비
