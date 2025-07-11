from fastapi import FastAPI, status
from config.redis import redisStore
import models
from config.database import engine
from controllers import auth, recruiter, candidate

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def homeRoute():
    return {"status": True, "message": "Welcome to home Page!!"}


# defining routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(recruiter.router, prefix="/recruiter", tags=["Recruiter"])
app.include_router(candidate.router, prefix="/candidate", tags=["Candidate"])
