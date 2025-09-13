from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    
    investor = relationship("Investor", back_populates="user", uselist=False, cascade="all, delete")
    business = relationship("Business", back_populates="user", uselist=False, cascade="all, delete")

class Investor(Base):
    __tablename__ = "investors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    phone_number = Column(String, nullable=False)
    id_document_type = Column(String, nullable=False)  
    id_document_number = Column(String, nullable=False)
    id_document_front = Column(LargeBinary)  
    id_document_back = Column(LargeBinary)  
    selfie_with_id = Column(LargeBinary)  
    address = Column(Text, nullable=False)
    tax_number = Column(String)
    risk_level = Column(String, default="medium")
    verification_status = Column(String, default="pending")  
    rejection_reason = Column(Text)
    
    user = relationship("User", back_populates="investor")

class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String, nullable=False)
    registration_number = Column(String, nullable=False)
    registration_date = Column(Date, nullable=False)
    tax_number = Column(String, nullable=False)
    legal_address = Column(Text, nullable=False)
    physical_address = Column(Text, nullable=False)
    business_type = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    director_first_name = Column(String, nullable=False)
    director_last_name = Column(String, nullable=False)
    director_dob = Column(Date, nullable=False)
    director_id_number = Column(String, nullable=False)
    director_id_document = Column(LargeBinary)  
    director_selfie = Column(LargeBinary)  
    company_registration_certificate = Column(LargeBinary) 
    tax_registration_certificate = Column(LargeBinary)  
    ownership_structure = Column(Text) 
    website = Column(String)
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=False)
    verification_status = Column(String, default="pending") 
    rejection_reason = Column(Text)
    
    user = relationship("User", back_populates="business")
