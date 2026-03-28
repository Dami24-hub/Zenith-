from enum import Enum
from typing import Tuple, Optional, Dict, Any
from models import MarketBenchmark, engine
from sqlmodel import Session, select
from constants import (
    PropertyType, 
    DEVIATION_HIGH_FRAUD, 
    DEVIATION_OVERPRICED, 
    DEVIATION_FAIR_MIN, 
    DEVIATION_FAIR_MAX
)

class ValuationStatus(str, Enum):
    HIGH_FRAUD_RISK = "HIGH_FRAUD_RISK"
    OVERPRICED = "OVERPRICED"
    FAIR_MARKET_VALUE = "FAIR_MARKET_VALUE"
    MARKET_ADJACENT = "MARKET_ADJACENT"
    UNKNOWN_AREA = "UNKNOWN_AREA"

class ValuationService:
    @staticmethod
    def calculate_valuation(
        state: str, 
        lga: str, 
        property_type: PropertyType, 
        input_price: float,
        neighborhood: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Zenith Waterfall Valuation Engine:
        1. Neighborhood Match
        2. LGA Fallback
        3. State/Property-Type Median Fallback
        """
        with Session(engine) as session:
            benchmark = None
            confidence = "High"

            # 1. Neighborhood Lookup
            if neighborhood:
                stmt = select(MarketBenchmark).where(
                    MarketBenchmark.state.ilike(state),
                    MarketBenchmark.lga.ilike(lga),
                    MarketBenchmark.neighborhood.ilike(neighborhood),
                    MarketBenchmark.property_type == property_type
                )
                benchmark = session.exec(stmt).first()

            # 2. LGA Fallback
            if not benchmark:
                confidence = "Medium"
                stmt = select(MarketBenchmark).where(
                    MarketBenchmark.state.ilike(state),
                    MarketBenchmark.lga.ilike(lga),
                    MarketBenchmark.property_type == property_type,
                    MarketBenchmark.is_lga_default == True
                )
                benchmark = session.exec(stmt).first()

            # 3. State Median Fallback
            if not benchmark:
                confidence = "Low"
                stmt = select(MarketBenchmark).where(
                    MarketBenchmark.state.ilike(state),
                    MarketBenchmark.property_type == property_type,
                    MarketBenchmark.is_state_median == True
                )
                benchmark = session.exec(stmt).first()

            if not benchmark:
                return {
                    "status": ValuationStatus.UNKNOWN_AREA,
                    "market_avg": 0.0,
                    "deviation": 0.0,
                    "risk_score": "UNCERTAIN",
                    "confidence_interval": "None",
                    "message": f"No market benchmarks available for {property_type} in {lga}, {state}."
                }

            benchmark_price = benchmark.avg_market_price
            deviation = (input_price - benchmark_price) / benchmark_price

            # Anomaly Detection Logic
            if deviation < DEVIATION_HIGH_FRAUD:
                status = ValuationStatus.HIGH_FRAUD_RISK
                risk_score = "VULNERABLE"
            elif deviation > DEVIATION_OVERPRICED:
                status = ValuationStatus.OVERPRICED
                risk_score = "LOW_RISK"
            elif DEVIATION_FAIR_MIN <= deviation <= DEVIATION_FAIR_MAX:
                status = ValuationStatus.FAIR_MARKET_VALUE
                risk_score = "SECURE"
            else:
                status = ValuationStatus.MARKET_ADJACENT
                risk_score = "NORMAL"

            return {
                "status": status,
                "market_avg": benchmark_price,
                "deviation": deviation,
                "risk_score": risk_score,
                "confidence_interval": confidence,
                "message": f"Analysis complete. Deviation: {deviation:.1%}"
            }
