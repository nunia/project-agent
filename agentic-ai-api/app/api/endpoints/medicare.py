from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.medicare import (
    PatientResponse,
    PatientCreateRequest,
    Patient,
    AppointmentResponse,
    AppointmentCreate,
    Appointment
)

router = APIRouter()

# Patients CRUD Endpoints

# Get a specific patient by ID
@router.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

# Get all patients
@router.get("/patients", response_model=List[PatientResponse])
def get_all_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return patients

# Create a new patient
@router.post("/patients", response_model=PatientResponse)
def create_patient_endpoint(patient_data: PatientCreateRequest, db: Session = Depends(get_db)):
    new_patient = Patient(
        name=patient_data.name,
        email=patient_data.email,
        mobile_phone=patient_data.mobile_phone,
        home_phone=patient_data.home_phone,
        referral_info=patient_data.referral_info
    )
    db.add(new_patient)
    db.commit()  # Save to the database
    db.refresh(new_patient)  # Get the patient object with the generated id and timestamps
    return new_patient

# Update an existing patient
@router.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(patient_id: str, patient: PatientCreateRequest, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    for key, value in patient.dict().items():
        setattr(db_patient, key, value)
    
    db.commit()
    return db_patient

# Delete a patient
@router.delete("/patients/{patient_id}", response_model=PatientResponse)
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db.delete(db_patient)
    db.commit()
    return db_patient

# Appointments CRUD Endpoints

@router.get("/appointments", response_model=List[AppointmentResponse])
def get_appointments(
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    type: Optional[str] = Query(None, description="Filter by type"),
    scheduled_date: Optional[date] = Query(None, description="Filter by scheduled date"),
    skip: int = Query(0, description="Number of records to skip for pagination"),
    limit: int = Query(10, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    query = db.query(Appointment)

    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    if type:
        query = query.filter(Appointment.type == type)
    
    if scheduled_date:
        query = query.filter(Appointment.scheduled_date == scheduled_date)

    appointments = query.order_by(Appointment.created_at).offset(skip).limit(limit).all()
    
    return appointments

# Create a new appointment
@router.post("/appointments", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# Update an existing appointment
@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(appointment_id: str, appointment: AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    for key, value in appointment.dict().items():
        setattr(db_appointment, key, value)

    db.commit()
    
    return db_appointment

# Delete an appointment
@router.delete("/appointments/{appointment_id}", response_model=AppointmentResponse)
def delete_appointment(appointment_id: str, db: Session = Depends(get_db)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    db.delete(db_appointment)
    db.commit()
    
    return db_appointment
