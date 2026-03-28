# 🌌 Zenith v2.0 — The Real Estate Truth Engine for Nigeria

> **National Infrastructure for Property Valuation and Fraud Detection.**

---

## 🚀 The Mission
**Zenith** provides a unified API Layer for the Nigerian real estate market. We detect valuation anomalies and provide 2026 Fair Market Value (FMV) benchmarks for all **36 States and the 774 LGAs** of Nigeria.

Zenith is the "Ground Truth" for Banks, Mortgage Firms, and PropTech portals.

---

## 🛠 Advanced Features

### 1. 3-Tier Geographical Hierarchy
*   **State -> LGA -> Neighborhood**: Resolves specific neighborhood prices.
*   **Fallback Intelligence**: If a neighborhood's specific data is missing, the AI automatically falls back to the **LGA Average** to ensure zero-downtime estimates.

### 2. Comprehensive Property Schema
Categorizes the entire Nigerian market:
*   **Apartments**: Self-contain, Mini-flat, 2BR/3BR/4BR Flats.
*   **Houses**: Terraces, Semi-Detached Duplexes, Fully Detached Duplexes, Bungalows.
*   **Luxury**: Penthouses, Maisonettes.

### 3. Advanced Fraud & Anomaly Detection
*   **Price-per-Unit Analysis**: Compares price-per-room vs. LGA benchmarks.
*   **Structural Anomaly**: Flags suspicious listings (e.g., a "Detached Duplex" priced lower than a "2BR Flat" in the same zone).

---

## 🏛 Institutional Integration (V1 API)

### Evaluate Deal
`POST /v1/evaluate`
```json
{
  "state": "Lagos",
  "lga": "Eti-Osa",
  "neighborhood": "Ikoyi",
  "property_type": "PENTHOUSE",
  "price": 950000000
}
```

### Market Trends & Reporting
`GET /v1/market-trends?state=Lagos&lga=Ikeja&property_type=FLAT_3BR`

---

## 📈 National Data Strategy
Our engine is powered by a multi-source ingestion layer:
1.  **Volume Ingestion**: Jiji.ng (bulk market data).
2.  **Verified Listings**: Nigeria Property Centre.
3.  **Inflation Modeling**: NBS 2026 housing inflation + 12-18% annual growth across Tier 1 to Tier 4 cities.

---

## 🛠 Setup & Deployment
1.  **Database Initialized**: Uses SQLite locally or external PostgreSQL. Ensure `nigeria_geo.sql` containing the 774 LGA structure is run or DB is pre-seeded.
2.  **Seed**: `python seed_data.py` to populate advanced 2026 benchmarks.

---
© 2026 Zenith Real Estate Tech. *National Trust, Local Truth.*
