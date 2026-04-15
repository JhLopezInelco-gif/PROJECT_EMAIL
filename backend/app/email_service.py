"""
Email service for sending emails via SMTP
Improved version with STARTTLS support and detailed logging
"""
import asyncio
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate, make_msgid
from datetime import datetime
from typing import List, Optional, Callable, Dict, Any
from sqlalchemy.orm import Session
import logging
import traceback

from app.config import settings
from app.models import Correo, EmailLog, EmailCampaign
from app.database import SessionLocal

# Configure logging
logger = logging.getLogger(__name__)


class SMTPConnectionError(Exception):
    """Error de conexión SMTP"""
    pass


class SMTPAuthenticationError(Exception):
    """Error de autenticación SMTP"""
    pass


class SMTPTLSError(Exception):
    """Error de TLS SMTP"""
    pass


class EmailService:
    """Service for sending emails with improved SMTP handling"""
    
    def __init__(self):
        # Try to load from database first, fall back to .env settings
        db_config = self._load_smtp_from_db()
        if db_config:
            self.host = db_config['host']
            self.port = db_config['port']
            self.username = db_config['username']
            self.password = db_config['password']
            self.from_email = db_config['from_email']
            self.from_name = db_config['from_name']
            self.security = 'SSL' if db_config['use_ssl'] else ('STARTTLS' if db_config['use_tls'] else 'NONE')
            self.timeout = db_config.get('timeout', 30)
            logger.info("[SMTP] Config loaded from DATABASE")
        else:
            # Fallback to .env settings
            self.host = settings.SMTP_HOST
            self.port = settings.SMTP_PORT
            self.username = settings.SMTP_USER
            self.password = settings.SMTP_PASSWORD
            self.from_email = settings.smtp_from_email
            self.from_name = settings.SMTP_FROM_NAME
            self.security = settings.SMTP_SECURITY
            self.timeout = settings.SMTP_TIMEOUT
            logger.info("[SMTP] Config loaded from .env (fallback, no DB config found)")
        
        logger.info(f"[SMTP] EmailService inicializado:")
        logger.info(f"   Host: {self.host}:{self.port}")
        logger.info(f"   User: {self.username}")
        logger.info(f"   Security: {self.security}")
        logger.info(f"   From: {self.from_name} <{self.from_email}>")
    
    @staticmethod
    def _load_smtp_from_db():
        """Load SMTP configuration from database (active/default config)"""
        try:
            from app.models import SMTPConfig as SMTPConfigModel
            db = SessionLocal()
            try:
                # First try active default config
                config = db.query(SMTPConfigModel).filter(
                    SMTPConfigModel.is_default == True,
                    SMTPConfigModel.is_active == True
                ).first()
                # Then try any active config
                if not config:
                    config = db.query(SMTPConfigModel).filter(
                        SMTPConfigModel.is_active == True
                    ).first()
                # Then try any config at all
                if not config:
                    config = db.query(SMTPConfigModel).first()
                if config:
                    return {
                        'host': config.host,
                        'port': config.port,
                        'username': config.username,
                        'password': config.password,
                        'from_email': config.from_email,
                        'from_name': config.from_name,
                        'use_ssl': config.use_ssl,
                        'use_tls': config.use_tls,
                        'timeout': config.timeout,
                    }
                return None
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[SMTP] Could not load from DB: {e}")
            return None
    
    def _create_message(self, to_email: str, subject: str, body: str) -> MIMEMultipart:
        """Create an email message with proper headers"""
        msg = MIMEMultipart('alternative')
        
        # Set From with name and email
        msg['From'] = formataddr((self.from_name, self.from_email))
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid(domain=self.host.split('.')[0] if '.' in self.host else 'localhost')
        
        # Add HTML body
        html_part = MIMEText(body, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Also add plain text version for compatibility
        text_body = body.replace('<br>', '\n').replace('<br/>', '\n').replace('</p>', '\n\n')
        text_body = ''.join(c for c in text_body if c.isalnum() or c in ' \n\t.,;:!?()-')
        text_part = MIMEText(text_body[:500], 'plain', 'utf-8')
        msg.attach(text_part)
        
        return msg
    
    def verify_connection(self) -> tuple[bool, str]:
        """
        Verify SMTP connection and authentication
        
        Returns:
            tuple: (success: bool, message: str)
        """
        logger.info(f"🔍 Verificando conexión SMTP a {self.host}:{self.port}...")
        
        try:
            # Create SMTP connection - choose between SMTP and SMTP_SSL based on port/security
            logger.debug(f"   Creando conexión SMTP...")
            if self.port == 465 or self.security.upper() == 'SSL':
                logger.debug(f"   Usando SMTP_SSL para puerto {self.port}")
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                logger.debug(f"   Usando SMTP estándar para puerto {self.port}")
                server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
            
            # Enable debug output
            server.set_debuglevel(1 if settings.DEBUG else 0)
            
            # Identify ourselves
            logger.debug(f"   Enviando EHLO...")
            code, msg = server.ehlo()
            logger.info(f"   EHLO: {code}")
            
            # Check STARTTLS support (only for non-SSL connections)
            if self.port != 465 and self.security.upper() == 'STARTTLS':
                logger.debug(f"   Iniciando STARTTLS...")
                if server.has_extn('STARTTLS'):
                    code, msg = server.starttls()
                    logger.info(f"   ✅ STARTTLS activado: {code}")
                    # Re-identify after TLS
                    code, msg = server.ehlo()
                    logger.debug(f"   ✅ EHLO después de TLS: {code}")
                else:
                    error_msg = "El servidor no soporta STARTTLS"
                    logger.error(f"   ❌ {error_msg}")
                    server.quit()
                    return False, error_msg
            
            # Authenticate
            logger.debug(f"   Autenticando usuario: {self.username}...")
            code, msg = server.login(self.username, self.password)
            logger.info(f"   ✅ Autenticación exitosa: {code}")
            
            # Close connection
            server.quit()
            logger.info(f"   ✅ Conexión verificada correctamente")
            
            return True, "Conexión SMTP verificada correctamente"
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Error de autenticación: {e.smtp_code} - {e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)}"
            logger.error(f"   ❌ {error_msg}")
            logger.error(f"   Verifique usuario y contraseña")
            return False, error_msg
            
        except smtplib.SMTPConnectError as e:
            error_msg = f"Error de conexión: {e.smtp_code} - {e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except smtplib.SMTPHeloError as e:
            error_msg = f"Error en EHLO/HELO: {e.smtp_code} - {e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except smtplib.SMTPNotSupportedError as e:
            error_msg = f"Comando no soportado: {str(e)}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except socket.timeout:
            error_msg = f"Timeout conectando a {self.host}:{self.port}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except socket.gaierror as e:
            error_msg = f"Error resolviendo hostname {self.host}: {str(e)}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except ConnectionRefusedError:
            error_msg = f"Conexión rechazada por {self.host}:{self.port}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(f"   ❌ {error_msg}")
            logger.error(traceback.format_exc())
            return False, error_msg
    
    def send_email(self, to_email: str, subject: str, body: str) -> tuple[bool, Optional[str]]:
        """
        Send a single email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email HTML body
            
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        logger.info(f"📤 Enviando email a: {to_email}")
        logger.debug(f"   Asunto: {subject}")
        
        try:
            # Create message
            msg = self._create_message(to_email, subject, body)
            
            # Connect to SMTP server - choose between SMTP and SMTP_SSL based on port/security
            logger.debug(f"   Conectando a {self.host}:{self.port}...")
            if self.port == 465 or self.security.upper() == 'SSL':
                logger.debug(f"   Usando SMTP_SSL para puerto {self.port}")
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                logger.debug(f"   Usando SMTP estándar para puerto {self.port}")
                server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
            
            try:
                # Enable debug output
                server.set_debuglevel(1 if settings.DEBUG else 0)
                
                # EHLO
                code, msg_response = server.ehlo()
                logger.debug(f"   EHLO: {code}")
                
                # STARTTLS if configured (only for non-SSL connections)
                if self.port != 465 and self.security.upper() == 'STARTTLS':
                    if server.has_extn('STARTTLS'):
                        code, msg_response = server.starttls()
                        logger.debug(f"   STARTTLS: {code}")
                        code, msg_response = server.ehlo()
                        logger.debug(f"   EHLO after TLS: {code}")
                    else:
                        logger.warning(f"   STARTTLS no disponible, continuando sin encriptación")
                
                # Login
                code, msg_response = server.login(self.username, self.password)
                logger.debug(f"   Login: {code}")
                
                # Send email
                logger.debug(f"   Enviando mensaje...")
                server.sendmail(self.from_email, to_email, msg.as_string())
                
                logger.info(f"   ✅ Email enviado exitosamente a {to_email}")
                
            finally:
                # Always close connection
                server.quit()
            
            return True, None
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Error de autenticación SMTP: {e.smtp_code}"
            if isinstance(e.smtp_error, bytes):
                error_msg += f" - {e.smtp_error.decode()}"
            else:
                error_msg += f" - {str(e.smtp_error)}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Destinatario rechazado: {to_email}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except smtplib.SMTPSenderRefused as e:
            error_msg = f"Remitente rechazado: {self.from_email}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except smtplib.SMTPDataError as e:
            error_msg = f"Error en datos del mensaje: {e.smtp_code}"
            if isinstance(e.smtp_error, bytes):
                error_msg += f" - {e.smtp_error.decode()}"
            else:
                error_msg += f" - {str(e.smtp_error)}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except smtplib.SMTPException as e:
            error_msg = f"Error SMTP: {str(e)}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except socket.timeout:
            error_msg = f"Timeout enviando email a {to_email}"
            logger.error(f"   ❌ {error_msg}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(f"   ❌ {error_msg}")
            logger.error(traceback.format_exc())
            return False, error_msg
    
    async def send_email_async(self, to_email: str, subject: str, body: str) -> tuple[bool, Optional[str]]:
        """Send email asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.send_email, 
            to_email, 
            subject, 
            body
        )


class BulkEmailService:
    """Service for sending bulk emails with progress tracking"""
    
    def __init__(self):
        self.email_service = EmailService()
        self._cancel_flag = False
        self._current_connection = None
    
    def cancel_sending(self):
        """Cancel ongoing email sending"""
        logger.info("🛑 Solicitud de cancelación recibida")
        self._cancel_flag = True
    
    def send_bulk_emails(
        self,
        campaign_id: int,
        recipients: List[dict],
        subject: str,
        body: str,
        delay_seconds: float = 2.0,
        progress_callback: Optional[Callable] = None
    ) -> dict:
        """
        Send bulk emails with delay between each to avoid spam
        
        Args:
            campaign_id: ID of the email campaign
            recipients: List of recipient dicts with 'id', 'email'
            subject: Email subject
            body: Email HTML body
            delay_seconds: Delay between emails (default 2 seconds)
            progress_callback: Optional callback function for progress updates
        
        Returns:
            dict with 'sent', 'failed', 'total' counts
        """
        self._cancel_flag = False
        results = {'sent': 0, 'failed': 0, 'total': len(recipients)}
        
        logger.info(f"📧 Iniciando envío masivo:")
        logger.info(f"   Campaña ID: {campaign_id}")
        logger.info(f"   Total destinatarios: {len(recipients)}")
        logger.info(f"   Delay entre emails: {delay_seconds}s")
        
        db = SessionLocal()
        try:
            # Get campaign
            campaign = db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            campaign.status = "sending"
            campaign.started_at = datetime.utcnow()
            db.commit()
            
            # Verify SMTP connection before starting
            logger.info("   Verificando conexión SMTP...")
            success, msg = self.email_service.verify_connection()
            if not success:
                error_msg = f"Error de conexión SMTP: {msg}"
                logger.error(f"   ❌ {error_msg}")
                campaign.status = "failed"
                campaign.completed_at = datetime.utcnow()
                db.commit()
                raise Exception(error_msg)
            
            logger.info("   ✅ Conexión SMTP verificada")
            
            for idx, recipient in enumerate(recipients):
                if self._cancel_flag:
                    logger.info(f"🛑 Envío cancelado en {idx}/{len(recipients)}")
                    campaign.status = "cancelled"
                    campaign.completed_at = datetime.utcnow()
                    db.commit()
                    break
                
                to_email = recipient['email']
                logger.info(f"   [{idx + 1}/{len(recipients)}] Enviando a: {to_email}")
                
                # Send email
                success, error_msg = self.email_service.send_email(
                    to_email,
                    subject,
                    body
                )
                
                # Log result
                email_log = EmailLog(
                    correo_id=recipient.get('id'),
                    email=to_email,
                    subject=subject,
                    body=body[:1000],  # Store first 1000 chars
                    status="sent" if success else "failed",
                    error_message=error_msg,
                    sent_at=datetime.utcnow() if success else None
                )
                db.add(email_log)
                
                # Update campaign stats
                if success:
                    campaign.sent_count += 1
                    results['sent'] += 1
                    logger.info(f"      ✅ Enviado correctamente")
                else:
                    campaign.failed_count += 1
                    results['failed'] += 1
                    logger.error(f"      ❌ Error: {error_msg}")
                
                db.commit()
                
                # Progress callback
                if progress_callback:
                    progress_callback(idx + 1, len(recipients), to_email, success)
                
                # Delay to avoid spam
                if idx < len(recipients) - 1 and not self._cancel_flag:
                    import time
                    time.sleep(delay_seconds)
            
            # Mark campaign as completed if not cancelled
            if not self._cancel_flag:
                campaign.status = "completed"
                campaign.completed_at = datetime.utcnow()
                db.commit()
                logger.info(f"✅ Campaña completada: {results['sent']} enviados, {results['failed']} fallidos")
            
        except Exception as e:
            logger.error(f"❌ Error en envío masivo: {e}")
            logger.error(traceback.format_exc())
            if campaign:
                campaign.status = "failed"
                campaign.completed_at = datetime.utcnow()
                db.commit()
            raise
        finally:
            db.close()
        
        return results


# Global instance
bulk_email_service = BulkEmailService()