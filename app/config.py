from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OTP_SECRET: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_NUMBER: str

    class Config:
        env_file = ".env"

settings = Settings()
