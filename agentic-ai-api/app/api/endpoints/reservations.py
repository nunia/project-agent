from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.reservations import create_reservation, get_reservation, get_reservations, update_reservation, delete_reservation
from app.schemas.reservations import ReservationCreate, ReservationResponse
from app.core.database import get_db 
from uuid import UUID

router = APIRouter()

@router.post("/reservations/", response_model=ReservationResponse)
def create_new_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    return create_reservation(db=db, reservation=reservation)

@router.get("/reservations/{reservation_id}", response_model=ReservationResponse)
def read_reservation(reservation_id: UUID, db: Session = Depends(get_db)):
    reservation = get_reservation(db=db, reservation_id=reservation_id)
    
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    return reservation

@router.get("/reservations/", response_model=list[ReservationResponse])
def read_all_reservations(db: Session = Depends(get_db)):
    return get_reservations(db=db)

@router.put("/reservations/{reservation_id}", response_model=ReservationResponse)
def update_existing_reservation(reservation_id: UUID, reservation_data: ReservationCreate, db: Session = Depends(get_db)):
    updated_reservation = update_reservation(db=db, reservation_id=reservation_id, reservation_data=reservation_data)
    
    if updated_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    return updated_reservation

@router.delete("/reservations/{reservation_id}")
def delete_existing_reservation(reservation_id: UUID, db: Session = Depends(get_db)):
    success = delete_reservation(db=db, reservation_id=reservation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    return {"detail": "Reservation deleted successfully"}
