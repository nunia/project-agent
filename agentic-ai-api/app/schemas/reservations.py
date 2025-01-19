from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class ReservationBase(BaseModel):
    user_id: int
    restaurant_name: str
    reservation_time: datetime
    number_of_people: int
    budget: float
    status: Optional[str] = 'pending'  # Default status

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(ReservationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes=True
        orm_mode = True  # Allow reading data as ORM objects
