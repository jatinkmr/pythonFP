from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db
from datetime import datetime
from routers import auth, recruiter, candidate

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def homeRoute():
    return {"status": True, "message": "Welcome to home Page!!"}


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(recruiter.router, prefix="/recruiter", tags=["Recruiter"])
app.include_router(candidate.router, prefix="/candidate", tags=["Candidate"])
