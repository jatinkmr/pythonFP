import datetime
import math
import random
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import get_db
from config.redis import redisStore
import schemas, models
from ulid import ULID
from utils.hash import hash_password, verify_password
from utils.token import createRecruiterToken, createCandidateToken
from utils.utils import generateUniqueSixDigitToken


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
    except Exception as e:
        raise e


def forgotPasswordService(
    reqBody: schemas.ForgotPassword, db: Session = Depends(get_db)
):
    try:
        isUserExist = (
            db.query(models.User).filter(models.User.email == reqBody.email).first()
        )
        if not isUserExist:
            raise HTTPException(status_code=404, detail="Invalid Email")

        isTokenExist = redisStore.get(str(isUserExist.userUlId))

        if isTokenExist:
            tokenToBeSend = isTokenExist
        else:
            tokenToBeSend = generateUniqueSixDigitToken()
            redisStore.set(str(isUserExist.userUlId), tokenToBeSend, 600)  # 10 minutes

        return
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e


def resetPassword(reqBody: schemas.ResetUserPassword, db: Session = Depends(get_db)):
    try:
        tokenFromStore = redisStore.get(str(reqBody.ulid))
        if not tokenFromStore:
            raise HTTPException(status_code=400, detail="Link Expired!!")

        isUserExist = (
            db.query(models.User).filter(models.User.userUlId == tokenFromStore).first()
        )

        if not isUserExist:
            raise HTTPException(status_code=404, detail="User not found")

        isUserExist.password = models.User.type.python_type(
            hash_password(reqBody.newPassword)
        )

        db.add(isUserExist)
        db.commit()

        return True
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
