from models import MarketBenchmark, engine, init_db
from sqlmodel import Session
from constants import PropertyType

def seed_benchmarks():
    init_db()
    
    # 2026 Advanced Benchmarks for Zenith
    benchmarks = [
        # Lagos - Eti-Osa
        MarketBenchmark(state="Lagos", lga="Eti-Osa", neighborhood="Ikoyi", property_type=PropertyType.PENTHOUSE, avg_market_price=950_000_000),
        MarketBenchmark(state="Lagos", lga="Eti-Osa", neighborhood="Lekki Phase 1", property_type=PropertyType.FLAT_3BR, avg_market_price=220_000_000),
        MarketBenchmark(state="Lagos", lga="Eti-Osa", property_type=PropertyType.FLAT_3BR, avg_market_price=180_000_000, is_lga_default=True),
        MarketBenchmark(state="Lagos", lga="Eti-Osa", property_type=PropertyType.FULLY_DET_DUPLEX, avg_market_price=450_000_000, is_lga_default=True),
        
        # Abuja
        MarketBenchmark(state="FCT", lga="Abuja Municipal", neighborhood="Maitama", property_type=PropertyType.FULLY_DET_DUPLEX, avg_market_price=850_000_000),
        MarketBenchmark(state="FCT", lga="Abuja Municipal", property_type=PropertyType.FULLY_DET_DUPLEX, avg_market_price=650_000_000, is_lga_default=True),
        
        # Kaduna
        MarketBenchmark(state="Kaduna", lga="Chikun", property_type=PropertyType.BUNGALOW, avg_market_price=45_000_000, is_lga_default=True),
        
        # State Medians (Fallback Tier 3)
        MarketBenchmark(state="Lagos", property_type=PropertyType.FLAT_3BR, avg_market_price=120_000_000, is_state_median=True, lga="State"),
        MarketBenchmark(state="FCT", property_type=PropertyType.FULLY_DET_DUPLEX, avg_market_price=400_000_000, is_state_median=True, lga="State"),
    ]

    with Session(engine) as session:
        # Check if table exists before deleting (avoids error on first run in SQLite)
        try:
            session.exec("DELETE FROM market_benchmarks")
        except Exception:
            # Table might not exist yet if init_db failed or metadata is out of sync
            pass
        for benchmark in benchmarks:
            session.add(benchmark)
        session.commit()
    print("Zenith Database Seeded Specifically for 2026.")

if __name__ == "__main__":
    seed_benchmarks()
