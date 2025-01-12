from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from db import SessionLocal, init_db, User, FarmerDetails, LandlordDetails, Space, Crop
from validators import * #validate_user_registration, validate_farmer_details, validate_landlord_details, is_admin, validate_user_login, FarmerDetailsRequest
from security import create_access_token, create_refresh_token, verify_token, validate_token_from_header
from typing import List
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uuid
# Mount the 'media' directory to serve static files (images)

app = FastAPI()

# Path where the media files will be stored
MEDIA_DIR = Path(__file__).parent / "media"

# Ensure the media directory exists
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize the database
@app.on_event("startup")
def on_startup():
    init_db()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Route for user registration
@app.post("/register")
def register_user(user_details : RegisterRequest, db: Session = Depends(get_db)):
    if validate_user_registration(db, user_details.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    if user_details.role not in ["admin", "farmer", "landlord"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    new_user = User(email=user_details.email, password=user_details.password, role=user_details.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email, "role": new_user.role}

@app.post("/login")
def login_user(user_details: LoginRequest, db: Session = Depends(get_db)):
    # Validate if the user exists
    user = db.query(User).filter(User.email == user_details.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Validate the password (assuming a `verify_password` function is implemented in `security.py`)
    if not validate_user_login(db, user_details.email, user_details.password):  # Replace with your password validation logic
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Generate tokens
    access_token = create_access_token(data={"email": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"email": user.email, "role": user.role})
    
    # Return tokens and user details
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }


# Route to refresh access token using the refresh token
@app.post("/refresh-token")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = verify_token(refresh_token)
    
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    user_email = payload.get("sub")
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    # Create a new access token
    new_access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


# Dashboard API for stats (Total Farmers, Total Landlords, Total Spaces, etc.)
@app.get("/dashboard")
def dashboard_stats(user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    total_farmers = db.query(FarmerDetails).count()
    total_landlords = db.query(LandlordDetails).count()
    total_spaces = db.query(Space).count()
    
    # Total acres calculation
    total_acres_farmers = db.query(FarmerDetails.acres).all()
    total_acres_landlords = db.query(LandlordDetails.acres).all()
    
    total_acres_farmers_sum = sum([acre[0] for acre in total_acres_farmers])
    total_acres_landlords_sum = sum([acre[0] for acre in total_acres_landlords])

    total_acres = total_acres_farmers_sum + total_acres_landlords_sum

    # Total connections are the same as total spaces (spaces represent farmer-landlord connections)
    total_connections = total_spaces

    return {
        "total_farmers": total_farmers,
        "total_landlords": total_landlords,
        "total_spaces": total_spaces,
        "total_connections": total_connections,
        "total_acres": total_acres
    }


# Route to get all farmers
@app.get("/farmers")
def get_all_farmers(user: dict = Depends(validate_token_from_header),db: Session = Depends(get_db)):
    if user['role'] in ['farmer', 'admin']:

        farmers = db.query(FarmerDetails).all()
        return farmers
    else:
        raise HTTPException(status_code=400, detail="You Dont have permission to access.")

# Route to get all landlords
@app.get("/landlords")
def get_all_landlords(user: dict = Depends(validate_token_from_header),db: Session = Depends(get_db)):
    if user['role'] in ['landlord', 'admin']:
        landlords = db.query(LandlordDetails).all()
        return landlords
    else:
        raise HTTPException(status_code=400, detail="You Dont have permission to access.")

# Route for farmer details registration
@app.post("/farmer/register")
def register_farmer(farmer_details: FarmerDetailsRequest, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    if user['role'] not in ['admin','farmer']:
        raise HTTPException(status_code=400, detail="You Dont have permission to access.")
    if user['role']=='admin' and farmer_details.user_id:
        user_id = db.query(User).filter(User.id == farmer_details.user_id).first().id    
    elif user['role']=='farmer':
        user_id = db.query(User).filter(User.email == user['email']).first().id
    else:
        raise HTTPException(status_code=400, detail="Please provide farmer id")
    
    existing_farmer = db.query(FarmerDetails).filter(FarmerDetails.user_id == user_id).first()
    if existing_farmer:
        raise HTTPException(status_code=400, detail="Farmer already exists")
    
    if validate_farmer_details(farmer_details.acres, farmer_details.previous_experience):
        new_farmer = FarmerDetails(user_id=user_id, acres=farmer_details.acres, previous_experience=farmer_details.previous_experience)
        db.add(new_farmer)
        db.commit()
        db.refresh(new_farmer)
        return {"user_id": user_id, "acres": farmer_details.acres, "previous_experience": farmer_details.previous_experience}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid farmer details")

# Route for landlord details registration
@app.post("/landlord/register")
def register_landlord(landlord_details: LandlordDetailsRequest, user: dict = Depends(validate_token_from_header),  db: Session = Depends(get_db)):
    if user['role'] not in ['admin','landlord']:
        raise HTTPException(status_code=400, detail="You Dont have permission to access.")
    
    if user['role']=='admin' and landlord_details.user_id:
        user_id = db.query(User).filter(User.id == landlord_details.user_id).first().id    
    elif user['role']=='landlord':
        user_id = db.query(User).filter(User.email == user['email']).first().id
    else:
        raise HTTPException(status_code=400, detail="Please provide landlord id")

    existing_landlord = db.query(LandlordDetails).filter(LandlordDetails.user_id == user_id).first()
    print(existing_landlord)
    if existing_landlord:
        raise HTTPException(status_code=400, detail="landlord already exists")

    if validate_landlord_details(landlord_details.land_type, landlord_details.acres, landlord_details.location, landlord_details.images_list):
        new_landlord = LandlordDetails(user_id=user_id, land_type=landlord_details.land_type, acres=landlord_details.acres, location=landlord_details.location, images_list=landlord_details.images_list)
        db.add(new_landlord)
        db.commit()
        db.refresh(new_landlord)
        return {"user_id": user_id, "land_type": landlord_details.land_type, "acres": landlord_details.acres, "location": landlord_details.location}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid landlord details")

# Admin route for registering another admin
@app.post("/admin/register-admin")
def register_admin(user_details : LoginRequest, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    if not is_admin(db, user['email']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can register new admins")
    
    if validate_user_registration(db, user_details.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    new_admin = User(email=user_details.email, password=user_details.password, role="admin")
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return {"message": "Admin created successfully", "admin_id": new_admin.id}

# Admin route to create a connection (space) between farmer and landlord
@app.post("/admin/connect")
def connect_farmer_landlord(details: FarmerLandlordConnectRequest, user: dict = Depends(validate_token_from_header),  db: Session = Depends(get_db)):
    if not is_admin(db, user['email']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create connections")
    
    farmer = db.query(FarmerDetails).filter(FarmerDetails.user_id == details.farmer_id).first()
    landlord = db.query(LandlordDetails).filter(LandlordDetails.user_id == details.landlord_id).first()
    admin = db.query(User).filter(User.email == user['email']).first()
    if not farmer or not landlord:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer or Landlord not found")
    
    space = Space(farmer_id=farmer.id, landlord_id=landlord.id, admin_id=admin.id)
    db.add(space)
    db.commit()
    db.refresh(space)
    
    return {"message": "Connection (space) created successfully", "space_id": space.id}

# Route to get the number of spaces (connections) for a user
@app.get("/user/{user_id}/spaces")
def get_user_spaces(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    spaces = db.query(Space).filter(Space.admin_id == user_id).all()
    return {"user_id": user.id, "spaces_count": len(spaces)}

# Route to remove a space (connection)
@app.delete("/admin/remove-space/{space_id}")
def remove_space(space_id: int, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    if not is_admin(db, user['email']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can remove spaces")
    
    space = db.query(Space).filter(Space.id == space_id).first()
    if not space:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")
    
    db.delete(space)
    db.commit()
    
    return {"message": "Space removed successfully"}

# Admin route to delete a farmer
@app.delete("/admin/delete-farmer/{farmer_id}")
def delete_farmer(farmer_id: int, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    if not is_admin(db, user['email']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete farmers")
    
    farmer = db.query(FarmerDetails).filter(FarmerDetails.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found")
    
    db.delete(farmer)
    db.commit()
    
    return {"message": "Farmer deleted successfully"}

# Admin route to delete a landlord
@app.delete("/admin/delete-landlord/{landlord_id}")
def delete_landlord(landlord_id: int, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    if not is_admin(db, user['email']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete landlords")
    
    landlord = db.query(LandlordDetails).filter(LandlordDetails.id == landlord_id).first()
    if not landlord:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Landlord not found")
    
    db.delete(landlord)
    db.commit()
    
    return {"message": "Landlord deleted successfully"}

# Route to update farmer details
@app.put("/farmer/update/{farmer_id}")
def update_farmer(farmer_id: int, farmer_details: FarmerDetailsRequest,user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    user_id = db.query(User).filter(User.email ==  user['email']).id
    if user['role']!='admin' and (not user_id or  user_id!=farmer_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")

    farmer = db.query(FarmerDetails).filter(FarmerDetails.user_id == farmer_id).first()
    
    if not farmer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found")
    
    farmer.acres = farmer_details.acres
    farmer.previous_experience = farmer_details.previous_experience
    db.commit()
    db.refresh(farmer)
    
    return {"message": "Farmer details updated", "farmer_id": farmer.id}

# Route to update landlord details
@app.put("/landlord/update/{landlord_id}")
def update_landlord(landlord_id: int, landlord_details: LandlordDetailsRequest,user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):

    user_id = db.query(User).filter(User.email ==  user['email']).id
    if user['role']!='admin' and (not user_id or  user_id!=landlord_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")
    landlord = db.query(LandlordDetails).filter(LandlordDetails.user_id == landlord_id).first()
    
    if not landlord:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Landlord not found")
    
    landlord.land_type = landlord_details.land_type
    landlord.acres = landlord_details.acres
    landlord.location = landlord_details.location
    db.commit()
    db.refresh(landlord)
    
    return {"message": "Landlord details updated", "landlord_id": landlord.id}


@app.post("/upload/images")
async def upload_images(files: List[UploadFile] = File(...)):
    """
    Upload multiple images and return their URLs.
    The images are saved in the 'media' directory and accessible via URLs.
    """
    image_urls = []

    for file in files:
        try:
            # Generate a unique UUID for the file
            unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
            
            # Save the uploaded image to the 'media' directory with a unique name
            file_location = MEDIA_DIR / unique_filename
            with open(file_location, "wb") as f:
                f.write(await file.read())

            # Construct the URL for accessing the image
            image_url = f"http://localhost:9876/media/{unique_filename}"
            image_urls.append(image_url)
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename}: {str(e)}")

    return JSONResponse(content={"image_urls": image_urls})

@app.post("/farmer/{farmer_id}/add_crop")
def add_crop(farmer_id: int, crop: CropCreate,user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    # Check if the farmer exists
    user_obj = db.query(User).filter(User.email == user['email']).first()
    if user['role']!='admin' and farmer_id!=user_obj.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")

    farmer = db.query(User).filter(User.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    # Creating a new crop record
    new_crop = Crop(
        crop_name=crop.crop_name,
        duration=crop.duration,
        images=crop.images,  # Directly passing the list of images
        farmer_id=farmer.id
    )

    db.add(new_crop)
    db.commit()
    db.refresh(new_crop)

    return {"id": new_crop.id, "crop_name": new_crop.crop_name, "duration": new_crop.duration, "images": new_crop.images}

@app.get("/crop/{crop_id}")
def get_crop(crop_id: int,user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    if user['role'] not in ['admin','farmer']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")
    
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return {"id": crop.id, "crop_name": crop.crop_name, "duration": crop.duration, "images": crop.images}

@app.put("/crop/{crop_id}")
def update_crop(crop_id: int, crop: CropCreate,user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    if user['role'] not in ['admin','farmer']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")
    
    db_crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not db_crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    
    db_crop.crop_name = crop.crop_name
    db_crop.duration = crop.duration
    db_crop.images = crop.images
    db_crop.space_id = crop.space_id  # Update the space_id

    db.commit()
    db.refresh(db_crop)
    
    return db_crop

@app.delete("/crop/{crop_id}")
def delete_crop(crop_id: int, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    if user['role'] not in ['admin','farmer']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")
    
    db_crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not db_crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    
    db.delete(db_crop)
    db.commit()
    return {"message": "Crop deleted successfully"}
