from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    userUlId = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String)
    is_recruiter = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    skills = Column(String)
    bio = Column(String)

    # Relationships
    jobs = relationship("Job", back_populates="recruiter")
    applications = relationship("JobApplication", back_populates="candidate")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    ulid = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(String)
    requirements = Column(String)
    recruiter_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    recruiter = relationship("User", back_populates="jobs")
    applications = relationship("JobApplication", back_populates="job")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    ulid = Column(String, unique=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    candidate_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")
    applied_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="applications")
    candidate = relationship("User", back_populates="applications")
