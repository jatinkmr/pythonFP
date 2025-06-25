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
def testRecruiterRoute():
    return Response(
        status_code=status.HTTP_200_OK,
        media_type="application/json",
        content=json.dumps({"message": "Recruiter route is running..."}),
    )
