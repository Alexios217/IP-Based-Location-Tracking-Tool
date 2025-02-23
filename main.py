from datetime import datetime, timezone
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
import httpx
import joblib
import numpy as np
import smtplib
import json
from email.message import EmailMessage
from twilio.rest import Client
from sqlalchemy.orm import Session
from database import SessionLocal, IPRecord
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI()

# API Endpoints
GEO_API_URL = "https://ipinfo.io/{}/json"
VPN_CHECK_URL = "https://www.ipqualityscore.com/api/json/ip/{}?key={}"
IPQS_API_KEY = os.getenv("IPQS_API_KEY")

# Load ML model & scaler
model = joblib.load("ip_model.pkl")
scaler = joblib.load("scaler.pkl")

# Email configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
ALERT_PHONE_NUMBER = os.getenv("ALERT_PHONE_NUMBER")

# WebSocket connections
active_connections = set()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dependency: Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def fetch_data(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

def send_email_alert(ip_data):
    msg = EmailMessage()
    msg["Subject"] = f"🚨 Suspicious IP Detected: {ip_data['ip']}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg.set_content(f"""
    Suspicious IP Alert!
    
    IP Address: {ip_data['ip']}
    Location: {ip_data['city']}, {ip_data['region']}, {ip_data['country']}
    VPN: {ip_data['vpn']}
    Tor: {ip_data['tor']}
    Fraud Score: {ip_data['fraud_score']}
    Bot Activity: {ip_data['bot_status']}
    """)
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")

def send_sms_alert(ip_data):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"🚨 Suspicious IP Detected: {ip_data['ip']} (Fraud Score: {ip_data['fraud_score']})",
        from_=TWILIO_PHONE_NUMBER,
        to=ALERT_PHONE_NUMBER,
    )
    logger.info(f"SMS Sent: {message.sid}")

async def send_ip_alert(ip_address: str, timestamp: datetime):
    """Send real-time alert to connected WebSocket clients."""
    for connection in active_connections:
        await connection.send_text(json.dumps({"ip": ip_address, "tracked_at": timestamp.isoformat()}))

def store_ip_data(db: Session, ip_data: dict):
    """Store tracked IP and trigger real-time alert."""
    try:
        ip_data["tracked_at"] = datetime.now(timezone.utc)
        db_record = IPRecord(**ip_data)
        db.add(db_record)
        db.commit()
        import asyncio
        asyncio.create_task(send_ip_alert(ip_data["ip"], ip_data["tracked_at"]))
    except Exception as e:
        logger.error(f"Database Error: {e}")

@app.get("/track/{ip_address}")
async def track_ip(ip_address: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        geo_data = await fetch_data(GEO_API_URL.format(ip_address))
        if "bogon" in geo_data:
            raise HTTPException(status_code=400, detail="Invalid IP address")
        
        vpn_data = await fetch_data(VPN_CHECK_URL.format(ip_address, IPQS_API_KEY))
        
        features = np.array([[
            vpn_data.get("fraud_score", 0),
            int(vpn_data.get("vpn", False)),
            int(vpn_data.get("tor", False)),
            int(vpn_data.get("recent_abuse", False)),
            int(vpn_data.get("bot_status", False)),
        ]])
        
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        suspicion_level = "Suspicious" if prediction == 1 else "Safe"
        
        ip_data = {
            "ip": geo_data.get("ip"),
            "city": geo_data.get("city"),
            "region": geo_data.get("region"),
            "country": geo_data.get("country"),
            "vpn": vpn_data.get("vpn"),
            "tor": vpn_data.get("tor"),
            "fraud_score": vpn_data.get("fraud_score"),
            "recent_abuse": vpn_data.get("recent_abuse"),
            "bot_status": vpn_data.get("bot_status"),
            "suspicion_level": suspicion_level,
        }
        
        logger.info(f"Tracked IP: {ip_data}")
        background_tasks.add_task(store_ip_data, db, ip_data)
        
        if prediction == 1:
            background_tasks.add_task(send_email_alert, ip_data)
            background_tasks.add_task(send_sms_alert, ip_data)
        
        return ip_data
    except Exception as e:
        logger.error(f"Error tracking IP: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")