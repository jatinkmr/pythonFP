from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from utils.hash import hash_password, verify_password
from utils.token import createRecruiterToken, createCandidateToken
from ulid import ULID
import json

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
        existing = db.query(models.User).filter(models.User.email == user.email).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="User already registered with provided email address",
            )

        new_user = models.User(
            userUlId=str(ULID()),
            email=user.email,
            full_name=user.full_name,
            password=hash_password(user.password),
            role_id=user.role_id,
            skills=user.skills,
            bio=user.bio,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # Create a UserOut instance
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
        # return { "status": False, "message": "" }
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        existing = db.query(models.User).filter(models.User.email == user.email).first()
        if not existing:
            raise HTTPException(status_code=400, detail="Invalid Credentials")

        if not verify_password(user.password, str(existing.password)):
            raise HTTPException(status_code=400, detail="Invalid Credentials")

        if existing.role_id == 3:
            print("Recruiter logging in...")
            token = createRecruiterToken(str(existing.userUlId))
        elif existing.role_id == 2:
            print("Candidate logging in...")
            token = createCandidateToken(str(existing.userUlId))

        response_data = {
            "message": "Login successfully",
            "token": token
        }

        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(response_data),
            media_type="application/json"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
