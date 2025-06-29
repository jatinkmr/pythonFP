from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from config.database import get_db
from middlewares.recruiter import get_current_recruiter
import models, schemas
from services.recruiter import (
    deleteRecruiterJobService,
    fetchJobApplicationService,
    fetchRecruiterJobInfoService,
    getRecruiterJobsService,
    recruiterJobCreationService,
    updateJobApplicationStatusService,
    updateRecruiterJobService,
)
import json
import math

router = APIRouter()


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
        responseData = recruiterJobCreationService(job_data, current_user, db)
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
        responseData = getRecruiterJobsService(page, limit, current_user, db)

        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(responseData),
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to fetch job listing due to: {str(e)}",
        )


@router.get("/jobs/{jobId}")
def fetchRecruiterJobInfo(
    jobId: str,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        responseData = fetchRecruiterJobInfoService(jobId, current_user, db)

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


@router.delete("/jobs/{jobId}")
def deleteRecruiterJob(
    jobId: str,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        deleteRecruiterJobService(jobId, current_user, db)
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps({"message": "Job deleted successfully"}),
            media_type="application/json",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job deletion failed due to: {str(e)}",
        )


@router.patch("/jobs/{jobId}")
def updateRecruiterJobs(
    jobId: str,
    job_data: schemas.JobUpdate,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        responseData = updateRecruiterJobService(jobId, current_user, db)

        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(responseData),
            media_type="application/json",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to update the job info due to: {str(e)}",
        )


@router.get("/job-applications/{jobId}")
def fetchJobApplications(
    jobId: str,
    page: int = 1,
    limit: int = 10,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        responseData = fetchJobApplicationService(jobId, page, limit, current_user, db)

        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(responseData),
            media_type="application/json",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to fetch the list of Candidate due to: {str(e)}",
        )


@router.patch("/job-application/{applicationId}/status/{latestStatus}")
def updateJobApplicationStatus(
    applicationId: str,
    latestStatus: str,
    current_user: models.User = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        updateJobApplicationStatusService(applicationId, latestStatus, current_user, db)

        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps(
                {"message": "Job application status updated successfully!!"}
            ),
            media_type="application/json",
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to update the status of job application due to: {str(e)}",
        )
