# SQLAlchemy Core and ORM
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, Text
from sqlalchemy.orm import sessionmaker, relationship, Session

# Declarative Base
from sqlalchemy.ext.declarative import declarative_base

# Custom TypeDecorator
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.ext.mutable import Mutable  # For potential mutability of JSON fields

# Utility Libraries
import json  # For serialization and deserialization of JSON data

# PostgreSQL-Specific Imports (if PostgreSQL is used)
from sqlalchemy.dialects.postgresql import JSON  # If using PostgreSQL for native JSON support
from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import Text  # Add this import

# Database setup
DATABASE_URL = "sqlite:///./app.db"  # SQLite database

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



# Custom type decorator for JSON list storage in SQLite
class JSONEncodedList(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)  # Serialize list to JSON string
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)  # Deserialize JSON string to Python list
        return value


# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # Roles: 'admin', 'farmer', 'landlord'

    farmer_details = relationship("FarmerDetails", back_populates="user", uselist=False)
    landlord_details = relationship("LandlordDetails", back_populates="user", uselist=False)
    spaces = relationship("Space", back_populates="user")


class FarmerDetails(Base):
    __tablename__ = "farmer_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    phone_number = Column(String, nullable=True)  # farmer's contact number
    land_handling_capacity = Column(Integer)
    preferred_locations = Column(JSONEncodedList, default=[])

    user = relationship("User", back_populates="farmer_details")


class LandlordDetails(Base):
    __tablename__ = "landlord_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    phone_number = Column(String, nullable=True)  # Landlord's contact number
    soil_type = Column(String)
    acres = Column(Integer)
    location = Column(String)
    images_list = Column(JSONEncodedList)  # Store as JSON encoded string

    user = relationship("User", back_populates="landlord_details")


class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmer_details.id"), nullable=False)
    landlord_id = Column(Integer, ForeignKey("landlord_details.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=True)  # Optional description of the collaboration

    # Relationships
    farmer = relationship("FarmerDetails")
    landlord = relationship("LandlordDetails")
    user = relationship("User", back_populates="spaces")
    crops = relationship("Crop", back_populates="space", cascade="all, delete")  # Associated crops

    # Tracking progress
    progress = Column(JSON, default={})




class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    steps = Column(JSON, nullable=True)  # Use JSON for structured steps data

    space_id = Column(Integer, ForeignKey("spaces.id"))
    space = relationship("Space", back_populates="crops")

    # Define relationship with Proof
    proofs = relationship("Proof", back_populates="crop", cascade="all, delete")


class Proof(Base):
    __tablename__ = "proofs"

    id = Column(Integer, primary_key=True, index=True)
    file_url = Column(String, nullable=False)  # URL of the uploaded file
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)  # Reference to Crop
    step_index = Column(Integer, nullable=False)  # Index of the step in the JSON list

    crop = relationship("Crop", back_populates="proofs")  # Relationship with Crop





def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
