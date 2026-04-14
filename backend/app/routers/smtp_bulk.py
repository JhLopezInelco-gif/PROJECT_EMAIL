"""
Router for bulk email sending operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.database import get_db
from app.models import Correo, EmailCampaign, EmailLog
from app.schemas import (
    EmailSendRequest,
    EmailSendResponse,
    EmailCampaignResponse,
    EmailCampaignListResponse,
    MessageResponse
)
from app.auth import get_current_user
from app.email_service import bulk_email_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/smtp",
    tags=["SMTP Bulk Operations"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/enviar-masivo", response_model=EmailSendResponse, status_code=status.HTTP_201_CREATED)
def enviar_email_masivo(
    email_data: EmailSendRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Enviar correos masivos a múltiples destinatarios
    
    Este endpoint permite enviar correos a una lista de contactos filtrados por tipo.
    El envío se realiza en segundo plano para no bloquear la respuesta.
    """
    try:
        # Get recipients based on filters
        query = db.query(Correo)
        
        if email_data.recipient_ids:
            # Send to specific recipients
            query = query.filter(Correo.id.in_(email_data.recipient_ids))
        elif email_data.filter_tipo_tercero:
            # Filter by type
            query = query.filter(Correo.tipo_tercero == email_data.filter_tipo_tercero)
        
        recipients = query.all()
        
        if not recipients:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se encontraron destinatarios para los criterios especificados"
            )
        
        # Create email campaign
        campaign = EmailCampaign(
            name=f"Campaña {email_data.subject[:50]}...",
            subject=email_data.subject,
            body=email_data.body,
            total_recipients=len(recipients),
            sent_count=0,
            failed_count=0,
            status="pending"
        )
        
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        # Prepare recipients data for bulk sending
        recipients_data = [
            {"id": r.id, "email": r.email}
            for r in recipients
        ]
        
        # Start bulk sending in background
        background_tasks.add_task(
            bulk_email_service.send_bulk_emails,
            campaign_id=campaign.id,
            recipients=recipients_data,
            subject=email_data.subject,
            body=email_data.body,
            delay_seconds=2.0  # 2 second delay between emails
        )
        
        return EmailSendResponse(
            message="Campaña de correo iniciada exitosamente",
            campaign_id=campaign.id,
            total_recipients=len(recipients)
        )
        
    except Exception as e:
        logger.error(f"Error al iniciar campaña de correo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar campaña: {str(e)}"
        )


@router.get("/campañas", response_model=EmailCampaignListResponse)
def get_campañas(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Obtener todas las campañas de correo con paginación"""
    try:
        campaigns = db.query(EmailCampaign).order_by(EmailCampaign.created_at.desc()).offset(skip).limit(limit).all()
        total = db.query(EmailCampaign).count()
        
        return EmailCampaignListResponse(items=campaigns, total=total)
        
    except Exception as e:
        logger.error(f"Error al obtener campañas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener campañas"
        )


@router.get("/campañas/{campaign_id}", response_model=EmailCampaignResponse)
def get_campaña(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Obtener detalles de una campaña específica"""
    try:
        campaign = db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaña con ID {campaign_id} no encontrada"
            )
        
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener campaña {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener campaña"
        )


@router.delete("/campañas/{campaign_id}", response_model=MessageResponse)
def delete_campaña(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar una campaña de correo"""
    try:
        # Check if campaign exists
        campaign = db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaña con ID {campaign_id} no encontrada"
            )
        
        # Check if campaign is in progress
        if campaign.status == "sending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una campaña en progreso"
            )
        
        # Delete associated email logs
        db.query(EmailLog).filter(EmailLog.correo_id.in_(
            db.query(Correo.id).join(EmailLog, Correo.id == EmailLog.correo_id)
        )).delete(synchronize_session=False)
        
        # Delete campaign
        db.delete(campaign)
        db.commit()
        
        return MessageResponse(
            message="Campaña eliminada exitosamente",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar campaña {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar campaña"
        )


@router.post("/campañas/{campaign_id}/cancelar", response_model=MessageResponse)
def cancelar_campaña(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Cancelar una campaña de correo en progreso"""
    try:
        campaign = db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaña con ID {campaign_id} no encontrada"
            )
        
        if campaign.status not in ["pending", "sending"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden cancelar campañas pendientes o en progreso"
            )
        
        # Cancel the campaign
        campaign.status = "cancelled"
        campaign.completed_at = datetime.utcnow()
        db.commit()
        
        # Cancel the bulk sending
        bulk_email_service.cancel_sending()
        
        return MessageResponse(
            message="Campaña cancelada exitosamente",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al cancelar campaña {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cancelar campaña"
        )


@router.get("/campañas/{campaign_id}/logs")
def get_campaña_logs(
    campaign_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener los logs de envío de una campaña específica"""
    try:
        # Verify campaign exists
        campaign = db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Campaña con ID {campaign_id} no encontrada"
            )
        
        # Get email logs for this campaign
        logs = db.query(EmailLog).filter(
            EmailLog.subject == campaign.subject
        ).order_by(EmailLog.created_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "logs": [
                {
                    "id": log.id,
                    "email": log.email,
                    "status": log.status,
                    "error_message": log.error_message,
                    "sent_at": log.sent_at,
                    "created_at": log.created_at
                }
                for log in logs
            ],
            "total": db.query(EmailLog).filter(EmailLog.subject == campaign.subject).count()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener logs de campaña {campaign_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener logs de campaña"
        )