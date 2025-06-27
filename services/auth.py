from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import schemas, models
from ulid import ULID
from utils.hash import hash_password, verify_password
from utils.token import createRecruiterToken, createCandidateToken


def registerUserService(user: schemas.UserCreate, db: Session = Depends(get_db)):
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

        return new_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e


def userLoginService(user: schemas.UserLogin, db: Session = Depends(get_db)):
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

        return token
    except:
        raise e
