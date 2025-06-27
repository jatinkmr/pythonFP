from fastapi import APIRouter, Depends, HTTPException, status, Response, Header
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Column
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from utils.hash import hash_password, verify_password
from utils.token import verifyCandidateToken
from ulid import ULID
import json
from typing import Optional
import math
from datetime import datetime

router = APIRouter()


@router.get("/")
def testCandidateRoute():
    return Response(
        status_code=status.HTTP_200_OK,
        media_type="application/json",
        content=json.dumps({"message": "Candidate route is running..."}),
    )


@router.get("/jobs")
def fetchJobListingRoute(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    try:
        if page < 1:
            page = 1

        if limit < 1 or limit > 100:
            limit = 10

        offset = (page - 1) * limit

        totalCount = db.query(models.Job).count()

        jobs = (
            db.query(models.Job)
            .order_by(models.Job.created_at.desc())
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
            "message": "Jobs list retrieved successfully",
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
            detail=f"Unable to fetch job list due to: {str(e)}",
        )


@router.get("/jobs/{jobId}")
def fetchRecruiterJobInfo(
    jobId: str,
    db: Session = Depends(get_db),
):
    try:
        job = db.query(models.Job).filter(models.Job.ulid == jobId).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job not found or you do not have permission to access this job",
            )

        responseData = {
            "message": "Job info available",
            "data": {
                "id": job.ulid,
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements,
                "created_at": (
                    job.created_at.isoformat() if hasattr(job, "created_at") else None
                ),
            },
        }

        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(responseData),
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to fetch job info due to: {str(e)}",
        )


def get_current_candidate(
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
    token_result = verifyCandidateToken(token)
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

    if user.role_id != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Recruiter role required",
        )

    return user


@router.post("/jobs-application/{jobId}")
def sendJobApplication(
    jobId: str,
    current_user: models.User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    try:
        job = db.query(models.Job).filter(models.Job.ulid == jobId).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job not found or you do not have permission to access this job",
            )

        isCandidateAlreadyApplied = (
            db.query(models.JobApplication)
            .filter(
                models.JobApplication.candidate_id == current_user.userUlId,
                models.JobApplication.job_id == jobId,
            )
            .first()
        )

        if isCandidateAlreadyApplied:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You've already applied for the same job previously!!",
            )

        newApplication = models.JobApplication(
            ulid=str(ULID()),
            job_id=jobId,
            candidate_id=current_user.userUlId,
            applied_at=datetime.utcnow(),
        )

        db.add(newApplication)
        db.commit()

        return Response(
            status_code=status.HTTP_201_CREATED,
            content=json.dumps({"message": "Job application submitted successfully!!"}),
            media_type="application/json",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to apply due to: {str(e)}",
        )


@router.get("/applied-jobs")
def fetchCandidateAppliedJobs(
    page: int = 1,
    limit: int = 10,
    current_user: models.User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    try:
        if page < 1:
            page = 1

        if limit < 1 or limit > 100:
            limit = 10

        offset = (page - 1) * limit

        totalCount = (
            db.query(models.JobApplication)
            .filter(models.JobApplication.candidate_id == current_user.userUlId)
            .count()
        )

        jobApplications = (
            db.query(models.JobApplication, models.Job)
            .join(models.Job, models.JobApplication.job_id == models.Job.ulid)
            .filter(models.JobApplication.candidate_id == current_user.userUlId)
            .offset(offset)
            .limit(limit)
            .all()
        )

        applicationsData = []
        for application, job in jobApplications:
            applicationsData.append(
                {
                    "application_id": application.ulid,
                    "applied_at": application.applied_at.isoformat(),
                    "job": {
                        "id": job.ulid,
                        "title": job.title,
                        "description": job.description,
                        "requirements": job.requirements,
                        "created_at": (
                            job.created_at.isoformat()
                            if hasattr(job, "created_at")
                            else None
                        ),
                    },
                }
            )

        total_pages = math.ceil(totalCount / limit) if totalCount > 0 else 1

        response_data = {
            "message": "Applied jobs retrieved successfully",
            "data": applicationsData,
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
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to fetch applied jobs due to: {str(e)}",
        )
