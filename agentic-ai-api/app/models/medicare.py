from sqlalchemy import Column, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.sql import func
from app.core.database import Base
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from sqlalchemy.orm import relationship

# SQLAlchemy ORM Models
class Patient(Base):
    __tablename__ = "Patients"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=func.newid())  # Auto-generate ID
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    mobile_phone = Column(String, nullable=False)
    home_phone = Column(String, nullable=True)
    referral_info = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship to Appointment
    appointments = relationship("Appointment", back_populates="patient")

class PatientBase(BaseModel):
    name: str
    email: Optional[str] = None
    mobile_phone: str
    home_phone: Optional[str] = None
    referral_info: Optional[str] = None

class PatientCreateRequest(PatientBase):
    pass

class PatientResponse(BaseModel):
    id: str  # Keep it as a string in the API response
    name: str
    email: Optional[str] = None
    mobile_phone: str
    home_phone: Optional[str] = None
    referral_info: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes=True

    # Validator to convert UUID to string
    @validator("id", pre=True)
    def convert_uuid_to_string(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v

class Appointment(Base):
    __tablename__ = "Appointments"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=func.newid())  # Auto-generate ID
    patient_id = Column(UNIQUEIDENTIFIER, ForeignKey("Patients.id"), nullable=False)  # Foreign key to Patient
    type = Column(String(50), nullable=False)  # Type of appointment
    status = Column(String(20), nullable=False)  # Status of the appointment
    scheduled_date = Column(Date, nullable=True)  # Date of the appointment
    insurance_required = Column(Boolean, nullable=True)  # Whether insurance is required
    created_at = Column(DateTime, server_default=func.now())  # Timestamp of creation
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  # Timestamp of update

    # Relationship to Patient (optional)
    patient = relationship("Patient", back_populates="appointments")

class AppointmentBase(BaseModel):
    patient_id: UUID
    type: str
    status: str
    scheduled_date: Optional[date] = None
    insurance_required: Optional[bool] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes=True

        @validator("id", "patient_id", pre=True)
        def convert_uuid_to_string(cls, v):
            if isinstance(v, UUID):
                return str(v)
            return v
