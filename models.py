from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}  # Add this line

    id = Column(Integer, primary_key=True, index=True)
    userUlId = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String)
    role_id = Column(Integer, default=2)  # 1->Admin, 2->Candidate, 3->Recruiter
    created_at = Column(DateTime, default=datetime.utcnow)
    skills = Column(String)
    bio = Column(String)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {"schema": "public"}  # Add this line

    id = Column(Integer, primary_key=True, index=True)
    ulid = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    requirements = Column(Text)
    recruiter_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    # recruiter = relationship("User", back_populates="jobs")
    # applications = relationship("JobApplication", back_populates="job")


class JobApplication(Base):
    __tablename__ = "job_applications"
    __table_args__ = {"schema": "public"}  # Add this line

    id = Column(Integer, primary_key=True, index=True)
    ulid = Column(String, index=True)
    job_id = Column(Integer)
    candidate_id = Column(Integer)
    status = Column(String, default="pending")
    applied_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    # job = relationship("Job", back_populates="applications")
    # candidate = relationship("User", back_populates="applications")


# Add back_populates to User model
# User.jobs = relationship("Job", back_populates="recruiter")
# User.applications = relationship("JobApplication", back_populates="candidate")
