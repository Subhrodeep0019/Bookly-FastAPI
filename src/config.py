from pydantic_settings import BaseSettings, SettingsConfigDict

# this is a config class
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_URL: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    DOMAIN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

setting = Settings()

broker_url = setting.REDIS_URL
result_backend = setting.REDIS_URL