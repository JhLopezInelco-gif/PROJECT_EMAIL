"""
Router for SMTP configuration management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from app.database import get_db
from app.models import SMTPConfig
from app.schemas import (
    SMTPConfigCreate,
    SMTPConfigUpdate,
    SMTPConfigResponse,
    SMTPConfigListResponse,
    SMTPTestRequest,
    SMTPTestResponse,
    MessageResponse
)
from app.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/smtp-config",
    tags=["SMTP Configuration"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=SMTPConfigListResponse)
def get_smtp_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all SMTP configurations"""
    configs = db.query(SMTPConfig).offset(skip).limit(limit).all()
    total = db.query(SMTPConfig).count()
    return SMTPConfigListResponse(items=configs, total=total)


@router.get("/default", response_model=SMTPConfigResponse)
def get_default_smtp_config(db: Session = Depends(get_db)):
    """Get the default SMTP configuration"""
    config = db.query(SMTPConfig).filter(SMTPConfig.is_default == True).first()
    if not config:
        # Try to get any active config
        config = db.query(SMTPConfig).filter(SMTPConfig.is_active == True).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No SMTP configuration found. Please create one."
        )
    return config


@router.get("/{config_id}", response_model=SMTPConfigResponse)
def get_smtp_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific SMTP configuration by ID"""
    config = db.query(SMTPConfig).filter(SMTPConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SMTP configuration with id {config_id} not found"
        )
    return config


@router.post("/", response_model=SMTPConfigResponse, status_code=status.HTTP_201_CREATED)
def create_smtp_config(
    config_data: SMTPConfigCreate,
    db: Session = Depends(get_db)
):
    """Create a new SMTP configuration"""
    # If this is set as default, unset other defaults
    if config_data.is_default:
        db.query(SMTPConfig).update({SMTPConfig.is_default: False})
    
    # Check if this is the first config, make it default
    existing_count = db.query(SMTPConfig).count()
    
    new_config = SMTPConfig(
        name=config_data.name,
        host=config_data.host,
        port=config_data.port,
        username=config_data.username,
        password=config_data.password,
        from_email=config_data.from_email,
        from_name=config_data.from_name,
        use_tls=config_data.use_tls,
        use_ssl=config_data.use_ssl,
        is_default=config_data.is_default or (existing_count == 0),
        timeout=config_data.timeout
    )
    
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    return new_config


@router.put("/{config_id}", response_model=SMTPConfigResponse)
def update_smtp_config(
    config_id: int,
    config_data: SMTPConfigUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing SMTP configuration"""
    config = db.query(SMTPConfig).filter(SMTPConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SMTP configuration with id {config_id} not found"
        )
    
    # If setting as default, unset other defaults
    if config_data.is_default:
        db.query(SMTPConfig).update({SMTPConfig.is_default: False})
    
    update_data = config_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    return config


@router.delete("/{config_id}", response_model=MessageResponse)
def delete_smtp_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Delete an SMTP configuration"""
    config = db.query(SMTPConfig).filter(SMTPConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SMTP configuration with id {config_id} not found"
        )
    
    was_default = config.is_default
    db.delete(config)
    db.commit()
    
    # If deleted config was default, set another as default
    if was_default:
        new_default = db.query(SMTPConfig).filter(SMTPConfig.is_active == True).first()
        if new_default:
            new_default.is_default = True
            db.commit()
    
    return MessageResponse(message="SMTP configuration deleted successfully", success=True)


@router.post("/test", response_model=SMTPTestResponse)
def test_smtp_connection(
    test_data: SMTPTestRequest,
    db: Session = Depends(get_db)
):
    """Test SMTP connection with provided settings"""
    logger.info(f"[SMTP TEST] Testing connection to {test_data.host}:{test_data.port} SSL={test_data.use_ssl} TLS={test_data.use_tls}")
    
    # Validate password
    if not test_data.password:
        return SMTPTestResponse(
            success=False,
            message="Contraseña requerida",
            details="Debe proporcionar la contraseña para probar la conexión"
        )
    
    try:
        # Determine connection type
        if test_data.use_ssl:
            # SSL connection (usually port 465) - direct encrypted connection
            logger.info(f"[SMTP TEST] Using SMTP_SSL on port {test_data.port}")
            server = smtplib.SMTP_SSL(test_data.host, test_data.port, timeout=30)
        else:
            # STARTTLS connection (usually port 587) - upgrade to TLS
            logger.info(f"[SMTP TEST] Using SMTP + STARTTLS on port {test_data.port}")
            server = smtplib.SMTP(test_data.host, test_data.port, timeout=30)
            server.ehlo()
            if test_data.use_tls:
                server.starttls()
                server.ehlo()
        
        # Login
        logger.info(f"[SMTP TEST] Logging in as {test_data.username}")
        server.login(test_data.username, test_data.password)
        logger.info("[SMTP TEST] Login successful")
        
        # If test email provided, send a test email
        if test_data.test_email:
            msg = MIMEMultipart()
            msg['From'] = test_data.username
            msg['To'] = test_data.test_email
            msg['Subject'] = "Prueba de Configuracion SMTP"
            body = """
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #2563eb;">Prueba de Conexion Exitosa</h2>
                <p>Este correo confirma que la configuracion SMTP es correcta.</p>
                <hr>
                <p><strong>Servidor:</strong> {}:{}</p>
                <p><strong>Usuario:</strong> {}</p>
                <p><strong>Seguridad:</strong> {}</p>
                <br>
                <p style="color: #666; font-size: 12px;">Sistema de Gestion de Correos</p>
            </body>
            </html>
            """.format(test_data.host, test_data.port, test_data.username, 
                      "SSL" if test_data.use_ssl else ("STARTTLS" if test_data.use_tls else "Ninguna"))
            msg.attach(MIMEText(body, 'html'))
            
            server.sendmail(test_data.username, test_data.test_email, msg.as_string())
            logger.info(f"[SMTP TEST] Test email sent to {test_data.test_email}")
        
        server.quit()
        
        return SMTPTestResponse(
            success=True,
            message="Conexion SMTP exitosa" + (" y correo de prueba enviado" if test_data.test_email else ""),
            details=f"Conectado a {test_data.host}:{test_data.port}"
        )
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"[SMTP TEST] Authentication failed: {e}")
        return SMTPTestResponse(
            success=False,
            message="Error de autenticacion",
            details=f"Verifique usuario y contrasena. Detalle: {str(e)}"
        )
    except smtplib.SMTPConnectError as e:
        logger.error(f"[SMTP TEST] Connection error: {e}")
        return SMTPTestResponse(
            success=False,
            message="Error de conexion al servidor SMTP",
            details=f"No se pudo conectar a {test_data.host}:{test_data.port}. Verifique servidor y puerto. Detalle: {str(e)}"
        )
    except socket.timeout:
        logger.error(f"[SMTP TEST] Connection timeout to {test_data.host}:{test_data.port}")
        return SMTPTestResponse(
            success=False,
            message="Tiempo de conexion agotado",
            details=f"No se pudo conectar a {test_data.host}:{test_data.port} en 30 segundos. Verifique que el servidor y puerto sean correctos."
        )
    except socket.gaierror as e:
        logger.error(f"[SMTP TEST] DNS resolution failed for {test_data.host}: {e}")
        return SMTPTestResponse(
            success=False,
            message="Error de resolucion DNS",
            details=f"No se pudo resolver el nombre del servidor '{test_data.host}'. Verifique que el nombre sea correcto."
        )
    except ConnectionRefusedError:
        logger.error(f"[SMTP TEST] Connection refused by {test_data.host}:{test_data.port}")
        return SMTPTestResponse(
            success=False,
            message="Conexion rechazada",
            details=f"El servidor {test_data.host}:{test_data.port} rechazo la conexion. Verifique el puerto y si SSL/STARTTLS es correcto."
        )
    except smtplib.SMTPException as e:
        logger.error(f"[SMTP TEST] SMTP error: {e}")
        return SMTPTestResponse(
            success=False,
            message="Error SMTP",
            details=str(e)
        )
    except Exception as e:
        logger.error(f"[SMTP TEST] Unexpected error: {type(e).__name__}: {e}")
        return SMTPTestResponse(
            success=False,
            message="Error inesperado",
            details=f"{type(e).__name__}: {str(e)}"
        )


@router.post("/test/{config_id}", response_model=SMTPTestResponse)
def test_existing_smtp_config(
    config_id: int,
    test_email: str = None,
    db: Session = Depends(get_db)
):
    """Test an existing SMTP configuration"""
    config = db.query(SMTPConfig).filter(SMTPConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SMTP configuration with id {config_id} not found"
        )
    
    test_data = SMTPTestRequest(
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password,
        use_tls=config.use_tls,
        use_ssl=config.use_ssl,
        test_email=test_email
    )
    
    return test_smtp_connection(test_data, db)


@router.post("/{config_id}/set-default", response_model=SMTPConfigResponse)
def set_default_smtp_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Set an SMTP configuration as default"""
    config = db.query(SMTPConfig).filter(SMTPConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SMTP configuration with id {config_id} not found"
        )
    
    # Unset all defaults
    db.query(SMTPConfig).update({SMTPConfig.is_default: False})
    
    # Set this as default
    config.is_default = True
    config.is_active = True
    db.commit()
    db.refresh(config)
    
    return config


@router.post("/{config_id}/toggle-active", response_model=SMTPConfigResponse)
def toggle_smtp_config_active(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Toggle active status of an SMTP configuration"""
    config = db.query(SMTPConfig).filter(SMTPConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SMTP configuration with id {config_id} not found"
        )
    
    config.is_active = not config.is_active
    db.commit()
    db.refresh(config)
    
    return config