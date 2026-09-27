from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
import secrets
from datetime import datetime, timedelta, timezone

router = APIRouter()

JWT_SECRET = "bank-demo-secret-key"
JWT_ALGORITHM = "HS256"

CLIENT_ID = "FINTECH001"
CLIENT_SECRET = "FINTECH001_SECRET"

authorization_codes = {}

class TokenRequest(BaseModel):
    code: str
    client_id: str
    client_secret: str

@router.get("/authorize")
def authorize(
    client_id: str,
    scope: str,
    consent: bool = False
):
    if client_id != CLIENT_ID:
        raise HTTPException(
            status_code=400,
            detail="Unknown client"
        )

    if not consent:
        return {
            "message": "User consent required",
            "requested_scope": scope,
            "instruction": "Call this endpoint again with consent=true"
        }

    code = secrets.token_urlsafe(16)

    authorization_codes[code] = {
        "client_id": client_id,
        "scope": scope
    }

    return {
        "message": "User consent granted",
        "authorization_code": code
    }

@router.post("/token")
def token(request: TokenRequest):

    if request.client_id != CLIENT_ID:
        raise HTTPException(
            status_code=401,
            detail="Invalid client ID"
        )

    if request.client_secret != CLIENT_SECRET:
        raise HTTPException(
            status_code=401,
            detail="Invalid client secret"
        )

    if request.code not in authorization_codes:
        raise HTTPException(
            status_code=400,
            detail="Invalid authorization code"
        )

    data = authorization_codes.pop(request.code)

    now = datetime.now(timezone.utc)

    payload = {
        "sub": "USER001",
        "client_id": data["client_id"],
        "scope": data["scope"],
        "iss": "bank-auth-server",
        "aud": "bank-api",
        "iat": now,
        "exp": now + timedelta(minutes=15),
        "jti": secrets.token_urlsafe(12)
    }

    access_token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return {
        "token_type": "Bearer",
        "access_token": access_token,
        "expires_in": 900,
        "scope": data["scope"]
    }