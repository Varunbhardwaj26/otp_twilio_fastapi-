from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base  

class JobApplication(Base):
    __tablename__ = "job_applications"
    __table_args__ = (UniqueConstraint("job_id", "phone", name="uq_job_phone"),)

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)

    # rresume_key = Column(String(500), nullable=True)
    # resume_filename = Column(String(255), nullable=True)
    # resume_mime = Column(String(100), nullable=True)
    # resume_size = Column(Integer, nullable=True)
    resume_url = Column(String(2000), nullable=True)
    status = Column(String(30), nullable=False, default="PENDING_OTP")

    created_at = Column(DateTime, default=datetime.utcnow)

class ApplicationOTP(Base):
    __tablename__ = "application_otps"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)

    otp_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
