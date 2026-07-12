"""환경변수/설정 파일에서 런타임 설정 로드.

systemd unit의 EnvironmentFile 또는 /etc/canduck/canduck.env 에서 읽음.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CANDUCK_",
        env_file="/etc/canduck/canduck.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # UART
    uart_device: str = "/dev/ttyAMA0"
    uart_baud: int = 115200

    # MQTT
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_keepalive: int = 60
    mqtt_client_id: str = "canduck-daemon"

    # LCD
    lcd_spi_bus: int = 0
    lcd_spi_dev: int = 0
    lcd_gpio_dc: int = 27
    lcd_gpio_rst: int = 17
    lcd_gpio_bl: int = 22
    lcd_width: int = 240
    lcd_height: int = 240

    # Telemetry
    telemetry_poll_hz: float = 1.0
    vbat_warn_mv: int = 7000
    vbat_critical_mv: int = 6600

    # Behavior
    idle_to_sleepy_sec: int = 600
    sleepy_to_sleep_sec: int = 60
    headache_cooldown_sec: int = 10

    # Voice
    enable_voice: bool = False
    porcupine_access_key: str = Field(default="", repr=False)
    wake_word_path: str = ""

    # Logging
    log_level: str = "INFO"


settings = Settings()
