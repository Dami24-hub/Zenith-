from fastapi import FastAPI, Request
from router_institution import router as institution_router
from router_sms import router as sms_router
from models import init_db
import uvicorn

app = FastAPI(title="Zenith: National Real Estate Valuation & Fraud API")

# Initialize Database
@app.on_event("startup")
def on_startup():
    init_db()

# Register Routers
app.include_router(institution_router)
app.include_router(sms_router)

@app.get("/")
async def root():
    return {"message": "Zenith API v1 is operational."}

from router_sms import sms_hook
@app.post("/sms")
@app.post("/v1/sms")
async def fallback_sms(request: Request):
    return await sms_hook(request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
