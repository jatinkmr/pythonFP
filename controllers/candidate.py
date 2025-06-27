from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from config.database import get_db
from middlewares.candidate import get_current_candidate
import models
import json
from services import candidate

router = APIRouter()


@router.get("/")
def testCandidateRoute():
    return Response(
        status_code=status.HTTP_200_OK,
        media_type="application/json",
        content=json.dumps({"message": "Candidate route is running..."}),
    )


@router.get("/jobs")
def fetchJobListing(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    try:
        response_data = candidate.fetchJobListing(page, limit, db)

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
def fetchJobInfo(
    jobId: str,
    db: Session = Depends(get_db),
):
    try:
        responseData = candidate.fetchJobInfo(jobId, db)

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


@router.post("/jobs-application/{jobId}")
def sendJobApplication(
    jobId: str,
    current_user: models.User = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    try:
        candidate.sendJobApplication(jobId, current_user, db)

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
        response_data = candidate.fetchCandidateAppliedJobs(page, limit, current_user, db)

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
