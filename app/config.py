from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="forbid"  # unknown env variables allow nahi karega
    )

    OTP_SECRET: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_VERIFY_SERVICE_SID: str 

    # --- SMS OTP sender number (Twilio phone number) ---
    TWILIO_SMS_FROM: str  # ye Twilio ka purchased/trial phone number hoga jisse SMS OTP jayega

    # --- WhatsApp future use (delete nahi karna, agge kaam aayega) ---
    TWILIO_WHATSAPP_FROM: str | None = None  # optional rakha hai future WhatsApp production ke liye

    # --- Channel switch (sms default rakha) ---
    OTP_CHANNEL: str = "sms"  # sms = production free option, whatsapp future me enable kar sakte ho

    REDIS_URL: str = "redis://localhost:6379/0" 


settings = Settings()
