from fastapi import APIRouter, Request, Form
from valuation_service import ValuationService, ValuationStatus
from constants import PropertyType
import re
import os
import subprocess

# Configuration for Africa's Talking
AT_USERNAME = os.getenv("AT_USERNAME", "sandbox")
AT_API_KEY = os.getenv("AT_API_KEY", "your_sandbox_api_key_here")

router = APIRouter(prefix="/v1", tags=["SMS"])

def parse_sms_text(text: str):
    """
    Robust Regex Parser for Zenith SMS Hook.
    Extracts: (State, LGA, Type, Price)
    Example: "Lagos, Surulere, 3BR Flat, 45M"
    """
    # 1. Extract Price (e.g. 45M, 200m, 1.5B)
    # Exclude cases where the number is followed by 'BR' (Bedrooms)
    # \b ensures we match word boundaries, (?i) inline for ignore case (handled by flag)
    price_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(m|k|b|million|billion)\b', text, re.IGNORECASE)
    price = 0.0
    if price_match:
        val = float(price_match.group(1))
        unit = (price_match.group(2) or "").lower()
        if unit in ['m', 'million']:
            price = val * 1_000_000
        elif unit in ['b', 'billion']:
            price = val * 1_000_000_000
        elif unit in ['k']:
            price = val * 1_000
        else:
            price = val
    else:
        # Fallback: look for a large raw number like 45000000
        large_num_match = re.search(r'\b(\d{6,})\b', text.replace(',', ''))
        if large_num_match:
            price = float(large_num_match.group(1))

    # 2. Extract Property Type
    # Simple mapping for common SMS terms to PropertyType Enum
    type_map = {
        r"self-?contain": PropertyType.SELF_CONTAIN,
        r"mini-?flat": PropertyType.MINI_FLAT,
        r"1br": PropertyType.FLAT_1BR,
        r"2br": PropertyType.FLAT_2BR,
        r"3br": PropertyType.FLAT_3BR,
        r"4br": PropertyType.FLAT_4BR,
        r"terrace": PropertyType.TERRACE_DUPLEX,
        r"semi-?detached": PropertyType.SEMI_DET_DUPLEX,
        r"fully-?detached": PropertyType.FULLY_DET_DUPLEX,
        r"bungalow": PropertyType.BUNGALOW,
        r"penthouse": PropertyType.PENTHOUSE
    }
    
    prop_type = PropertyType.FLAT_3BR # Default
    for pattern, enum_val in type_map.items():
        if re.search(pattern, text, re.IGNORECASE):
            prop_type = enum_val
            break

    # 3. Extract Geographic (State, LGA)
    # Using comma split as a primary divider, then fallback to keywords
    parts = [p.strip() for p in text.split(",")]
    state = "Lagos" # Defaults
    lga = "Ikeja"
    
    if len(parts) >= 2:
        state = parts[0]
        lga = parts[1]
    else:
        # Fallback keyword search for major states
        states_regex = r"(Lagos|FCT|Abuja|Rivers|Oyo|Kano|Kaduna)"
        state_match = re.search(states_regex, text, re.IGNORECASE)
        if state_match:
            state = state_match.group(1)

    return state, lga, prop_type, price

@router.post("/sms-hook")
async def sms_hook(request: Request):
    """
    Africa's Talking Webhook for Zenith.
    POST /v1/sms-hook (form-data: from, to, text)
    """
    form_data = await request.form()
    text = form_data.get("text", "")
    sender = form_data.get("from", "")
    our_shortcode = form_data.get("to", "")

    state, lga, prop_type, price = parse_sms_text(text)
    
    result = ValuationService.calculate_valuation(
        state=state,
        lga=lga,
        property_type=prop_type,
        input_price=price
    )
    
    # Zenith SMS Verdict Formatting (Max 160 chars)
    if result["status"] == ValuationStatus.UNKNOWN_AREA:
        response_msg = f"Zenith Error: No data for {lga}, {state}."
    else:
        status = result["status"].value
        avg = result["market_avg"]
        risk = result["risk_score"]
        dev = result["deviation"]
        
        response_msg = (
            f"Zenith Zenith: {status}\n"
            f"Market Avg: \u20a6{avg/1e6:,.1f}M\n"
            f"Risk: {risk} ({dev:+.0%})"
        )

    # Send the SMS reply using cURL to bypass Python's strict SSL WRONG_VERSION_NUMBER bug
    at_status = 0
    at_text = ""
    try:
        url = "https://api.sandbox.africastalking.com/version1/messaging"
        cmd = [
            "curl", "-s", "-X", "POST", url,
            "-H", "Accept: application/json",
            "-H", "Content-Type: application/x-www-form-urlencoded",
            "-H", f"apiKey: {AT_API_KEY}",
            "--data-urlencode", f"username={AT_USERNAME}",
            "--data-urlencode", f"to={sender}",
            "--data-urlencode", f"message={response_msg}",
            "--data-urlencode", f"from={our_shortcode}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        at_status = 200 if result.returncode == 0 else 500
        at_text = result.stdout
        print(f"AT Response: {at_text}")
            
    except Exception as e:
        at_status = 500
        at_text = str(e)
        print(f"AT SMS Error: {e}")

    return {"message": response_msg, "to": sender, "at_status": at_status, "at_text": at_text}
