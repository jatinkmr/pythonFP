from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from middlewares.candidate import get_current_candidate
import models, schemas
import math
from datetime import datetime
from ulid import ULID

from database import get_db


def fetchJobListing(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
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

        return {
            "message": "Jobs list retrieved successfully",
            "data": jobsData,
            "pagination": {
                "current_page": page,
                "per_page": limit,
                "total_items": totalCount,
                "total_pages": total_pages,
            },
        }
    except Exception as e:
        raise e


def fetchJobInfo(jobId: str, db: Session = Depends(get_db)):
    try:
        job = db.query(models.Job).filter(models.Job.ulid == jobId).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found",
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

        return responseData
    except Exception as e:
        raise e


def sendJobApplication(jobId: str, current_user: models.User, db: Session=Depends(get_db)):
    try:
        job = db.query(models.Job).filter(models.Job.ulid == jobId).first()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job not found",
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

        return
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e

def fetchCandidateAppliedJobs(page: int = 1, limit: int = 10, current_user: models.User = Depends(get_current_candidate), db: Session = Depends(get_db)):
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

        totalPages = math.ceil(totalCount / limit) if totalCount > 0 else 1

        response_data = {
            "message": "Applied jobs retrieved successfully",
            "data": applicationsData,
            "pagination": {
                "current_page": page,
                "per_page": limit,
                "totalCount": totalCount,
                "totalPages": totalPages,
            },
        }

        return response_data
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e
