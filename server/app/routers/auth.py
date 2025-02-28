from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..database import get_mongo_db
from .. import model, utils, oauth2, schemas
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter(
    tags=['Authentication']
)


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def signup(user: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    # Check if user already exists
    existing_user = await db.Users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password using utils
    hashed_password = utils.hash(user.password)

    # Create user document manually
    user_dict = {
        "username": user.username,
        "password": hashed_password,
        "created_at": str(datetime.now()),
        "categories": [],
        "likedStocks" : []
    }

    # Insert into database
    result = await db.Users.insert_one(user_dict)

    # Get created user
    created_user = await db.Users.find_one({"_id": result.inserted_id})
    created_user["id"] = str(created_user["_id"])
    del created_user["_id"]
    return created_user


@router.post("/login", response_model=schemas.LoginResponse)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    user = await db.Users.find_one({"username": user_credentials.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    # Use utils.verify for password check
    if not utils.verify(user_credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    access_token = oauth2.create_access_code(
        data={"user_id": str(user["_id"])})
    return {
        "user_id": str(user["_id"]),
        "access_token": access_token,
        "token_type": "bearer"
    }
