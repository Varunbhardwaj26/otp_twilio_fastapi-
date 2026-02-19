from fastapi import FastAPI
from app.otp_router import router as otp_router


app = FastAPI(title="OTP Twilio API")

app.include_router(otp_router)


@app.get("/")
def root():
    return {"status": "ok"}
