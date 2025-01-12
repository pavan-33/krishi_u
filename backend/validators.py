from db import User, FarmerDetails, LandlordDetails
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

def validate_user_registration(db: Session, email: str) -> bool:
    """Check if the email is already registered."""
    return db.query(User).filter(User.email == email).first() is not None

def validate_user_login(db: Session, email: str, password: str) -> bool:
    """Check if the user exists and password matches."""
    user = db.query(User).filter(User.email == email).first()
    return user and user.password == password


def validate_farmer_details(acres: int, previous_experience: str) -> bool:
    """Validate farmer registration details."""
    if acres < 1:
        raise ValueError("Acres must be a positive number.")
    return True


def validate_landlord_details(land_type: str, acres: int, location: str) -> bool:
    """Validate landlord registration details."""
    if acres < 1:
        raise ValueError("Acres must be a positive number.")
    if not land_type or not location:
        raise ValueError("Land type and location cannot be empty.")
    return True


def is_admin(db: Session, email: str) -> bool:
    """Check if the user is an admin."""
    user = db.query(User).filter(User.email == email).first()
    return user and user.role == "admin"

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email:str
    password: str
    role: str

class FarmerDetailsRequest(BaseModel):
    user_id: Optional[int] = None
    acres: int
    previous_experience: str

class LandlordDetailsRequest(BaseModel):
    user_id: Optional[int] = None
    land_type: str
    acres: int
    location: str
    images: List[str]  # List of image URLs


class FarmerLandlordConnectRequest(BaseModel):
    farmer_id: int
    landlord_id: int

class CropCreate(BaseModel):
    crop_name: str
    duration: int
    images: List[str]  # List of image URLs