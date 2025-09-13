from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date, datetime
import re

class UserBase(BaseModel):
    email: EmailStr
    user_type: str

    @validator('user_type')
    def validate_user_type(cls, v):
        if v not in ["investor", "business"]:
            raise ValueError('User type must be either "investor" or "business"')
        return v

class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class InvestorBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    phone_number: str
    id_document_type: str
    id_document_number: str
    address: str
    tax_number: Optional[str] = None

    @validator('phone_number')
    def validate_phone_number(cls, v):
        pattern = r'^\+7\d{10}$|^8\d{10}$'
        if not re.match(pattern, v):
            raise ValueError('Phone number must be in format +7XXXXXXXXXX or 8XXXXXXXXXX')
        return v

class InvestorCreate(InvestorBase):
    pass

class InvestorResponse(InvestorBase):
    id: int
    user_id: int
    verification_status: str
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True

class BusinessBase(BaseModel):
    company_name: str
    registration_number: str
    registration_date: date
    tax_number: str
    legal_address: str
    physical_address: str
    business_type: str
    industry: str
    director_first_name: str
    director_last_name: str
    director_dob: date
    director_id_number: str
    ownership_structure: Optional[str] = None
    website: Optional[str] = None
    phone_number: str
    email: EmailStr

class BusinessCreate(BusinessBase):
    pass

class BusinessResponse(BusinessBase):
    id: int
    user_id: int
    verification_status: str
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
