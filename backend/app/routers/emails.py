"""
Email sending router
Improved version with SMTP verification and better error handling
"""
import asyncio
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.database import get_db
from app.models import Correo, EmailLog, EmailCampaign
from app.schemas import (
    EmailSendRequest, EmailSendResponse, EmailLogResponse,
    EmailCampaignResponse, EmailCampaignListResponse, MessageResponse
)
from app.auth import get_current_user
from app.schemas import UserResponse
from app.email_service import EmailService, bulk_email_service

router = APIRouter(prefix="/emails", tags=["Emails"])
logger = logging.getLogger(__name__)


# Store for tracking sending progress
sending_progress = {}


@router.post("/verify-smtp", response_model=dict)
async def verify_smtp_connection(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Verify SMTP connection and authentication
    
    Returns connection status and any error messages
    """
    logger.info("🔍 Verificando conexión SMTP...")
    
    email_service = EmailService()
    success, message = email_service.verify_connection()
    
    return {
        "success": success,
        "message": message,
        "smtp_host": settings.SMTP_HOST if success else None,
        "smtp_port": settings.SMTP_PORT if success else None,
        "smtp_user": settings.SMTP_USER if success else None
    }


@router.post("/test", response_model=dict)
async def send_test_email(
    to_email: str,
    subject: str = "Test Email - Sistema de Correos",
    body: str = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Send a test email to verify SMTP configuration
    
    - **to_email**: Recipient email address
    - **subject**: Email subject (optional)
    - **body**: Email HTML body (optional, uses default if not provided)
    """
    logger.info(f"📤 Enviando email de prueba a: {to_email}")
    
    # Default test body
    if not body:
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #333;">Test Email</h2>
            <p>Este es un email de prueba enviado desde el Sistema de Envío de Correos.</p>
            <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Enviado a:</strong> {to_email}</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                Este email fue enviado automáticamente. Por favor no responda.
            </p>
        </body>
        </html>
        """
    
    email_service = EmailService()
    success, error_msg = email_service.send_email(to_email, subject, body)
    
    if success:
        return {
            "success": True,
            "message": f"Email de prueba enviado exitosamente a {to_email}",
            "to_email": to_email,
            "subject": subject
        }
    else:
        logger.error(f"❌ Error enviando email de prueba: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error enviando email de prueba",
                "error": error_msg,
                "to_email": to_email
            }
        )


@router.post("/send", response_model=EmailSendResponse)
async def send_emails(
    request: EmailSendRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Send bulk emails
    
    - **subject**: Email subject
    - **body**: Email HTML body
    - **recipient_ids**: List of specific recipient IDs (optional, if None sends to all)
    - **filter_tipo_tercero**: Filter recipients by tipo_tercero (optional)
    """
    logger.info(f"📧 Iniciando envío de correos masivos...")
    
    # Get recipients
    query = db.query(Correo)
    
    if request.recipient_ids:
        query = query.filter(Correo.id.in_(request.recipient_ids))
    elif request.filter_tipo_tercero:
        query = query.filter(Correo.tipo_tercero == request.filter_tipo_tercero)
    
    recipients = query.all()
    
    if not recipients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se encontraron destinatarios con los criterios especificados"
        )
    
    # Verify SMTP connection first
    email_service = EmailService()
    success, msg = email_service.verify_connection()
    if not success:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error de conexión SMTP: {msg}"
        )
    
    # Create campaign
    campaign = EmailCampaign(
        name=f"Campaign {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        subject=request.subject,
        body=request.body,
        total_recipients=len(recipients),
        status="draft"
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    
    # Prepare recipient list
    recipient_list = [
        {"id": r.id, "email": r.email}
        for r in recipients
    ]
    
    # Initialize progress tracking
    sending_progress[campaign.id] = {
        "total": len(recipient_list),
        "sent": 0,
        "failed": 0,
        "current_email": None,
        "status": "starting"
    }
    
    # Define progress callback
    def progress_callback(current, total, email, success):
        sending_progress[campaign.id]["sent"] = current
        sending_progress[campaign.id]["current_email"] = email
        if not success:
            sending_progress[campaign.id]["failed"] += 1
        sending_progress[campaign.id]["status"] = "sending"
    
    # Start background task for sending emails
    def send_task():
        try:
            bulk_email_service.send_bulk_emails(
                campaign_id=campaign.id,
                recipients=recipient_list,
                subject=request.subject,
                body=request.body,
                delay_seconds=settings.EMAIL_DELAY_SECONDS,
                progress_callback=progress_callback
            )
            sending_progress[campaign.id]["status"] = "completed"
        except Exception as e:
            logger.error(f"❌ Error en tarea de envío: {e}")
            sending_progress[campaign.id]["status"] = f"error: {str(e)}"
    
    background_tasks.add_task(send_task)
    
    logger.info(f"✅ Campaña {campaign.id} iniciada con {len(recipients)} destinatarios")
    
    return EmailSendResponse(
        message=f"Campaña iniciada. Enviando a {len(recipients)} destinatarios.",
        campaign_id=campaign.id,
        total_recipients=len(recipients)
    )


@router.get("/progress/{campaign_id}", response_model=dict)
async def get_sending_progress(
    campaign_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get the progress of an email sending campaign"""
    if campaign_id not in sending_progress:
        # Check if campaign exists in database
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            campaign = db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
            if campaign:
                return {
                    "campaign_id": campaign_id,
                    "total": campaign.total_recipients,
                    "sent": campaign.sent_count,
                    "failed": campaign.failed_count,
                    "status": campaign.status,
                    "current_email": None,
                    "started_at": campaign.started_at.isoformat() if campaign.started_at else None,
                    "completed_at": campaign.completed_at.isoformat() if campaign.completed_at else None
                }
        finally:
            db.close()
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaña {campaign_id} no encontrada"
        )
    
    return {
        "campaign_id": campaign_id,
        **sending_progress[campaign_id]
    }


@router.get("/campaigns", response_model=EmailCampaignListResponse)
async def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """List all email campaigns"""
    total = db.query(EmailCampaign).count()
    offset = (page - 1) * page_size
    
    campaigns = db.query(EmailCampaign)\
        .order_by(EmailCampaign.created_at.desc())\
        .offset(offset)\
        .limit(page_size)\
        .all()
    
    return EmailCampaignListResponse(
        items=[EmailCampaignResponse.model_validate(c) for c in campaigns],
        total=total
    )


@router.get("/campaigns/{campaign_id}", response_model=EmailCampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific campaign"""
    campaign = db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaña {campaign_id} no encontrada"
        )
    return EmailCampaignResponse.model_validate(campaign)


@router.get("/logs", response_model=dict)
async def list_email_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    campaign_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """List email logs with optional filtering"""
    query = db.query(EmailLog)
    
    if campaign_id:
        # Get logs for emails sent in a campaign (by matching subject/body)
        campaign = db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
        if campaign:
            query = query.filter(
                EmailLog.subject == campaign.subject,
                EmailLog.created_at >= campaign.started_at
            )
    
    if status_filter:
        query = query.filter(EmailLog.status == status_filter)
    
    total = query.count()
    offset = (page - 1) * page_size
    
    logs = query.order_by(EmailLog.created_at.desc())\
        .offset(offset)\
        .limit(page_size)\
        .all()
    
    return {
        "items": [EmailLogResponse.model_validate(log) for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.post("/cancel/{campaign_id}", response_model=MessageResponse)
async def cancel_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Cancel an ongoing email campaign"""
    campaign = db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaña {campaign_id} no encontrada"
        )
    
    if campaign.status != "sending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La campaña no está en estado de envío (estado actual: {campaign.status})"
        )
    
    # Cancel the sending
    bulk_email_service.cancel_sending()
    
    return MessageResponse(message=f"Solicitud de cancelación enviada para campaña {campaign_id}")


@router.get("/stats", response_model=dict)
async def get_email_stats(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get email statistics"""
    total_contacts = db.query(Correo).count()
    total_sent = db.query(EmailLog).filter(EmailLog.status == "sent").count()
    total_failed = db.query(EmailLog).filter(EmailLog.status == "failed").count()
    total_campaigns = db.query(EmailCampaign).count()
    
    # Contacts by type
    contacts_by_type = db.query(
        Correo.tipo_tercero,
        func.count(Correo.id)
    ).group_by(Correo.tipo_tercero).all()
    
    contacts_by_type_dict = {t: c for t, c in contacts_by_type if t}
    
    # Recent campaigns
    recent_campaigns = db.query(EmailCampaign)\
        .order_by(EmailCampaign.created_at.desc())\
        .limit(5)\
        .all()
    
    return {
        "total_contacts": total_contacts,
        "total_emails_sent": total_sent,
        "total_emails_failed": total_failed,
        "total_campaigns": total_campaigns,
        "contacts_by_type": contacts_by_type_dict,
        "recent_campaigns": [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "sent_count": c.sent_count,
                "failed_count": c.failed_count,
                "total_recipients": c.total_recipients,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in recent_campaigns
        ]
    }


# Import settings for the verify endpoint
from app.config import settings