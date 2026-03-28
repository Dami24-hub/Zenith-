import os
from dotenv import load_dotenv
import africastalking

load_dotenv()
AT_USERNAME = os.getenv("AT_USERNAME", "sandbox")
AT_API_KEY = os.getenv("AT_API_KEY")

print(f"Testing AT with Username: {AT_USERNAME}")
print(f"API Key (first 5): {AT_API_KEY[:5] if AT_API_KEY else 'NONE'}")

try:
    africastalking.initialize(AT_USERNAME, AT_API_KEY)
    sms = africastalking.SMS
    print("Successfully initialized AT")
except Exception as e:
    print(f"Initialization Failed: {e}")
