import requests
from fastapi import HTTPException, status
import re
from datetime import datetime, date

def validate_phone_number(phone_number: str):
    """Validate Kazakhstan phone number format"""
    pattern = r'^\+7\d{10}$|^8\d{10}$'
    if not re.match(pattern, phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must be in format +7XXXXXXXXXX or 8XXXXXXXXXX"
        )
    return True

def validate_iin(iin: str):
    """Validate Kazakhstan IIN (Individual Identification Number)"""
    if not iin.isdigit() or len(iin) != 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IIN must be 12 digits"
        )
    

    century_char = iin[6]
    year = int(iin[0:2])
    month = int(iin[2:4])
    day = int(iin[4:6])
    
    if century_char in ['1', '2']:
        full_year = 1800 + year
    elif century_char in ['3', '4']:
        full_year = 1900 + year
    else:
        full_year = 2000 + year
    
    try:
        birth_date = date(full_year, month, day)
        if birth_date > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid birth date in IIN"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid birth date in IIN"
        )
    
    return True

def validate_business_registration_number(reg_number: str):
    """Validate business registration number format"""
    if not reg_number.replace('-', '').isdigit() or len(reg_number.replace('-', '')) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid business registration number format"
        )
    return True

def validate_tax_number(tax_number: str):
    """Validate tax identification number"""
    if not tax_number.isdigit() or len(tax_number) != 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tax number must be 12 digits"
        )
    return True


def verify_identity_with_government_db(iin: str, full_name: str, dob: date):
    """Stub function for integration with government identity verification"""
   
    print(f"Verifying identity with government DB: IIN={iin}, Name={full_name}, DOB={dob}")
    return {"status": "verified", "confidence": "high"}

def verify_business_with_government_db(reg_number: str, company_name: str):
    """Stub function for integration with government business verification"""
  
    print(f"Verifying business with government DB: RegNumber={reg_number}, Name={company_name}")
    return {"status": "verified", "confidence": "high"}

def check_sanctions_list(full_name: str, dob: date):
    """Stub function for checking against sanctions lists"""
   
    print(f"Checking sanctions list: Name={full_name}, DOB={dob}")
    return {"sanctioned": False}

def perform_kyc_checks(investor_data: dict):
    """Perform all KYC checks for an investor"""
    
    validate_phone_number(investor_data.get('phone_number', ''))
    
  
    full_name = f"{investor_data.get('first_name', '')} {investor_data.get('last_name', '')}"
    gov_result = verify_identity_with_government_db(
        investor_data.get('id_document_number', ''),
        full_name,
        investor_data.get('date_of_birth')
    )
    
    # Check sanctions list
    sanctions_result = check_sanctions_list(
        full_name,
        investor_data.get('date_of_birth')
    )
    
    if sanctions_result.get('sanctioned', False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot complete registration due to sanctions list match"
        )
    
    return {
        "government_verification": gov_result,
        "sanctions_check": sanctions_result
    }

def perform_kyb_checks(business_data: dict):
    """Perform all KYB checks for a business"""

    validate_business_registration_number(business_data.get('registration_number', ''))
    validate_tax_number(business_data.get('tax_number', ''))
    
    
    gov_result = verify_business_with_government_db(
        business_data.get('registration_number', ''),
        business_data.get('company_name', '')
    )
    

    director_name = f"{business_data.get('director_first_name', '')} {business_data.get('director_last_name', '')}"
    sanctions_result = check_sanctions_list(
        director_name,
        business_data.get('director_dob')
    )
    
    if sanctions_result.get('sanctioned', False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot complete registration due to sanctions list match for director"
        )
    
    return {
        "government_verification": gov_result,
        "sanctions_check": sanctions_result
    }
