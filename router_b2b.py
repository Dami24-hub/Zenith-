from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from valuation_service import ValuationService, ValuationStatus

router = APIRouter(prefix="/b2b", tags=["B2B Integration"])

SECRET_KEY = os.getenv("SECRET_KEY", "zenith_secret_token_2026")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

class TrustBadgeRequest(BaseModel):
    listing_id: str
    state: str
    town: str
    bedrooms: int
    price: float

class TrustBadgeResponse(BaseModel):
    verified: bool
    token: Optional[str] = None
    status: str

@router.post("/trust-badge", response_model=TrustBadgeResponse)
async def get_trust_badge(request: TrustBadgeRequest):
    status, message, avg = ValuationService.calculate_fmv(
        request.state, request.town, request.bedrooms, request.price
    )
    
    if status == ValuationStatus.FAIR_MARKET:
        # Create a signed token for the listing site
        payload = {
            "listing_id": request.listing_id,
            "verification_status": "ZENITH_VERIFIED",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return TrustBadgeResponse(verified=True, token=token, status=status.value)
    
    return TrustBadgeResponse(verified=False, status=status.value)
