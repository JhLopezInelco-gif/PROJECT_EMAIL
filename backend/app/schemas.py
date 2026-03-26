"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
import re


# Correo Schemas
class CorreoBase(BaseModel):
    """Base schema for Correo"""
    codigo: Optional[str] = None
    razon_social: Optional[str] = None
    tipo_tercero: Optional[str] = None
    numero_identificacion: Optional[str] = None
    email: str
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()


class CorreoCreate(CorreoBase):
    """Schema for creating a new Correo"""
    pass


class CorreoUpdate(BaseModel):
    """Schema for updating a Correo"""
    codigo: Optional[str] = None
    razon_social: Optional[str] = None
    tipo_tercero: Optional[str] = None
    numero_identificacion: Optional[str] = None
    email: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        if v is None:
            return v
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()


class CorreoResponse(CorreoBase):
    """Schema for Correo response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CorreoListResponse(BaseModel):
    """Schema for list of Correos with pagination"""
    items: List[CorreoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Auth Schemas
class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """Schema for user response"""
    username: str
    message: str


# Email Schemas
class EmailSendRequest(BaseModel):
    """Schema for sending an email"""
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)
    recipient_ids: Optional[List[int]] = None  # If None, send to all
    filter_tipo_tercero: Optional[str] = None  # Filter by type


class EmailSendResponse(BaseModel):
    """Schema for email send response"""
    message: str
    campaign_id: int
    total_recipients: int


class EmailLogResponse(BaseModel):
    """Schema for email log response"""
    id: int
    correo_id: Optional[int]
    email: str
    subject: str
    status: str
    error_message: Optional[str]
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmailCampaignResponse(BaseModel):
    """Schema for email campaign response"""
    id: int
    name: str
    subject: str
    body: str
    total_recipients: int
    sent_count: int
    failed_count: int
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EmailCampaignListResponse(BaseModel):
    """Schema for list of campaigns"""
    items: List[EmailCampaignResponse]
    total: int


# CSV Upload Response
class CSVUploadResponse(BaseModel):
    """Schema for CSV upload response"""
    message: str
    total_processed: int
    total_inserted: int
    total_duplicates: int
    total_invalid: int
    errors: List[str] = []


# Stats Response
class StatsResponse(BaseModel):
    """Schema for dashboard stats"""
    total_contacts: int
    total_emails_sent: int
    total_emails_failed: int
    total_campaigns: int
    contacts_by_type: dict


# Generic Response
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True