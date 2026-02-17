from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OTP_SECRET: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_NUMBER: str
    REDIS_URL: str = "redis://localhost:6379/0" 

    class Config:
        env_file = ".env"

settings = Settings()
