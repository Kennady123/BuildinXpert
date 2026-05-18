from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from twilio.rest import Client
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz

app = FastAPI(
    docs_url=None,
    redoc_url=None
)
load_dotenv()
# Allow your website to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # After deploying, replace * with your actual website URL
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Twilio credentials — stored safely as environment variables on Render
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WA_NUMBER   = "whatsapp:+14155238886"

RECIPIENTS = [
    "whatsapp:+919710908050",
    "whatsapp:+918838143348",
    "whatsapp:+919360605902",
]

# Form data model
class EnquiryForm(BaseModel):
    name: str
    phone: str
    area: str = "Not specified"
    service: str
    message: str = "No additional details"

@app.post("/send-enquiry")
async def send_enquiry(form: EnquiryForm):
    if not form.name or not form.phone or not form.service:
        raise HTTPException(status_code=400, detail="Name, phone, and service are required.")

    # Format WhatsApp message
    ist = pytz.timezone("Asia/Kolkata")
    time_now = datetime.now(ist).strftime("%d %b %Y, %I:%M %p")

    text = f"""🔔 New Enquiry — Building Xpert

👤 Name: {form.name}
📞 Phone: {form.phone}
📍 Area: {form.area}
🛠 Service: {form.service}
💬 Details: {form.message}

⏰ {time_now}"""

    # Send to all recipients via Twilio
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    errors = []
    for recipient in RECIPIENTS:
        try:
            client.messages.create(
                from_=TWILIO_WA_NUMBER,
                to=recipient,
                body=text
            )
        except Exception as e:
            errors.append(str(e))

    if len(errors) == len(RECIPIENTS):
        raise HTTPException(status_code=500, detail="Failed to send WhatsApp messages.")

    return {"success": True, "message": "Enquiry sent successfully!"}

@app.get("/")
def root():
    return {"status": "Building Xpert Backend Running ✅"}
