from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
from typing import Optional
from datetime import date

    # used at /register 
class UserRegister(BaseModel):
    tc: int = Field(..., gt=10**10, lt=10**11, description="Turkish Citizen ID must be an 11-digit number.")
    birth_date: date
    password: str
    name: str
    surname: str
    email: EmailStr
    blood_type: Optional[str]

class BannedUser(BaseModel):
    tc_id: int = Field(..., gt=10**10, lt=10**11, description="Turkish Citizen ID must be an 11-digit number.")
    date: date
    cause: Optional[str]
    unban_date: Optional[date]
    

from datetime import datetime


class Request(BaseModel):
    request_id: Optional[int] = None
    requested_tc_id: int = Field(..., gt=10**10, lt=10**11, description="Turkish Citizen ID must be an 11-digit number.")
    patient_tc_id: Optional[int] = Field(None, gt=10**10, lt=10**11)
    blood_type: Optional[str]
    age: Optional[int] = Field(None, ge=0, description="Age must be a non-negative integer.")
    gender: Optional[str]
    note: Optional[str]
    location: Optional[str]
    coordinates: Optional[str]
    status: Optional[str]
    create_time: Optional[datetime] = Field(default_factory=datetime.utcnow)


class OnTheWay(BaseModel):
    id: Optional[int] = None
    request_id: int
    donor_tc_id: int = Field(..., gt=10**10, lt=10**11, description="Turkish Citizen ID must be an 11-digit number.")
    status: Optional[str]
    create_time: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Notification(BaseModel):
    id: Optional[int] = None
    request_id: int
    notification_type: Optional[str]
    message: Optional[str]

class Location(BaseModel):
    city_name: str = Field(..., max_length=50, description="City name cannot exceed 50 characters.")
    district_name: str = Field(..., max_length=50, description="District name cannot exceed 50 characters.")
