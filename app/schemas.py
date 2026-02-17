from pydantic import BaseModel, EmailStr
from typing import Optional

class ApplicationStart(BaseModel):
    job_id: int
    name: str
    email: EmailStr
    phone: str
    resume_url: str

class ApplicationStartResponse(BaseModel):
    application_id: int
    status: str
    message: str

class ApplicationVerifyOtp(BaseModel):
    application_id: int
    phone: str
    otp: str

class ApplicationVerifyResponse(BaseModel):
    application_id: int
    status: str
    message: str
