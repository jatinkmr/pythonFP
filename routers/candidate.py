from fastapi import APIRouter, Depends, HTTPException, status, Response, Header
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Column
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from utils.hash import hash_password, verify_password
from utils.token import createCandidateToken
from ulid import ULID
import json
from typing import Optional
import math

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
