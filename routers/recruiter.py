from fastapi import APIRouter, Depends, HTTPException, status, Response, Header
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from utils.hash import hash_password, verify_password
from utils.token import createRecruiterToken, createCandidateToken, verifyRecruiterToken
from ulid import ULID
import json
from typing import Optional
import math

router = APIRouter()


def get_current_recruiter(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    # Verify the token
    token_result = verifyRecruiterToken(token)
    if not token_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=token_result["error"]
        )

    # Get user from database
    user_id = token_result["data"]["userUlId"]
    user = db.query(models.User).filter(models.User.userUlId == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if user.role_id != 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Recruiter role required",
        )

    return user


@router.get("/")
def testRecruiterRoute():
    return Response(
        status_code=status.HTTP_200_OK,
        media_type="application/json",
        content=json.dumps({"message": "Recruiter route is running..."}),
    )


@router.post("/jobs")
def recruiterJobCreation(
    job_data: schemas.JobCreate,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        existing = (
            db.query(models.Job)
            .filter(
                models.Job.title == job_data.title,
                models.Job.recruiter_id == current_user.userUlId,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Job with the same title already exists for this recruiter",
            )

        newJob = models.Job(
            ulid=str(ULID()),
            title=job_data.title,
            description=job_data.description,
            requirements=job_data.requirements,
            recruiter_id=current_user.userUlId,
        )
        db.add(newJob)
        db.commit()
        db.refresh(newJob)
        responseData = {
            "message": "Job created successfully!!",
            "data": {
                "id": newJob.ulid,
                "title": newJob.title,
                "description": newJob.description,
                "requirements": newJob.requirements,
            },
        }
        return Response(
            status_code=status.HTTP_201_CREATED,
            content=json.dumps(responseData),
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job Creation failed due to: {str(e)}",
        )


@router.get("/jobs")
def getRecruiterJobs(
    page: int = 1,
    limit: int = 10,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        if page < 1:
            page = 1

        if limit < 1 or limit > 100:
            limit = 10

        offset = (page - 1) * limit

        totalCount = (
            db.query(models.Job)
            .filter(models.Job.recruiter_id == current_user.userUlId)
            .count()
        )

        jobs = (
            db.query(models.Job)
            .filter(models.Job.recruiter_id == current_user.userUlId)
            .order_by(models.Job.created_at.desc())  # Order by most recent first
            .offset(offset)
            .limit(limit)
            .all()
        )

        jobsData = []
        for job in jobs:
            jobsData.append(
                {
                    "id": job.ulid,
                    "title": job.title,
                    "description": job.description,
                    "requirements": job.requirements,
                    "created_at": (
                        job.created_at.isoformat()
                        if hasattr(job, "created_at")
                        else None
                    ),
                }
            )

        total_pages = math.ceil(totalCount / limit) if totalCount > 0 else 1

        response_data = {
            "message": "Jobs retrieved successfully",
            "data": jobsData,
            "pagination": {
                "current_page": page,
                "per_page": limit,
                "total_items": totalCount,
                "total_pages": total_pages,
            },
        }

        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(response_data),
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to fetch job listing due to: {str(e)}",
        )
