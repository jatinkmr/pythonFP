from multiprocessing import Value
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


class JobApplicationBase(BaseModel):
    status: Optional[str] = "pending"


class JobApplicationCreate(JobApplicationBase):
    job_id: str
    candidate_id: int
    ulid: str


class JobApplicationOut(JobApplicationBase):
    id: int
    ulid: str
    job_id: str
    candidate_id: str
    applied_at: datetime

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    title: str
    description: str
    requirements: str

    @validator("title")
    def title_validator(cls, v):
        if not v.strip():
            raise ValueError("Job Title cannot be empty or blank")
        return v

    @validator("description")
    def description_validator(cls, v):
        if not v.strip():
            raise ValueError("Job Description cannot be empty or blank")
        return v

    @validator("requirements")
    def requirement_validator(cls, v):
        if not v.strip():
            raise ValueError("Job Requirement cannot be empty or blank")
        return v


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role_id: int  # 1->Admin, 2->Candidate, 3->Recruiter
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


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None

    @validator("title")
    def title_validator(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Job Title cannot be empty or blank")
        return v

    @validator("description")
    def description_validator(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Job Description cannot be empty or blank")
        return v

    @validator("requirements")
    def requirement_validator(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Job Requirement cannot be empty or blank")
        return v


class ForgotPassword(BaseModel):
    email: str

    @validator("email")
    def email_validator(cls, v):
        if not v.strip():
            raise ValueError("Email cannot be empty")
        return v


class ResetUserPassword(BaseModel):
    ulid: str
    newPassword: str
    confirmPassword: str

    @validator("ulid")
    def fields_must_not_be_blank(cls, v):
        if not v.strip():
            raise ValueError(f"ulid cannot be empty or blank")
        return v

    @validator("newPassword")
    def new_password_validator(cls, v):
        if not v.strip():
            raise ValueError(f"new password cannot be empty or blank")

    @validator("confirmPassword")
    def passwords_must_match(cls, v, values):
        if "newPassword" in values and v != values["newPassword"]:
            raise ValueError("newPassword and confirmPassword must be equal")
        return v
