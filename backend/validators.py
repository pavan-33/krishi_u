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


def validate_farmer_details(land_handling_capacity: int) -> bool:
    """
    Validate farmer registration details.
    
    Args:
        land_handling_capacity (int): Land area the farmer can manage.

    Returns:
        bool: True if valid, raises ValueError otherwise.
    """
    if land_handling_capacity < 1:
        raise ValueError("Land handling capacity must be a positive number.")
    return True



def validate_landlord_details(soil_type: str, acres: int, location: str, images: List[str]) -> bool:
    """
    Validate landlord registration details.
    
    Args:
        land_type (str): Type of land.
        acres (int): Size of the land in acres.
        location (str): Location of the land.
        images (List[str]): List of image URLs.

    Returns:
        bool: True if valid, raises ValueError otherwise.
    """
    if acres < 1:
        raise ValueError("Acres must be a positive number.")
    if not soil_type or len(soil_type.strip()) < 3:
        raise ValueError("Land type must be at least 3 characters long.")
    if not location or len(location.strip()) < 3:
        raise ValueError("Location must be at least 3 characters long.")
    if images and not all(isinstance(image, str) and image.strip() for image in images):
        raise ValueError("All images must be valid non-empty strings.")
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

from typing import List, Optional
from pydantic import BaseModel, Field

class FarmerDetailsRequest(BaseModel):
    user_id: Optional[int] = None
    phone_number: Optional[str] = Field(
        None, pattern=r"^\+?\d{10,15}$", description="Phone number in international format (optional)."
    )
    land_handling_capacity: int = Field(
        ..., gt=0, description="Land area the farmer can handle in acres."
    )
    preferred_locations: Optional[List[str]] = Field(
        default=[], description="List of preferred locations for farming."
    )


from pydantic import BaseModel, Field
from typing import List, Optional

class LandlordDetailsRequest(BaseModel):
    user_id: Optional[int] = None
    phone_number: Optional[str] = Field(
    None, pattern=r"^\+?\d{10,15}$", description="Phone number in international format (optional)."
    )

    soil_type: str = Field(..., min_length=3, description="Type of land (e.g., agricultural, residential).")
    acres: int = Field(..., gt=0, description="Size of the land in acres (must be greater than 0).")
    location: str = Field(..., min_length=3, description="Location of the land.")
    images: List[str] = Field(default=[], description="List of image URLs for the land.")


class FarmerLandlordConnectRequest(BaseModel):
    farmer_id: int
    landlord_id: int

class CropCreate(BaseModel):
    crop_name: str
    duration: int
    images: List[str]  # List of image URLs