"""
SQLAlchemy models for the application
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from app.database import Base


class Correo(Base):
    """Model for storing email contacts"""
    __tablename__ = "correos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(20), index=True)
    razon_social = Column(String(255))
    tipo_tercero = Column(String(100))
    numero_identificacion = Column(String(50))
    email = Column(String(255), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Correo(id={self.id}, email='{self.email}', razon_social='{self.razon_social}')>"


class EmailLog(Base):
    """Model for logging sent emails"""
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    correo_id = Column(Integer, index=True)
    email = Column(String(255), index=True)
    subject = Column(String(500))
    body = Column(Text)
    status = Column(String(20), default="pending")  # pending, sent, failed
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<EmailLog(id={self.id}, email='{self.email}', status='{self.status}')>"


class EmailCampaign(Base):
    """Model for email campaigns"""
    __tablename__ = "email_campaigns"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))
    subject = Column(String(500))
    body = Column(Text)
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    status = Column(String(20), default="draft")  # draft, sending, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<EmailCampaign(id={self.id}, name='{self.name}', status='{self.status}')>"