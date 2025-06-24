from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


class JobApplicationBase(BaseModel):
    status: Optional[str] = "pending"


class JobApplicationCreate(JobApplicationBase):
    job_id: int
    candidate_id: int
    ulid: str


class JobApplicationOut(JobApplicationBase):
    id: int
    ulid: str
    job_id: int
    candidate_id: int
    applied_at: datetime

    class Config:
        orm_mode = True


class JobBase(BaseModel):
    title: str
    description: str
    requirements: str


class JobCreate(JobBase):
    ulid: str
    recruiter_id: int


class JobOut(JobBase):
    id: int
    ulid: str
    recruiter_id: int
    created_at: datetime
    applications: List[JobApplicationOut] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_recruiter: Optional[bool] = False
    skills: Optional[str] = None
    bio: Optional[str] = None

    @validator("full_name")
    def full_name_must_not_be_blank(cls, v):
        if not v.strip():
            raise ValueError("Full name cannot be empty or blank")
        return v

    @validator("email")
    def email_must_not_be_blank(cls, v):
        if not v.strip():
            raise ValueError("Email cannot be empty or blank")
        return v


class UserCreate(UserBase):
    password: str

    @validator("password")
    def password_must_not_be_blank(cls, v):
        if not v.strip():
            raise ValueError("Password cannot be empty or blank")
        return v


class UserOut(BaseModel):
    id: int
    userUlId: str
    email: EmailStr
    full_name: str
    is_recruiter: bool
    skills: Optional[str]
    bio: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @validator("email")
    def emailValidator(cls, v):
        if not v.strip():
            raise ValueError("Email cannot be empty or blank")
        return v

    @validator("password")
    def passWordValidator(cls, v):
        if not v.strip():
            raise ValueError("Password cannot be empty or blank")
        return v
