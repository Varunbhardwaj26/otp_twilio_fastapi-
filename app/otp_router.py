from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.redis_client import r
from app.config import settings
from app.otp_utils import generate_otp_4, hash_otp, verify_otp, OTP_TTL_SECONDS
from app.twilio_service import send_otp_sms

router = APIRouter(prefix="/otp", tags=["OTP"])


class OTPStartReq(BaseModel):
    phone: str = Field(..., examples=["+919876543210"])


class OTPStartRes(BaseModel):
    message: str
    expires_in: int


@router.post("/start", response_model=OTPStartRes)
def start_otp(payload: OTPStartReq):
    phone = payload.phone.strip().replace(" ", "")

    otp = generate_otp_4()
    otp_h = hash_otp(otp, settings.OTP_SECRET)

    otp_hash_key = f"otp:{phone}:hash"
    attempts_key = f"otp:{phone}:attempts"

    r.setex(otp_hash_key, OTP_TTL_SECONDS, otp_h)
    r.setex(attempts_key, OTP_TTL_SECONDS, 0)

    try:
        sid = send_otp_sms(
            account_sid=settings.TWILIO_ACCOUNT_SID,
            auth_token=settings.TWILIO_AUTH_TOKEN,
            from_number=settings.TWILIO_SMS_FROM,
            to_number=phone,
            otp=otp,
        )
        print("SMS SID:", sid)

    except Exception as e:
        r.delete(otp_hash_key, attempts_key)

        try:
            print("TWILIO STATUS:", getattr(e, "status", None))
            print("TWILIO CODE:", getattr(e, "code", None))
            print("TWILIO MSG:", getattr(e, "msg", None))
            print("TWILIO MORE:", getattr(e, "more_info", None))
            print("TWILIO URI:", getattr(e, "uri", None))
            print("TWILIO DETAILS:", getattr(e, "details", None))
        except Exception:
            pass

        raise HTTPException(status_code=502, detail=f"Twilio send failed: {str(e)}")

    return OTPStartRes(message="OTP sent", expires_in=OTP_TTL_SECONDS)


class OTPVerifyReq(BaseModel):
    phone: str = Field(..., examples=["+919876543210"])
    otp: str = Field(..., min_length=4, max_length=4, examples=["1234"])


class OTPVerifyRes(BaseModel):
    message: str


@router.post("/verify", response_model=OTPVerifyRes)
def verify_otp_endpoint(payload: OTPVerifyReq):
    phone = payload.phone.strip().replace(" ", "")

    otp_hash_key = f"otp:{phone}:hash"
    attempts_key = f"otp:{phone}:attempts"

    otp_hash = r.get(otp_hash_key)
    if not otp_hash:
        raise HTTPException(status_code=404, detail="OTP not found. Please start again.")

    attempts = int(r.get(attempts_key) or 0)
    if attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many attempts. Please resend OTP.")

    if not verify_otp(payload.otp, otp_hash, settings.OTP_SECRET):
        attempts += 1

        ttl = r.ttl(otp_hash_key)
        if ttl is None or ttl < 0:
            ttl = OTP_TTL_SECONDS

        r.setex(attempts_key, ttl, attempts)
        raise HTTPException(status_code=400, detail="Invalid OTP")

    r.delete(otp_hash_key, attempts_key)
    return OTPVerifyRes(message="OTP verified")
