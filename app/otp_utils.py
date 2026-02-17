import random
import hmac
import hashlib
import time

OTP_TTL_SECONDS = 300  # 5 min

def generate_otp_4() -> str:
    # 0000 to 9999, always 4 digits
    return f"{random.randint(0, 9999):04d}"

def hash_otp(otp: str, secret: str) -> str:
    # OTP ko direct store nahi karte; HMAC hash store karte hain
    return hmac.new(secret.encode(), otp.encode(), hashlib.sha256).hexdigest()

def verify_otp(otp: str, otp_hash: str, secret: str) -> bool:
    # timing attack safe compare
    return hmac.compare_digest(hash_otp(otp, secret), otp_hash)

def now_ts() -> int:
    return int(time.time())
