from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from utils.hash import hash_password, verify_password
from ulid import ULID

router = APIRouter()


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
            is_recruiter=user.is_recruiter,
            skills=user.skills,
            bio=user.bio,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except HTTPException as e:
        raise e
    except Exception as e:
        # return { "status": False, "message": "" }
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=schemas.UserOut)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        existing = db.query(models.User).filter(models.User.email == user.email).first()
        if not existing:
            raise HTTPException(status_code=400, detail="Invalid Credentials")

        if not verify_password(user.password, existing.password):
            raise HTTPException(status_code=400, detail="Invalid Credentials")

        return existing  # Safe with response_model filtering

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
