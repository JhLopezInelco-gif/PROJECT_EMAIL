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


# ==========================================
# INVENTARIO TI - Modelos
# ==========================================

class Equipo(Base):
    """Model for TI equipment inventory"""
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_equipo = Column(String(100))
    puesto = Column(String(100))
    nombre_usuario = Column(String(255))
    empleado = Column(String(255))
    marca = Column(String(100))
    estado_licencia = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Equipo(id={self.id}, nombre_equipo='{self.nombre_equipo}', empleado='{self.empleado}')>"


class MemoriaRAM(Base):
    """Model for RAM memory inventory"""
    __tablename__ = "memorias_ram"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tipo = Column(String(50))
    capacidad = Column(String(50))
    equipo = Column(String(50))
    cantidad = Column(Integer, default=0)
    disponible = Column(Integer, default=0)
    asignado = Column(Integer, default=0)
    observaciones = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<MemoriaRAM(id={self.id}, tipo='{self.tipo}', capacidad='{self.capacidad}')>"


class Almacenamiento(Base):
    """Model for storage devices inventory"""
    __tablename__ = "almacenamiento"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cantidad = Column(Integer, default=0)
    tipo = Column(String(100))
    capacidad = Column(String(100))
    marca = Column(String(100))
    disponible = Column(Integer, default=0)
    asignados = Column(Integer, default=0)
    asignado_por = Column(String(255), nullable=True)
    responsable = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Almacenamiento(id={self.id}, tipo='{self.tipo}', capacidad='{self.capacidad}')>"


class SalidaBodega(Base):
    """Model for warehouse exit records"""
    __tablename__ = "salida_bodega"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cantidad = Column(Integer, default=0)
    periferico = Column(String(100))
    marca = Column(String(100))
    modelo_serie = Column(String(255))
    asignado = Column(String(255))
    retirado_por = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SalidaBodega(id={self.id}, periferico='{self.periferico}', asignado='{self.asignado}')>"


class SMTPConfig(Base):
    """Model for SMTP configuration settings"""
    __tablename__ = "smtp_configs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), default="Configuración Principal")
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False, default=587)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    from_email = Column(String(255), nullable=False)
    from_name = Column(String(255), default="Sistema de Correos")
    use_tls = Column(Boolean, default=True)
    use_ssl = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    timeout = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SMTPConfig(id={self.id}, host='{self.host}', username='{self.username}')>"
