from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from config.database import get_db
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )


@router.post("/forgot-password")
def forgotPassword(reqBody: schemas.ForgotPassword, db: Session = Depends(get_db)):
    try:
        auth.forgotPasswordService(reqBody, db)

        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps({"message": "Email sent!!"}),
            media_type="application/json",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to send mail: {str(e)}",
        )


@router.post("/reset-password")
def resetPassword(reqBody: schemas.ResetUserPassword, db: Session = Depends(get_db)):
    try:
        auth.resetPassword(reqBody, db)

        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps({"message": "Password updated successfully!!"}),
            media_type="application/json",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unabel to reset the password due to: {str(e)}",
        )
