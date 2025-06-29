import math
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from middlewares.recruiter import get_current_recruiter
import models
import schemas
from ulid import ULID


def recruiterJobCreationService(
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
        return {
            "message": "Job created successfully!!",
            "data": {
                "id": newJob.ulid,
                "title": newJob.title,
                "description": newJob.description,
                "requirements": newJob.requirements,
            },
        }
    except Exception as e:
        raise e


def getRecruiterJobsService(
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
            "message": "Jobs retrieved successfully",
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


def fetchRecruiterJobInfoService(
    jobId: str,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        job = (
            db.query(models.Job)
            .filter(
                models.Job.ulid == jobId,
                models.Job.recruiter_id == current_user.userUlId,
            )
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job not found or you do not have permission to access this job",
            )

        return {
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
    except Exception as e:
        raise e


def deleteRecruiterJobService(
    jobId: str,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        job = (
            db.query(models.Job)
            .filter(
                models.Job.ulid == jobId,
                models.Job.recruiter_id == current_user.userUlId,
            )
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found or you do not have permission to delete this job",
            )

        db.delete(job)
        db.commit()
    except Exception as e:
        raise e


def updateRecruiterJobService(
    jobId: str,
    job_data: schemas.JobUpdate,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        job = (
            db.query(models.Job)
            .filter(
                models.Job.ulid == jobId,
                models.Job.recruiter_id == current_user.userUlId,
            )
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found or you do not have permission to update this job",
            )

        # Update job fields
        if job_data.title is not None:
            job.title = models.Job.title.type.python_type(job_data.title)
        if job_data.description is not None:
            job.description = models.Job.description.type.python_type(
                job_data.description
            )
        if job_data.requirements is not None:
            job.requirements = models.Job.requirements.type.python_type(
                job_data.requirements
            )

        db.commit()
        db.refresh(job)

        return {
            "message": "Job updated successfully",
            "data": {
                "id": job.ulid,
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements,
            },
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e


def fetchJobApplicationService(
    jobId: str,
    page: int = 1,
    limit: int = 10,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        isJobRelatedToRecruiter = (
            db.query(models.Job)
            .filter(
                models.Job.ulid == jobId,
                models.Job.recruiter_id == current_user.userUlId,
            )
            .first()
        )

        if not isJobRelatedToRecruiter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provided job not linked with current recruiter",
            )

        if page < 1:
            page = 1

        if limit < 1 or limit > 100:
            limit = 10

        offset = (page - 1) * limit

        totalCount = (
            db.query(models.JobApplication)
            .filter(models.JobApplication.job_id == jobId)
            .count()
        )

        jobApplications = (
            db.query(models.JobApplication, models.User)
            .join(
                models.User, models.JobApplication.candidate_id == models.User.userUlId
            )
            .filter(models.JobApplication.job_id == jobId)
            .offset(offset)
            .limit(limit)
            .all()
        )

        jobAppData = []
        for jobApplication, candidate in jobApplications:
            applicationData = {
                "application_id": jobApplication.ulid,
                "candidate_name": candidate.full_name,
                "candidate_email": candidate.email,
                "status": jobApplication.status,
                "applied_at": (
                    jobApplication.applied_at.isoformat()
                    if jobApplication.applied_at
                    else None
                ),
            }

            if hasattr(candidate, "bio"):
                applicationData["candidate_bio"] = candidate.bio

            if hasattr(candidate, "skills"):
                applicationData["skills"] = candidate.skills

            jobAppData.append(applicationData)

        totalPages = math.ceil(totalCount / limit) if totalCount > 0 else 1

        return {
            "message": "Job Application retrieved successfully",
            "data": jobAppData,
            "pagination": {
                "current_page": page,
                "per_page": limit,
                "total_items": totalCount,
                "total_pages": totalPages,
            },
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise e


def updateJobApplicationStatusService(
    applicationId: str,
    latestStatus: str,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        allowedStatuses = {"accepted", "rejected"}
        if latestStatus not in allowedStatuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status!!",
            )

        applicationInfo = (
            db.query(models.JobApplication)
            .filter(models.JobApplication.ulid == applicationId)
            .first()
        )

        if applicationInfo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job application not found",
            )

        if applicationInfo.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update status. Current status of requested application is {applicationInfo.status} already.",
            )

        isJobRelatedToRecruiter = (
            db.query(models.Job)
            .filter(
                models.Job.ulid == applicationInfo.job_id,
                models.Job.recruiter_id == current_user.userUlId,
            )
            .first()
        )

        if isJobRelatedToRecruiter is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Job is not related with the current recruiter",
            )

        applicationInfo.status = models.JobApplication.status.type.python_type(
            latestStatus
        )

        db.commit()
    except HTTPException as e:
        raise e
    except Exception as e:
    raise e
