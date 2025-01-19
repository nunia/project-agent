from sqlalchemy import Column, Integer, String, DateTime, Numeric, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

Base = declarative_base()

class ReservationStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    canceled = "canceled"

class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=func.newid())
    user_id = Column(Integer, nullable=False)
    restaurant_name = Column(String(255), nullable=False)
    reservation_time = Column(DateTime, nullable=False)
    number_of_people = Column(Integer, nullable=False)
    budget = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.pending)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
