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


# SMTP Configuration Schemas
class SMTPConfigBase(BaseModel):
    """Base schema for SMTP configuration"""
    name: Optional[str] = "Configuracion Principal"
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(default=465, ge=1, le=65535)
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=255)
    from_email: EmailStr
    from_name: Optional[str] = "Sistema de Correos"
    use_tls: bool = False
    use_ssl: bool = True
    timeout: int = Field(default=30, ge=5, le=300)


class SMTPConfigCreate(SMTPConfigBase):
    """Schema for creating SMTP configuration"""
    is_default: Optional[bool] = False


class SMTPConfigUpdate(BaseModel):
    """Schema for updating SMTP configuration"""
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = None
    password: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    use_tls: Optional[bool] = None
    use_ssl: Optional[bool] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    timeout: Optional[int] = Field(None, ge=5, le=300)


class SMTPConfigResponse(BaseModel):
    """Schema for SMTP configuration response"""
    id: int
    name: str
    host: str
    port: int
    username: str
    from_email: str
    from_name: str
    use_tls: bool
    use_ssl: bool
    is_active: bool
    is_default: bool
    timeout: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SMTPConfigListResponse(BaseModel):
    """Schema for list of SMTP configurations"""
    items: List[SMTPConfigResponse]
    total: int


class SMTPTestRequest(BaseModel):
    """Schema for testing SMTP connection"""
    host: str
    port: int
    username: str
    password: Optional[str] = None
    use_tls: bool = False
    use_ssl: bool = True
    test_email: Optional[EmailStr] = None


class SMTPTestResponse(BaseModel):
    """Schema for SMTP test response"""
    success: bool
    message: str
    details: Optional[str] = None


# ==========================================
# INVENTARIO TI - Schemas
# ==========================================

# --- Equipos ---
class EquipoBase(BaseModel):
    nombre_equipo: Optional[str] = None
    puesto: Optional[str] = None
    nombre_usuario: Optional[str] = None
    empleado: Optional[str] = None
    marca: Optional[str] = None
    estado_licencia: Optional[str] = None

class EquipoCreate(EquipoBase):
    pass

class EquipoUpdate(BaseModel):
    nombre_equipo: Optional[str] = None
    puesto: Optional[str] = None
    nombre_usuario: Optional[str] = None
    empleado: Optional[str] = None
    marca: Optional[str] = None
    estado_licencia: Optional[str] = None

class EquipoResponse(EquipoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class EquipoListResponse(BaseModel):
    items: List[EquipoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# --- Memorias RAM ---
class MemoriaRAMBase(BaseModel):
    tipo: Optional[str] = None
    capacidad: Optional[str] = None
    equipo: Optional[str] = None
    cantidad: Optional[int] = 0
    disponible: Optional[int] = 0
    asignado: Optional[int] = 0
    observaciones: Optional[str] = None

class MemoriaRAMCreate(MemoriaRAMBase):
    pass

class MemoriaRAMUpdate(BaseModel):
    tipo: Optional[str] = None
    capacidad: Optional[str] = None
    equipo: Optional[str] = None
    cantidad: Optional[int] = None
    disponible: Optional[int] = None
    asignado: Optional[int] = None
    observaciones: Optional[str] = None

class MemoriaRAMResponse(MemoriaRAMBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class MemoriaRAMListResponse(BaseModel):
    items: List[MemoriaRAMResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# --- Almacenamiento ---
class AlmacenamientoBase(BaseModel):
    cantidad: Optional[int] = 0
    tipo: Optional[str] = None
    capacidad: Optional[str] = None
    marca: Optional[str] = None
    disponible: Optional[int] = 0
    asignados: Optional[int] = 0
    asignado_por: Optional[str] = None
    responsable: Optional[str] = None

class AlmacenamientoCreate(AlmacenamientoBase):
    pass

class AlmacenamientoUpdate(BaseModel):
    cantidad: Optional[int] = None
    tipo: Optional[str] = None
    capacidad: Optional[str] = None
    marca: Optional[str] = None
    disponible: Optional[int] = None
    asignados: Optional[int] = None
    asignado_por: Optional[str] = None
    responsable: Optional[str] = None

class AlmacenamientoResponse(AlmacenamientoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class AlmacenamientoListResponse(BaseModel):
    items: List[AlmacenamientoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# --- Salida Bodega ---
class SalidaBodegaBase(BaseModel):
    cantidad: Optional[int] = 0
    periferico: Optional[str] = None
    marca: Optional[str] = None
    modelo_serie: Optional[str] = None
    asignado: Optional[str] = None
    retirado_por: Optional[str] = None

class SalidaBodegaCreate(SalidaBodegaBase):
    pass

class SalidaBodegaUpdate(BaseModel):
    cantidad: Optional[int] = None
    periferico: Optional[str] = None
    marca: Optional[str] = None
    modelo_serie: Optional[str] = None
    asignado: Optional[str] = None
    retirado_por: Optional[str] = None

class SalidaBodegaResponse(SalidaBodegaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class SalidaBodegaListResponse(BaseModel):
    items: List[SalidaBodegaResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
