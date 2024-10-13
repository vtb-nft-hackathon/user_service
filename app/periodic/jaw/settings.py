from pydantic_settings import BaseSettings


class JawCronSettings(BaseSettings):
    schedule: str = "*/1 * * * *"

    class Config:
        env_prefix = "JAW_CRON_"
