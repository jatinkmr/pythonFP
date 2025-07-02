import jwt
from datetime import datetime, timedelta
from jwt import ExpiredSignatureError, InvalidTokenError

from config.settings import CANDIDATE_TOKEN, EXPIRY_MINUTES, RECRUITER_TOKEN
from config.redis import redisStore

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
        # Check if token is blacklisted
        if isTokenBlacklisted(token):
            return {"valid": False, "error": "Token has been revoked"}

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
        # Check if token is blacklisted
        if isTokenBlacklisted(token):
            return {"valid": False, "error": "Token has been revoked"}

        decoded = jwt.decode(token, CANDIDATE_TOKEN, algorithms=[ALGORITHM])
        return {"valid": True, "data": decoded}
    except ExpiredSignatureError:
        return {"valid": False, "error": "Token has expired"}
    except InvalidTokenError:
        return {"valid": False, "error": "Invalid token"}


def blacklistToken(token: str) -> bool:
    """
    Add a token to the blacklist in Redis.
    The token will be stored until its natural expiration time.
    """
    try:
        # Decode the token to get expiration time (without verification)
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp_timestamp = decoded.get("exp")

        if exp_timestamp:
            # Calculate TTL (time to live) until token naturally expires
            current_timestamp = datetime.utcnow().timestamp()
            ttl_seconds = int(exp_timestamp - current_timestamp)

            # Only blacklist if token hasn't already expired
            if ttl_seconds > 0:
                # Store token in Redis with TTL
                redisStore.set(f"blacklist:{token}", "revoked", ttl_seconds)
                return True
            else:
                # Token is already expired, no need to blacklist
                return False

        return False
    except Exception as e:
        print(f"Error blacklisting token: {str(e)}")
        return False


def isTokenBlacklisted(token: str) -> bool:
    """
    Check if a token is in the blacklist.
    """
    try:
        result = redisStore.get(f"blacklist:{token}")
        return result is not None
    except Exception as e:
        print(f"Error checking token blacklist: {str(e)}")
        return False
