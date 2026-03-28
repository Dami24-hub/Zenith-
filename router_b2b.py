from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from valuation_service import ValuationService, ValuationStatus
from constants import PropertyType

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
    # Mapping bedrooms to property types for the engine
    prop_type = PropertyType.FLAT_1BR
    if request.bedrooms == 2: prop_type = PropertyType.FLAT_2BR
    elif request.bedrooms == 3: prop_type = PropertyType.FLAT_3BR
    elif request.bedrooms >= 4: prop_type = PropertyType.FLAT_4BR

    result = ValuationService.calculate_valuation(
        state=request.state,
        lga=request.town, # Using town as LGA for the demo
        property_type=prop_type,
        input_price=request.price
    )
    
    status = result["status"]
    
    if status == ValuationStatus.FAIR_MARKET_VALUE:
        # Create a signed token for the listing site
        payload = {
            "listing_id": request.listing_id,
            "verification_status": "ZENITH_VERIFIED",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return TrustBadgeResponse(verified=True, token=token, status=status.value)
    
    return TrustBadgeResponse(verified=False, status=status.value)
