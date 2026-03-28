from fastapi import APIRouter, HTTPException
from models import ValuationRequest, ValuationResponse
from valuation_service import ValuationService

router = APIRouter(prefix="/v1", tags=["Institutional"])

@router.post("/verify", response_model=ValuationResponse)
async def verify_property(request: ValuationRequest):
    """
    Institutional Tier: Verify property collateral with real-time benchmarking.
    """
    result = ValuationService.calculate_valuation(
        state=request.state,
        lga=request.lga,
        neighborhood=request.neighborhood,
        property_type=request.property_type,
        input_price=request.price
    )
    
    if result["status"] == "UNKNOWN_AREA":
        raise HTTPException(status_code=404, detail=result["message"])
        
    return ValuationResponse(
        market_avg=result["market_avg"],
        risk_score=result["risk_score"],
        confidence_interval=result["confidence_interval"],
        status=result["status"].value,
        deviation=result["deviation"]
    )
