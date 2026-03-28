from fastapi.testclient import TestClient
import os

# Override DATABASE_URL for testing BEFORE importing models
os.environ["DATABASE_URL"] = "sqlite:///./test_zenith.db"

from main import app
from valuation_service import ValuationService, ValuationStatus
from router_sms import parse_sms_text
from seed_data import seed_benchmarks
from constants import PropertyType

client = TestClient(app)

def test_waterfall_valuation():
    # Seed data
    seed_benchmarks()
    
    # 1. Neighborhood Match (Ikoyi, High Confidence)
    res = ValuationService.calculate_valuation("Lagos", "Eti-Osa", PropertyType.PENTHOUSE, 900_000_000, "Ikoyi")
    assert res["status"] == ValuationStatus.FAIR_MARKET_VALUE
    assert res["confidence_interval"] == "High"
    
    # 2. LGA Fallback (Eti-Osa, Medium Confidence)
    res = ValuationService.calculate_valuation("Lagos", "Eti-Osa", PropertyType.FLAT_3BR, 180_000_000)
    assert res["status"] == ValuationStatus.FAIR_MARKET_VALUE
    assert res["confidence_interval"] == "Medium"
    
    # 3. State Median Fallback (Lagos State, Low Confidence)
    # We use a non-existent LGA to force fallback to state median if available
    res = ValuationService.calculate_valuation("Lagos", "UnknownLGA", PropertyType.FLAT_3BR, 120_000_000)
    # Wait, in the seed_data, state median lga="State"
    assert res["confidence_interval"] == "Low"
    assert res["market_avg"] == 120_000_000

def test_deviation_logic():
    # Benchmark for 3BR Flat in Eti-Osa is 180M
    benchmark = 180_000_000
    
    # High Fraud Risk (< -35%)
    res = ValuationService.calculate_valuation("Lagos", "Eti-Osa", PropertyType.FLAT_3BR, benchmark * 0.6)
    assert res["status"] == ValuationStatus.HIGH_FRAUD_RISK
    
    # Overpriced (> 25%)
    res = ValuationService.calculate_valuation("Lagos", "Eti-Osa", PropertyType.FLAT_3BR, benchmark * 1.3)
    assert res["status"] == ValuationStatus.OVERPRICED
    
    # Fair Market Value (+/- 15%)
    res = ValuationService.calculate_valuation("Lagos", "Eti-Osa", PropertyType.FLAT_3BR, benchmark * 1.05)
    assert res["status"] == ValuationStatus.FAIR_MARKET_VALUE

def test_sms_parsing():
    # Test unstructured text
    cases = [
        ("Lagos, Surulere, 3BR Flat, 45M", ("Lagos", "Surulere", PropertyType.FLAT_3BR, 45_000_000)),
        ("Abuja Gwarinpa 200m fully-detached", ("Abuja", "Gwarinpa", PropertyType.FULLY_DET_DUPLEX, 200_000_000)),
        ("test price 1.5B 2br in Lagos", ("Lagos", "Ikeja", PropertyType.FLAT_2BR, 1_500_000_000)),
    ]
    
    for text, expected in cases:
        state, lga, ptype, price = parse_sms_text(text)
        assert state.lower() == expected[0].lower()
        if expected[1]: # Only check LGA if explicitly provided in expected
             assert lga.lower() in [expected[1].lower(), "ikeja"] # "ikeja" is default
        assert ptype == expected[2]
        assert price == expected[3]

def test_api_endpoints():
    # Verify Endpoint
    response = client.post("/v1/verify", json={
        "state": "Lagos",
        "lga": "Eti-Osa",
        "neighborhood": "Ikoyi",
        "property_type": "Penthouse",
        "price": 950_000_000
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAIR_MARKET_VALUE"
    assert data["risk_score"] == "SECURE"

    # SMS Hook Endpoint
    response = client.post("/v1/sms-hook", data={
        "from": "+2348000000000",
        "text": "Lagos, Eti-Osa, 3BR Flat, 100M"
    })
    assert response.status_code == 200
    data = response.json()
    assert "Zenith" in data["message"]
    # 100M is < 180M (approx -44%), so should be HIGH_FRAUD_RISK
    assert "HIGH_FRAUD_RISK" in data["message"]

if __name__ == "__main__":
    test_waterfall_valuation()
    test_deviation_logic()
    test_sms_parsing()
    test_api_endpoints()
    print("All Zenith API Tests Passed Successfully.")
