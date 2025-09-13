from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
import base64
from datetime import date
from . import database
from . import models
from . import schemas
from . import auth
from .verification import perform_kyc_checks, perform_kyb_checks, validate_phone_number, validate_iin, validate_business_registration_number, validate_tax_number

app = FastAPI(title="KYC/KYB API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)


@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def process_investor_verification(investor_id: int, db: Session):
    """Background task to process investor verification"""
    investor = db.query(models.Investor).filter(models.Investor.id == investor_id).first()
    if not investor:
        return
    
    try:

        investor_data = {
            'first_name': investor.first_name,
            'last_name': investor.last_name,
            'date_of_birth': investor.date_of_birth,
            'phone_number': investor.phone_number,
            'id_document_number': investor.id_document_number
        }

        verification_result = perform_kyc_checks(investor_data)
        

        if verification_result['government_verification']['status'] == 'verified':
            investor.verification_status = 'approved'
        else:
            investor.verification_status = 'rejected'
            investor.rejection_reason = "Failed government verification"
        
        db.commit()
        
    except Exception as e:

        investor.verification_status = 'rejected'
        investor.rejection_reason = f"Verification error: {str(e)}"
        db.commit()

def process_business_verification(business_id: int, db: Session):
    """Background task to process business verification"""
    business = db.query(models.Business).filter(models.Business.id == business_id).first()
    if not business:
        return
    
    try:

        business_data = {
            'company_name': business.company_name,
            'registration_number': business.registration_number,
            'tax_number': business.tax_number,
            'director_first_name': business.director_first_name,
            'director_last_name': business.director_last_name,
            'director_dob': business.director_dob
        }
        

        verification_result = perform_kyb_checks(business_data)
        

        if verification_result['government_verification']['status'] == 'verified':
            business.verification_status = 'approved'
        else:
            business.verification_status = 'rejected'
            business.rejection_reason = "Failed government verification"
        
        db.commit()
        
    except Exception as e:

        business.verification_status = 'rejected'
        business.rejection_reason = f"Verification error: {str(e)}"
        db.commit()


@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(f"Registering user: {user.email}")
    print(f"Original password: {user.password}")
    
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    print(f"Hashed password: {hashed_password}")
    
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        user_type=user.user_type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    print(f"User registered successfully with ID: {db_user.id}")
    return db_user

@app.post("/register/investor")
def register_investor(
    background_tasks: BackgroundTasks,
    user_id: int = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    date_of_birth: date = Form(...),
    phone_number: str = Form(...),
    id_document_type: str = Form(...),
    id_document_number: str = Form(...),
    address: str = Form(...),
    tax_number: Optional[str] = Form(None),
    id_document_front: UploadFile = File(...),
    id_document_back: UploadFile = File(...),
    selfie_with_id: UploadFile = File(...),
    db: Session = Depends(get_db)
):
 
    validate_phone_number(phone_number)
    
 
    if id_document_type == "id_card" and len(id_document_number) == 12:
        validate_iin(id_document_number)
    

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.user_type != "investor":
        raise HTTPException(status_code=400, detail="Invalid user or user type")
    

    existing_investor = db.query(models.Investor).filter(models.Investor.user_id == user_id).first()
    if existing_investor:
        raise HTTPException(status_code=400, detail="Investor profile already exists")

    id_front_data = base64.b64encode(id_document_front.file.read())
    id_back_data = base64.b64encode(id_document_back.file.read())
    selfie_data = base64.b64encode(selfie_with_id.file.read())
    

    investor = models.Investor(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        phone_number=phone_number,
        id_document_type=id_document_type,
        id_document_number=id_document_number,
        address=address,
        tax_number=tax_number,
        id_document_front=id_front_data,
        id_document_back=id_back_data,
        selfie_with_id=selfie_data
    )
    
    db.add(investor)
    db.commit()
    db.refresh(investor)
    

    background_tasks.add_task(process_investor_verification, investor.id, db)
    
    return {"message": "Investor registered successfully", "investor_id": investor.id}

@app.post("/register/business")
def register_business(
    background_tasks: BackgroundTasks,
    user_id: int = Form(...),
    company_name: str = Form(...),
    registration_number: str = Form(...),
    registration_date: date = Form(...),
    tax_number: str = Form(...),
    legal_address: str = Form(...),
    physical_address: str = Form(...),
    business_type: str = Form(...),
    industry: str = Form(...),
    director_first_name: str = Form(...),
    director_last_name: str = Form(...),
    director_dob: date = Form(...),
    director_id_number: str = Form(...),
    phone_number: str = Form(...),
    email: str = Form(...),
    ownership_structure: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    director_id_document: UploadFile = File(...),
    director_selfie: UploadFile = File(...),
    company_registration_certificate: UploadFile = File(...),
    tax_registration_certificate: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    validate_business_registration_number(registration_number)
    validate_tax_number(tax_number)
    validate_phone_number(phone_number)
    

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user or user.user_type != "business":
        raise HTTPException(status_code=400, detail="Invalid user or user type")
    

    existing_business = db.query(models.Business).filter(models.Business.user_id == user_id).first()
    if existing_business:
        raise HTTPException(status_code=400, detail="Business profile already exists")
    

    director_id_data = base64.b64encode(director_id_document.file.read())
    director_selfie_data = base64.b64encode(director_selfie.file.read())
    registration_cert_data = base64.b64encode(company_registration_certificate.file.read())
    tax_cert_data = base64.b64encode(tax_registration_certificate.file.read())
    
   
    business = models.Business(
        user_id=user_id,
        company_name=company_name,
        registration_number=registration_number,
        registration_date=registration_date,
        tax_number=tax_number,
        legal_address=legal_address,
        physical_address=physical_address,
        business_type=business_type,
        industry=industry,
        director_first_name=director_first_name,
        director_last_name=director_last_name,
        director_dob=director_dob,
        director_id_number=director_id_number,
        phone_number=phone_number,
        email=email,
        ownership_structure=ownership_structure,
        website=website,
        director_id_document=director_id_data,
        director_selfie=director_selfie_data,
        company_registration_certificate=registration_cert_data,
        tax_registration_certificate=tax_cert_data
    )
    
    db.add(business)
    db.commit()
    db.refresh(business)
    
   
    background_tasks.add_task(process_business_verification, business.id, db)
    
    return {"message": "Business registered successfully", "business_id": business.id}


@app.post("/login")
def login(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: schemas.UserResponse = Depends(auth.get_current_active_user)):
    return current_user

@app.get("/investor/{user_id}", response_model=schemas.InvestorResponse)
def get_investor(user_id: int, db: Session = Depends(get_db)):
    investor = db.query(models.Investor).filter(models.Investor.user_id == user_id).first()
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    return investor

@app.get("/business/{user_id}", response_model=schemas.BusinessResponse)
def get_business(user_id: int, db: Session = Depends(get_db)):
    business = db.query(models.Business).filter(models.Business.user_id == user_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
