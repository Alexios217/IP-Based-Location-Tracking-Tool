# IP-Based-Location-Tracking-Tool
IP-Based Location Tracking Tool designed for law enforcement and cybersecurity purposes

# IP-Based Location Tracking Tool

## Introduction
This project is an **IP-Based Location Tracking Tool** designed for **law enforcement and cybersecurity purposes**. It provides real-time tracking of IP addresses, determines their risk levels using machine learning, and triggers alerts for suspicious activity.

## Features
- **Real-time IP tracking** using FastAPI.
- **Machine Learning-based fraud detection**.
- **Database storage** of tracked IPs with timestamps.
- **Web dashboard** for monitoring and filtering IP addresses.
- **Automated alerts** via email, SMS (Twilio), and webhook notifications.
- **WebSocket integration** for real-time updates.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** HTML, JavaScript, WebSocket
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Machine Learning:** Scikit-learn (Joblib)
- **External APIs:**
  - [IPInfo.io](https://ipinfo.io/) (IP Geolocation)
  - [IPQualityScore](https://www.ipqualityscore.com/) (Fraud Detection)
  - Twilio (SMS alerts)
  - SMTP (Email alerts)

## System Architecture
1. **User sends an IP address query.**
2. **FastAPI fetches data** from IPInfo and IPQualityScore APIs.
3. **ML model analyzes the risk score** and classifies the IP as Safe or Suspicious.
4. **IP details are stored in the database.**
5. **Real-time alerts are triggered** (email, SMS, webhook) if an IP is marked suspicious.
6. **Dashboard displays tracked IPs** with filters and timestamps.

## Installation & Setup
### 1. Clone the Repository
```sh
git clone https://github.com/your-repo/ip-tracker.git
cd ip-tracker
```

### 2. Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Set Up Database
Modify `database.py` with your PostgreSQL credentials and run:
```sh
alembic upgrade head
```

### 5. Run the Server
```sh
uvicorn main:app --reload
```

### 6. Access the Web Dashboard
Open `http://127.0.0.1:8000/dashboard` in your browser.

## API Endpoints
### **Track an IP**
**GET /track/{ip_address}**
#### Response:
```json
{
  "ip": "8.8.8.8",
  "city": "Mountain View",
  "region": "California",
  "country": "US",
  "vpn": false,
  "tor": false,
  "fraud_score": 5,
  "bot_status": false,
  "suspicion_level": "Safe",
  "tracked_at": "2025-02-23T12:00:00Z"
}
```

### **Get Tracked IPs**
**GET /tracked_ips**
#### Response:
```json
[
  {"ip": "192.168.1.1", "tracked_at": "2025-02-23T11:45:00Z"},
  {"ip": "8.8.8.8", "tracked_at": "2025-02-23T12:00:00Z"}
]
```

## Real-Time Alerts
- **WebSockets** are used to push real-time updates to the dashboard.
- **Email Alerts:** Sent when a suspicious IP is detected.
- **SMS Alerts:** Uses Twilio for instant mobile notifications.
- **Webhook Alerts:** Can notify external services like Slack or Discord.

## Future Enhancements
- **Advanced filtering** (blacklist, known bad IPs)
- **User authentication** for restricted access
- **Export data** to CSV or JSON for analysis
- **Integration with AI models** for anomaly detection

## License
This project is open-source and licensed under the MIT License.

