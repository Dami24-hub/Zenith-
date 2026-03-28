import requests
from bs4 import BeautifulSoup
import statistics
import re
import numpy as np
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Form, BackgroundTasks
import africastalking


# --- 0. CONFIGURATION ---
load_dotenv()
AT_USERNAME = os.getenv("AT_USERNAME", "sandbox")
AT_API_KEY = os.getenv("AT_API_KEY", "fake")
africastalking.initialize(AT_USERNAME, AT_API_KEY)
sms = africastalking.SMS
app = FastAPI()

@app.middleware("http")
async def log_exceptions(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        import traceback
        print(f"ERROR: Unhandled Exception during {request.url.path}")
        traceback.print_exc()
        raise e

# --- 1. DATA CONTRACT ---
class PropertyData(BaseModel):
    state: str = Field(description="State name (e.g. Lagos, Kaduna)")
    area: str = Field(description="Neighborhood (e.g. Barnawa, Ajah)")
    property_type: str = Field(description="Must be 'houses' or 'flats-apartments'")
    price: str = Field(description="Price string found in text")
    bedrooms: int = Field(description="Number of bedrooms")

# --- 2. THE IMPROVED UNBIASED SCRAPER ---
def get_market_avg(state, area, prop_type, beds):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    # NPC uses a specific slug format
    state_slug = state.lower().strip().replace(" ", "-")
    area_slug = area.lower().strip().replace(" ", "-")
    
    # Search hierarchy: Specific Area -> Broad State
    urls = [
        f"https://nigeriapropertycentre.com/for-sale/{prop_type}/{state_slug}/{area_slug}/results?beds={beds}",
        f"https://nigeriapropertycentre.com/for-sale/{prop_type}/{state_slug}/results?beds={beds}"
    ]
    
    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200: continue
            
            soup = BeautifulSoup(res.content, 'html.parser')
            raw_prices = [
                int(re.sub(r'[^\d]', '', p.text)) 
                for p in soup.select('.price') 
                if re.sub(r'[^\d]', '', p.text)
            ]
            
            if len(raw_prices) >= 3:
                # --- DYNAMIC OUTLIER REMOVAL (IQR) ---
                prices = sorted(raw_prices)
                q1, q3 = np.percentile(prices, [25, 75])
                iqr = q3 - q1
                
                # Using 1.0 multiplier to aggressively cut out commercial '900M' noise
                lower_bound = q1 - (1.0 * iqr)
                upper_bound = q3 + (1.0 * iqr)
                
                filtered = [p for p in prices if lower_bound <= p <= upper_bound]
                median = statistics.median(filtered)
                print(f"DEBUG: Found {len(filtered)} valid properties. Median: {median}")
                return median
            elif raw_prices:
                return statistics.median(raw_prices)
        except:
            continue
    return None

# --- 3. ROBUST PRICE CLEANER ---
def clean_price(val):
    if not val or val == "N/A": return 0
    clean = str(val).lower().replace(",", "")
    
    multiplier = 1
    if 'm' in clean: multiplier = 1_000_000
    elif 'k' in clean: multiplier = 1_000
    elif 'b' in clean: multiplier = 1_000_000_000
    
    num_part = re.sub(r'[^\d.]', '', clean)
    try:
        return int(float(num_part) * multiplier) if num_part else 0
    except:
        return 0

# --- 4. THE VERIFICATION ENGINE ---
def verify_listing(user_input):
    try:
        # 1. Initialize LLM (Ensure qwen2.5:3b is used)
        llm = ChatOllama(model="qwen2.5:3b", temperature=0, format="json")
        parser = JsonOutputParser(pydantic_object=PropertyData)

        prompt = ChatPromptTemplate.from_template(
            "Extract property details from the text into JSON. "
            "If a state isn't mentioned, infer it (e.g., Barnawa is in Kaduna). "
            "Input: {user_input}\n{format_instructions}"
        )
        
        chain = prompt | llm | parser
        data = chain.invoke({"user_input": user_input, "format_instructions": parser.get_format_instructions()})

        # --- SAFETY NETS ---
        # Instead of data['price'], use .get() to avoid KeyError
        price_str = data.get('price')
        if not price_str or price_str == "N/A":
            # Fallback: Try a simple regex to find the price if the AI missed it
            match = re.search(r'(\d+)\s*(m|k|million|billion)', user_input.lower())
            if match:
                price_str = match.group(0)
            else:
                return "Intelligence Error: AI could not find a price in your input."

        u_price = clean_price(price_str)
        # -------------------

        m_avg = get_market_avg(
            data.get('state', 'Kaduna'), 
            data.get('area', 'Barnawa'), 
            data.get('property_type', 'houses'), 
            data.get('bedrooms', 1)
        )
        
        if m_avg is None:
            return "Scraper Error: We couldn't find enough regional price data for this location. Please try a major neighborhood or check your spelling."

        # Comparison Logic
        diff = ((m_avg - u_price) / m_avg) * 100
        
        if diff >= 40: verdict = " SCAM ALERT (Suspiciously Low)"
        elif -20 <= diff <= 20: verdict = " REALISTIC MARKET VALUE"
        elif diff < -20: verdict = " OVERPRICED"
        else: verdict = " GOOD DEAL (Verify Carefully)"

        return (
            f"--- {data.get('area', 'AREA').upper()} ({data.get('state', 'STATE').upper()}) REPORT ---\n"
            f"Verdict: {verdict}\n"
            f"Your Price: ₦{u_price:,.0f}\n"
            f"Market Avg: ₦{m_avg:,.0f}\n"
            f"Deviation: {diff:.1f}% from regional average"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"System Crash: {str(e)}"

# --- 5. FASTAPI WEBHOOK ---
def process_sms(phone_number, text):
    """Background task to handle AI & Scraper logic"""
    try:
        print(f"DEBUG: Starting verification for {phone_number}...")
        report = verify_listing(text)
        print(f"DEBUG: Report generated:\n{report}")
        sms.send(report, [phone_number])
        print(f"DEBUG: Report sent to {phone_number}")
    except Exception as e:
        print(f"DEBUG: Support Error in background task: {str(e)}")
        sms.send(f"Support Error: {str(e)}", [phone_number])
        
@app.post("/sms-incoming")
async def handle_sms(background_tasks: BackgroundTasks, From: str = Form(..., alias="from"), text: str = Form(...)):
    print(f"DEBUG: Received SMS from {From}: {text}")
    
    # 1. Immediate acknowledgement
    try:
        sms.send("Verifying property listing... Please wait for the report.", [From])
    except Exception as e:
        print(f"DEBUG: Failed to send initial SMS ack: {e}")
    
    # 2. Process heavy logic in background
    background_tasks.add_task(process_sms, From, text)
    
    return {"status": "Processing"}

# --- EXECUTION ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

