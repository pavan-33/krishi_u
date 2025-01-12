from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, VARCHAR
import json
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
    crops = relationship("Crop", back_populates="farmer")

class FarmerDetails(Base):
    __tablename__ = "farmer_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    acres = Column(Integer)
    previous_experience = Column(String)

    user = relationship("User", back_populates="farmer_details")


class LandlordDetails(Base):
    __tablename__ = "landlord_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    land_type = Column(String)
    acres = Column(Integer)
    location = Column(String)
    images_list = Column(JSONEncodedList)  # Store as JSON encoded string

    user = relationship("User", back_populates="landlord_details")


class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmer_details.id"))
    landlord_id = Column(Integer, ForeignKey("landlord_details.id"))
    admin_id = Column(Integer, ForeignKey("users.id"))
    
    farmer = relationship("FarmerDetails")
    landlord = relationship("LandlordDetails")
    user = relationship("User", back_populates="spaces")
    crops = relationship("Crop", back_populates="space")



class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String, index=True)
    duration = Column(Integer)  # Duration in months
    images = Column(JSONEncodedList)  # Store as JSON encoded string
    farmer_id = Column(Integer, ForeignKey("users.id"))  # Referring to the farmer
    space_id = Column(Integer, ForeignKey('spaces.id'))


    # Relationships
    farmer = relationship("User", back_populates="crops")
    space = relationship("Space", back_populates="crops")

def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
