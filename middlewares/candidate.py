from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Header, status
import models
from config.database import get_db
from utils.token import verifyCandidateToken


def get_current_candidate(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    # Verify the token
    token_result = verifyCandidateToken(token)
    if not token_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=token_result["error"]
        )

    # Get user from database
    user_id = token_result["data"]["userUlId"]
    user = db.query(models.User).filter(models.User.userUlId == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if user.role_id != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Recruiter role required",
        )

    return user
