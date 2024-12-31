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
