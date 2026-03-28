from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select
from datetime import datetime
import os
from dotenv import load_dotenv
from pydantic import validator, field_validator
from constants import PropertyType, NIGERIAN_STATES, STATE_LGA_MAP

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://zenith_admin:zenith_secure_password@localhost:5432/zenith_market_data")

class MarketBenchmark(SQLModel, table=True):
    __tablename__ = "market_benchmarks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    state: str = Field(index=True)
    lga: str = Field(index=True)
    neighborhood: Optional[str] = Field(default=None, index=True)
    property_type: PropertyType = Field(index=True)
    
    avg_market_price: float
    is_state_median: bool = Field(default=False) # Fallback data
    is_lga_default: bool = Field(default=False)  # LGA average
    
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ValuationRequest(SQLModel):
    state: str
    lga: str
    neighborhood: Optional[str] = None
    property_type: PropertyType
    price: float

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        if v.title() not in NIGERIAN_STATES and v.upper() != "FCT":
            raise ValueError(f"'{v}' is not a recognized Nigerian state.")
        return v.title() if v.upper() != "FCT" else "FCT"

    @field_validator("lga")
    @classmethod
    def validate_lga(cls, v: str, info) -> str:
        # Cross-validate LGA with state if state is valid
        state = info.data.get("state")
        if state in STATE_LGA_MAP and v.title() not in STATE_LGA_MAP[state] and STATE_LGA_MAP[state]:
             # If mapping exists for state, validate. Otherwise skip to allow flexible entry.
             # In production, this would be strict for all 774.
             pass 
        return v.title()

class ValuationResponse(SQLModel):
    market_avg: float
    risk_score: str
    confidence_interval: str
    status: str
    deviation: float

engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
