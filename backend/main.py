from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from db import SessionLocal, init_db, User, FarmerDetails, LandlordDetails, Space, Crop
from validators import * #validate_user_registration, validate_farmer_details, validate_landlord_details, is_admin, validate_user_login, FarmerDetailsRequest
from security import create_access_token, create_refresh_token, verify_token, validate_token_from_header
from typing import List
from sqlalchemy.sql import func
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
    access_token = create_access_token(data={"id": user.id, "email": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"id": user.id, "email": user.email, "role": user.role})

    
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
    # Farmers and landlords counts
    total_farmers = db.query(FarmerDetails).count()
    total_landlords = db.query(LandlordDetails).count()

    # Collaboration spaces count
    total_spaces = db.query(Space).count()

    # Total acres calculation for farmers and landlords
    total_land_handling_capacity = db.query(FarmerDetails.land_handling_capacity).all()
    total_landlord_acres = db.query(LandlordDetails.acres).all()

    total_land_handling_capacity_sum = sum([capacity[0] for capacity in total_land_handling_capacity])
    total_landlord_acres_sum = sum([acre[0] for acre in total_landlord_acres])

    # Breakdown of crops in collaborations
    crop_stats = (
        db.query(Crop.crop_name, func.count(Crop.id))
        .group_by(Crop.crop_name)
        .all()
    )
    crop_breakdown = {crop_name: count for crop_name, count in crop_stats}

    return {
        "total_farmers": total_farmers,
        "total_landlords": total_landlords,
        "total_spaces": total_spaces,
        "total_land_handling_capacity": total_land_handling_capacity_sum,
        "total_landlord_acres": total_landlord_acres_sum,
        "crop_breakdown": crop_breakdown
    }


# API to get single farmer details by ID (accessible only by the farmer themselves)
@app.get("/farmers/{farmer_id}")
def get_farmer_details(farmer_id: int, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    """
    Fetch details of a specific farmer by ID.
    Only admins or the farmer themselves can access this endpoint.
    """
    # Fetch the farmer details
    farmer = db.query(FarmerDetails).filter(FarmerDetails.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found.")

    # Authorization check
    if user["role"] != "admin" and farmer.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="You do not have access to this resource.")

    return farmer




# API to get single landlord details by ID (accessible only by the landlord themselves)
@app.get("/landlords/{landlord_id}")
def get_single_landlord(landlord_id: int, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
    landlord = db.query(LandlordDetails).filter(LandlordDetails.id == landlord_id).first()

    if not landlord:
        raise HTTPException(status_code=404, detail="Landlord not found")

    # Check if the requesting user is the landlord or admin
    if user['role'] == 'landlord' and user['id'] == landlord.user_id:
        return landlord
    elif user['role'] == 'admin':
        return landlord
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")



# Route to get all farmers
@app.get("/farmers")
def get_all_farmers(user: dict = Depends(validate_token_from_header),db: Session = Depends(get_db)):
    if user['role'] in ['admin']:

        farmers = db.query(FarmerDetails).all()
        return farmers
    else:
        raise HTTPException(status_code=400, detail="You Dont have permission to access.")

# Route to get all landlords
@app.get("/landlords")
def get_all_landlords(user: dict = Depends(validate_token_from_header),db: Session = Depends(get_db)):
    if user['role'] in ['admin']:
        landlords = db.query(LandlordDetails).all()
        return landlords
    else:
        raise HTTPException(status_code=400, detail="You Dont have permission to access.")

# Route for farmer details registration
@app.post("/farmer/register")
def register_farmer(farmer_details: FarmerDetailsRequest,user: dict = Depends(validate_token_from_header),db: Session = Depends(get_db)
):
    # Check if the user has the correct role
    if user['role'] not in ['admin', 'farmer']:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")

    # Determine the user_id based on the role
    user_id = None
    if user['role'] == 'admin' and farmer_details.user_id:
        user_obj = db.query(User).filter(User.id == farmer_details.user_id).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="User ID provided does not exist.")
        user_id = user_obj.id
    elif user['role'] == 'farmer':
        user_obj = db.query(User).filter(User.email == user['email']).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="Farmer not found.")
        user_id = user_obj.id
    else:
        raise HTTPException(status_code=400, detail="Please provide a valid user ID.")

    # Check if the farmer already exists
    existing_farmer = db.query(FarmerDetails).filter(FarmerDetails.user_id == user_id).first()
    if existing_farmer:
        raise HTTPException(status_code=400, detail="Farmer already exists.")

    # Validate the provided details
    if validate_farmer_details(farmer_details.land_handling_capacity):
        new_farmer = FarmerDetails(
            user_id=user_id,
            phone_number=farmer_details.phone_number,
            land_handling_capacity=farmer_details.land_handling_capacity,
            preferred_locations=farmer_details.preferred_locations,
        )
        db.add(new_farmer)
        db.commit()
        db.refresh(new_farmer)
        return {
            "message": "Farmer registered successfully",
            "farmer": {
                "user_id": new_farmer.user_id,
                "phone_number": new_farmer.phone_number,
                "land_handling_capacity": new_farmer.land_handling_capacity,
                "preferred_locations": new_farmer.preferred_locations,
            }
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid farmer details.")
# Route for landlord details registration
@app.post("/landlord/register")
def register_landlord(
    landlord_details: LandlordDetailsRequest,
    user: dict = Depends(validate_token_from_header),
    db: Session = Depends(get_db)
):
    # Check user role
    if user['role'] not in ['admin', 'landlord']:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")

    # Determine user ID based on role
    user_id = None
    if user['role'] == 'admin' and landlord_details.user_id:
        user_obj = db.query(User).filter(User.id == landlord_details.user_id).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="User ID provided does not exist.")
        user_id = user_obj.id
    elif user['role'] == 'landlord':
        user_obj = db.query(User).filter(User.email == user['email']).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="Landlord not found.")
        user_id = user_obj.id
    else:
        raise HTTPException(status_code=400, detail="Please provide a valid user ID.")

    # Check if landlord already exists
    existing_landlord = db.query(LandlordDetails).filter(LandlordDetails.user_id == user_id).first()
    if existing_landlord:
        raise HTTPException(status_code=400, detail="Landlord already exists.")

    # Validate landlord details
    if validate_landlord_details(
        landlord_details.soil_type,
        landlord_details.acres,
        landlord_details.location,
        landlord_details.images
    ):
        new_landlord = LandlordDetails(
            user_id=user_id,
            soil_type=landlord_details.soil_type,
            acres=landlord_details.acres,
            location=landlord_details.location,
            images_list=landlord_details.images,
        )
        db.add(new_landlord)
        db.commit()
        db.refresh(new_landlord)
        return {
            "message": "Landlord registered successfully",
            "landlord": {
                "user_id": new_landlord.user_id,
                "soil_type": new_landlord.soil_type,
                "acres": new_landlord.acres,
                "location": new_landlord.location,
                "images": new_landlord.images_list,
            }
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid landlord details.")


# Route to get the number of spaces (connections) for a user
@app.get("/user/{user_id}/collaborations")
def get_user_collaborations(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all collaborations associated with a specific farmer or landlord.
    
    Args:
        user_id (int): The ID of the farmer or landlord.
        db (Session): The database session.
    
    Returns:
        dict: Collaborations involving the user.
    """
    # Fetch the user by ID
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check the user's role
    if user.role not in ["farmer", "landlord"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers or landlords can view their collaborations.",
        )

    # Fetch collaborations based on role
    if user.role == "farmer":
        collaborations = db.query(Space).filter(Space.farmer_id == user_id).all()
    elif user.role == "landlord":
        collaborations = db.query(Space).filter(Space.landlord_id == user_id).all()

    # Format response
    collaboration_data = [
        {
            "space_id": collab.id,
            "farmer_id": collab.farmer_id,
            "landlord_id": collab.landlord_id,
            "description": collab.description,
            "crops": [
                {"id": crop.id, "name": crop.crop_name, "duration": crop.duration}
                for crop in collab.crops
            ],  # List crops involved in the collaboration
        }
        for collab in collaborations
    ]

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        },
        "collaborations": collaboration_data,
        "total_collaborations_count": len(collaborations),
    }


@app.post("/admin/create-crop")
def create_crop(crop_data: dict, db: Session = Depends(get_db)):
    """
    Create a crop with its cultivation steps.
    crop_data example:
    {
        "crop_name": "Paddy",
        "duration": "120 days",
        "steps": [
            {"name": "Land Preparation", "description": "Prepare the field."},
            {"name": "Sowing", "description": "Plant the seeds."},
            ...
        ]
    }
    """
    crop = Crop(
        crop_name=crop_data["crop_name"],
        duration=crop_data["duration"],
        steps=crop_data["steps"],  # Directly store steps as JSON
    )
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return {"message": "Crop created successfully", "crop_id": crop.id}

@app.get("/crop/{crop_id}/steps")
def get_crop_steps(crop_id: int, db: Session = Depends(get_db)):
    """
    Get the steps for a specific crop.
    """
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    return {"crop_name": crop.crop_name, "steps": crop.steps}

@app.post("/crop/{crop_id}/step/{step_index}/upload-proof")
async def upload_proof(
    crop_id: int,
    step_index: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload proof (images/videos) for a specific step in a crop.
    """
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    if step_index >= len(crop.steps):
        raise HTTPException(status_code=400, detail="Invalid step index")

    # Save files to media directory and update the step with proof URLs
    proofs = []
    for file in files:
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_location = MEDIA_DIR / unique_filename
        with open(file_location, "wb") as f:
            f.write(await file.read())

        proofs.append(f"/media/{unique_filename}")

    # Append proofs to the step
    crop.steps[step_index].setdefault("proofs", []).extend(proofs)
    db.commit()
    return {"message": "Proof uploaded successfully", "proofs": proofs}



# # Route to remove a space (connection)
# @app.delete("/admin/remove-space/{space_id}")
# def remove_space(space_id: int, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
#     if not is_admin(db, user['email']):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can remove spaces")
    
#     space = db.query(Space).filter(Space.id == space_id).first()
#     if not space:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")
    
#     db.delete(space)
#     db.commit()
    
#     return {"message": "Space removed successfully"}

# # Admin route to delete a farmer
# @app.delete("/admin/delete-farmer/{farmer_id}")
# def delete_farmer(farmer_id: int, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
#     if not is_admin(db, user['email']):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete farmers")
    
#     farmer = db.query(FarmerDetails).filter(FarmerDetails.id == farmer_id).first()
#     if not farmer:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found")
    
#     db.delete(farmer)
#     db.commit()
    
#     return {"message": "Farmer deleted successfully"}

# # Admin route to delete a landlord
# @app.delete("/admin/delete-landlord/{landlord_id}")
# def delete_landlord(landlord_id: int, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
#     if not is_admin(db, user['email']):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete landlords")
    
#     landlord = db.query(LandlordDetails).filter(LandlordDetails.id == landlord_id).first()
#     if not landlord:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Landlord not found")
    
#     db.delete(landlord)
#     db.commit()
    
#     return {"message": "Landlord deleted successfully"}

# # Route to update farmer details
# @app.put("/farmer/update/{farmer_id}")
# def update_farmer(farmer_id: int, farmer_details: FarmerDetailsRequest,user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
#     user_id = db.query(User).filter(User.email ==  user['email']).id
#     if user['role']!='admin' and (not user_id or  user_id!=farmer_id):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")

#     farmer = db.query(FarmerDetails).filter(FarmerDetails.user_id == farmer_id).first()
    
#     if not farmer:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer not found")
    
#     farmer.acres = farmer_details.acres
#     farmer.previous_experience = farmer_details.previous_experience
#     db.commit()
#     db.refresh(farmer)
    
#     return {"message": "Farmer details updated", "farmer_id": farmer.id}

# # Route to update landlord details
# @app.put("/landlord/update/{landlord_id}")
# def update_landlord(landlord_id: int, landlord_details: LandlordDetailsRequest,user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):

#     user_id = db.query(User).filter(User.email ==  user['email']).id
#     if user['role']!='admin' and (not user_id or  user_id!=landlord_id):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")
#     landlord = db.query(LandlordDetails).filter(LandlordDetails.user_id == landlord_id).first()
    
#     if not landlord:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Landlord not found")
    
#     landlord.land_type = landlord_details.land_type
#     landlord.acres = landlord_details.acres
#     landlord.location = landlord_details.location
#     db.commit()
#     db.refresh(landlord)
    
#     return {"message": "Landlord details updated", "landlord_id": landlord.id}


# from fastapi import Request

# @app.post("/upload/images")
# async def upload_images(request: Request, files: List[UploadFile] = File(...)):
#     """
#     Upload multiple images and return their URLs.
#     The images are saved in the 'media' directory and accessible via URLs.
#     """
#     print(f"Received files: {files}")  # Debugging input
#     image_urls = []

#     for file in files:
#         try:
#             # Generate a unique UUID for the file
#             unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
            
#             # Save the uploaded image to the 'media' directory with a unique name
#             file_location = MEDIA_DIR / unique_filename
#             with open(file_location, "wb") as f:
#                 f.write(await file.read())

#             # Construct the URL for accessing the image
#             base_url = f"{request.base_url.scheme}://{request.base_url.netloc}"
#             image_url = f"{base_url}/media/{unique_filename}"
#             image_urls.append(image_url)
        
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Failed to upload {file.filename}: {str(e)}")

#     return JSONResponse(content={"image_urls": image_urls})






# @app.delete("/crop/{crop_id}")
# def delete_crop(crop_id: int, user: dict = Depends(validate_token_from_header), db: Session = Depends(get_db)):
#     if user['role'] not in ['admin','farmer']:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized")
    
#     db_crop = db.query(Crop).filter(Crop.id == crop_id).first()
#     if not db_crop:
#         raise HTTPException(status_code=404, detail="Crop not found")
    
#     db.delete(db_crop)
#     db.commit()
#     return {"message": "Crop deleted successfully"}
