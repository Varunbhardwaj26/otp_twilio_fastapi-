from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.redis_client import r
from app.config import settings
from app.otp_utils import generate_otp_4, hash_otp, verify_otp, OTP_TTL_SECONDS
# from app.twilio_service import send_otp_sms
from app.twilio_service import send_otp_whatsapp

router = APIRouter(prefix="/otp", tags=["OTP"])

# Redis store
# phone -> otp_hash (TTL 5 min)
# phone -> attempts (TTL 5 min)


class OTPStartReq(BaseModel):
    phone: str = Field(..., examples=["+919876543210"])


class OTPStartRes(BaseModel):
    message: str
    expires_in: int


@router.post("/start", response_model=OTPStartRes)
def start_otp(payload: OTPStartReq):
    phone = payload.phone.strip().replace(" ", "")

    # 1) generate otp
    otp = generate_otp_4()

    # 2) hash otp (never store plain otp)
    otp_h = hash_otp(otp, settings.OTP_SECRET)

    # 3) save in redis (TTL auto)
    otp_hash_key = f"otp:{phone}:hash"
    attempts_key = f"otp:{phone}:attempts"

    r.setex(otp_hash_key, OTP_TTL_SECONDS, otp_h)
    r.setex(attempts_key, OTP_TTL_SECONDS, 0)

    # 4) send via twilio
    try:
        # send_otp_sms(
        #     account_sid=settings.TWILIO_ACCOUNT_SID,
        #     auth_token=settings.TWILIO_AUTH_TOKEN,
        #     from_number=settings.TWILIO_FROM_NUMBER,
        #     to_number=phone,
        #     otp=otp,
        # )

        sid = send_otp_whatsapp(
            account_sid=settings.TWILIO_ACCOUNT_SID,
            auth_token=settings.TWILIO_AUTH_TOKEN,
            to_number=phone,
            otp=otp,
        )
        print("WHATSAPP SID:", sid)

    except Exception as e:
        # Twilio fail ho to store clean kar diya (otherwise wrong OTP pending rahega)
        r.delete(otp_hash_key, attempts_key)

        # Optional debug prints (TwilioRestException usually has these attributes)
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

    # attempts limit
    attempts = int(r.get(attempts_key) or 0)
    if attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many attempts. Please resend OTP.")

    # verify
    if not verify_otp(payload.otp, otp_hash, settings.OTP_SECRET):
        attempts += 1

        # attempts TTL ko otp hash TTL ke saath align rakho
        ttl = r.ttl(otp_hash_key)
        if ttl is None or ttl < 0:
            ttl = OTP_TTL_SECONDS

        r.setex(attempts_key, ttl, attempts)
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # success -> cleanup
    r.delete(otp_hash_key, attempts_key)
    return OTPVerifyRes(message="OTP verified")


@router.get("/wa-ping")
def wa_ping():
    try:
        sid = send_otp_whatsapp(
            account_sid=settings.TWILIO_ACCOUNT_SID,
            auth_token=settings.TWILIO_AUTH_TOKEN,
            to_number="+918770486237",
            otp="9999",
        )
        return {"sid": sid}
    except Exception as e:
        return {
            "error": str(e),
            "status": getattr(e, "status", None),
            "code": getattr(e, "code", None),
            "msg": getattr(e, "msg", None),
            "uri": getattr(e, "uri", None),
            "details": getattr(e, "details", None),
        }


#  Line-by-line: kya ho raha hai?
# Redis keys:
# otp:{phone}:hash      -> OTP ka HMAC hash (TTL 5 min)
# otp:{phone}:attempts  -> attempts counter (TTL same as OTP)
#
# /otp/start
# phone input leta ha
# otp generate karta
# otp hash karta
# Redis me TTL ke saath store karta
# Twilio WhatsApp bhejtahai 