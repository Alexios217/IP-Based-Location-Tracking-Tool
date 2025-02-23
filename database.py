from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# PostgreSQL Connection (Replace with actual credentials)
DATABASE_URL = "postgresql://user:password@localhost/ip_tracking"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# IP Tracking Model
class IPRecord(Base):
    __tablename__ = "ip_records"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, index=True)
    city = Column(String)
    region = Column(String)
    country = Column(String)
    location = Column(String)
    org = Column(String)
    vpn = Column(Boolean)
    tor = Column(Boolean)
    fraud_score = Column(Integer)
    recent_abuse = Column(Boolean)
    bot_status = Column(Boolean)
    suspicion_level = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Initialize database
init_db()
