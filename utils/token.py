import jwt
from datetime import datetime, timedelta
from jwt import ExpiredSignatureError, InvalidTokenError

from config.settings import CANDIDATE_TOKEN, EXPIRY_MINUTES, RECRUITER_TOKEN

ALGORITHM = "HS256"


def createRecruiterToken(userUlId: str) -> str:
    expiry_minutes = int(EXPIRY_MINUTES) if EXPIRY_MINUTES is not None else 0
    payload = {
        "userUlId": userUlId,
        "exp": datetime.utcnow() + timedelta(minutes=expiry_minutes),
    }
    return jwt.encode(payload, RECRUITER_TOKEN, algorithm=ALGORITHM)


def verifyRecruiterToken(token: str) -> dict:
    try:
        decoded = jwt.decode(token, RECRUITER_TOKEN, algorithms=[ALGORITHM])
        return {"valid": True, "data": decoded}
    except ExpiredSignatureError:
        return {"valid": False, "error": "Token has expired"}
    except InvalidTokenError:
        return {"valid": False, "error": "Invalid token"}


def createCandidateToken(userUlId: str) -> str:
    expiry_minutes = int(EXPIRY_MINUTES) if EXPIRY_MINUTES is not None else 0
    payload = {
        "userUlId": userUlId,
        "exp": datetime.utcnow() + timedelta(minutes=expiry_minutes),
    }
    return jwt.encode(payload, CANDIDATE_TOKEN, algorithm=ALGORITHM)


def verifyCandidateToken(token: str) -> dict:
    try:
        decoded = jwt.decode(token, CANDIDATE_TOKEN, algorithms=[ALGORITHM])
        return {"valid": True, "data": decoded}
    except ExpiredSignatureError:
        return {"valid": False, "error": "Token has expired"}
    except InvalidTokenError:
        return {"valid": False, "error": "Invalid token"}
