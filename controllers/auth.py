from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from utils.hash import hash_password, verify_password
from ulid import ULID
import json
from services import auth

router = APIRouter()


@router.get("/")
def testAuthRoute():
    return Response(
        status_code=status.HTTP_200_OK,
        media_type="application/json",
        content=json.dumps({"message": "Auth route is running..."}),
    )


@router.post("/register")
def registerUser(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = auth.registerUserService(user, db)

        response_data = {
            "message": "User registered successfully",
            "data": {
                "id": new_user.userUlId,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "skills": new_user.skills,
                "bio": new_user.bio,
            },
        }

        return Response(
            status_code=status.HTTP_201_CREATED,
            content=json.dumps(response_data),
            media_type="application/json",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        token = auth.userLoginService(user, db)

        response_data = {"message": "Login successfully", "token": token}

        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(response_data),
            media_type="application/json",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
