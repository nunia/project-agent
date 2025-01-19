from sqlalchemy.orm import Session
from app.models.reservations import Reservation
from app.schemas.reservations import ReservationCreate, ReservationResponse
from uuid import UUID

def create_reservation(db: Session, reservation: ReservationCreate) -> ReservationResponse:
    db_reservation = Reservation(**reservation.dict())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return ReservationResponse.from_orm(db_reservation)

def get_reservation(db: Session, reservation_id: UUID) -> ReservationResponse:
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()

def get_reservations(db: Session):
    return db.query(Reservation).all()

def update_reservation(db: Session, reservation_id: UUID, reservation_data: ReservationCreate) -> ReservationResponse:
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    
    if db_reservation:
        for key, value in reservation_data.dict(exclude_unset=True).items():
            setattr(db_reservation, key, value)
        db.commit()
        db.refresh(db_reservation)
        return ReservationResponse.from_orm(db_reservation)
    
    return None

def delete_reservation(db: Session, reservation_id: UUID):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    
    if db_reservation:
        db.delete(db_reservation)
        db.commit()
        return True
    
    return False
