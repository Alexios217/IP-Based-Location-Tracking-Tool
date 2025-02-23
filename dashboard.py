from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from database import SessionLocal, IPRecord

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency: Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    ip_records = db.query(IPRecord).all()
    suspicious_count = db.query(IPRecord).filter(IPRecord.suspicion_level == "Suspicious").count()
    safe_count = db.query(IPRecord).filter(IPRecord.suspicion_level == "Safe").count()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "ip_records": ip_records,
        "suspicious_count": suspicious_count,
        "safe_count": safe_count,
    })