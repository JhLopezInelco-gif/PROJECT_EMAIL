"""
Correos (Contacts) router
"""
import csv
import io
import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.database import get_db
from app.models import Correo
from app.schemas import (
    CorreoCreate, CorreoUpdate, CorreoResponse, CorreoListResponse,
    CSVUploadResponse, MessageResponse
)
from app.auth import get_current_user
from app.schemas import UserResponse

router = APIRouter(prefix="/correos", tags=["Correos"])


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


@router.get("", response_model=CorreoListResponse)
async def list_correos(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=5000),
    search: Optional[str] = None,
    tipo_tercero: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    List all correos with pagination and filtering
    
    - **page**: Page number (starts at 1)
    - **page_size**: Items per page (max 500)
    - **search**: Search in email, razon_social, codigo
    - **tipo_tercero**: Filter by tipo_tercero
    """
    query = db.query(Correo)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Correo.email.ilike(search_term),
                Correo.razon_social.ilike(search_term),
                Correo.codigo.ilike(search_term),
                Correo.numero_identificacion.ilike(search_term)
            )
        )
    
    if tipo_tercero:
        query = query.filter(Correo.tipo_tercero == tipo_tercero)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    
    # Get paginated results
    items = query.order_by(Correo.id.desc()).offset(offset).limit(page_size).all()
    
    return CorreoListResponse(
        items=[CorreoResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/tipos", response_model=list[str])
async def get_tipos_tercero(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all unique tipo_tercero values"""
    tipos = db.query(Correo.tipo_tercero).distinct().all()
    return [t[0] for t in tipos if t[0]]


@router.get("/{correo_id}", response_model=CorreoResponse)
async def get_correo(
    correo_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific correo by ID"""
    correo = db.query(Correo).filter(Correo.id == correo_id).first()
    if not correo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Correo with id {correo_id} not found"
        )
    return CorreoResponse.model_validate(correo)


@router.post("", response_model=CorreoResponse, status_code=status.HTTP_201_CREATED)
async def create_correo(
    correo_data: CorreoCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new correo"""
    # Validate email
    if not validate_email(correo_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Check for duplicates
    existing = db.query(Correo).filter(Correo.email == correo_data.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email {correo_data.email} already exists"
        )
    
    # Create correo
    correo = Correo(
        codigo=correo_data.codigo,
        razon_social=correo_data.razon_social,
        tipo_tercero=correo_data.tipo_tercero,
        numero_identificacion=correo_data.numero_identificacion,
        email=correo_data.email.lower()
    )
    
    db.add(correo)
    db.commit()
    db.refresh(correo)
    
    return CorreoResponse.model_validate(correo)


@router.put("/{correo_id}", response_model=CorreoResponse)
async def update_correo(
    correo_id: int,
    correo_data: CorreoUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a correo"""
    correo = db.query(Correo).filter(Correo.id == correo_id).first()
    if not correo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Correo with id {correo_id} not found"
        )
    
    # Update fields
    update_data = correo_data.model_dump(exclude_unset=True)
    
    # Validate email if provided
    if 'email' in update_data:
        if not validate_email(update_data['email']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        # Check for duplicates
        existing = db.query(Correo).filter(
            Correo.email == update_data['email'].lower(),
            Correo.id != correo_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {update_data['email']} already exists"
            )
        update_data['email'] = update_data['email'].lower()
    
    for key, value in update_data.items():
        setattr(correo, key, value)
    
    db.commit()
    db.refresh(correo)
    
    return CorreoResponse.model_validate(correo)


@router.delete("/{correo_id}", response_model=MessageResponse)
async def delete_correo(
    correo_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a correo"""
    correo = db.query(Correo).filter(Correo.id == correo_id).first()
    if not correo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Correo with id {correo_id} not found"
        )
    
    db.delete(correo)
    db.commit()
    
    return MessageResponse(message=f"Correo {correo_id} deleted successfully")


@router.delete("", response_model=MessageResponse)
async def delete_all_correos(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete all correos (use with caution)"""
    count = db.query(Correo).delete()
    db.commit()
    
    return MessageResponse(message=f"Deleted {count} correos")


def detect_delimiter(line: str) -> str:
    """
    Detecta el delimitador del CSV (coma o punto y coma)
    Retorna el delimitador más probable
    """
    comma_count = line.count(',')
    semicolon_count = line.count(';')
    
    # Si no hay ninguno, default a coma
    if comma_count == 0 and semicolon_count == 0:
        return ','
    
    # Retornar el que tenga más ocurrencias
    return ';' if semicolon_count > comma_count else ','


def normalize_column_name(col_name: str) -> str:
    """Normaliza el nombre de columna para comparación"""
    return col_name.lower().strip().replace('_', ' ').replace('-', ' ')


def find_column_index(headers: list, possible_names: list) -> int:
    """
    Busca el índice de una columna por nombres posibles
    Retorna el índice o -1 si no se encuentra
    """
    headers_normalized = [normalize_column_name(h) for h in headers]
    
    for i, header in enumerate(headers_normalized):
        for name in possible_names:
            name_normalized = normalize_column_name(name)
            # Match exacto
            if header == name_normalized:
                return i
            # Match parcial
            if name_normalized in header or header in name_normalized:
                return i
    
    return -1


# Columnas requeridas con sus posibles nombres
REQUIRED_COLUMNS = {
    'codigo': ['codigo', 'código', 'code', 'id'],
    'razon_social': ['razon social', 'razón social', 'razon_social', 'razón_social', 'company', 'empresa', 'nombre'],
    'tipo_tercero': ['tipo de tercero', 'tipo_tercero', 'tipo', 'type', 'tipo tercero'],
    'numero_identificacion': ['numero identificacion', 'número identificación', 'numero_identificacion', 'número_identificación', 'nit', 'identification', 'doc', 'documento', 'número identificacion'],
    'email': ['email', 'correo', 'e-mail', 'mail', 'correo electronico', 'correo electrónico']
}


@router.post("/upload-csv", response_model=CSVUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Upload a CSV file with correos
    
    Acepta archivos separados por coma (,) o punto y coma (;)
    Detección automática del delimitador.
    
    Columnas requeridas:
    - Código
    - Razón social
    - Tipo de tercero
    - Número identificación
    - Email
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos CSV"
        )
    
    # Leer contenido del archivo
    content = await file.read()
    
    # Intentar diferentes codificaciones
    content_str = None
    used_encoding = None
    for encoding in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            content_str = content.decode(encoding)
            used_encoding = encoding
            break
        except UnicodeDecodeError:
            continue
    
    if content_str is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo decodificar el archivo. Use UTF-8 o Latin-1"
        )
    
    # Dividir en líneas y detectar delimitador
    lines = content_str.strip().split('\n')
    
    if not lines:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo CSV está vacío"
        )
    
    # Detectar delimitador usando la primera línea (headers)
    first_line = lines[0]
    delimiter = detect_delimiter(first_line)
    
    # Parsear CSV con el delimitador detectado
    try:
        reader = csv.reader(io.StringIO(content_str), delimiter=delimiter)
        rows = list(reader)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al parsear CSV: {str(e)}"
        )
    
    if len(rows) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo CSV debe tener al menos una fila de encabezados y una de datos"
        )
    
    # Obtener headers
    headers = [h.strip().strip('"').strip("'") for h in rows[0]]
    
    if not headers or all(h == '' for h in headers):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo CSV no tiene encabezados válidos"
        )
    
    # Validar que tengamos exactamente 5 columnas
    if len(headers) != 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El CSV debe tener exactamente 5 columnas. Se encontraron {len(headers)} columnas: {', '.join(headers)}"
        )
    
    # Encontrar índices de columnas
    col_indices = {}
    missing_columns = []
    
    for col_key, possible_names in REQUIRED_COLUMNS.items():
        idx = find_column_index(headers, possible_names)
        if idx >= 0:
            col_indices[col_key] = idx
        else:
            missing_columns.append(col_key)
    
    # Email es obligatorio
    if 'email' not in col_indices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La columna 'Email' es obligatoria. Nombres aceptados: email, correo, e-mail, mail"
        )
    
    # Advertir sobre columnas faltantes (no bloqueante)
    warnings = []
    if missing_columns:
        warnings.append(f"Columnas no detectadas: {', '.join(missing_columns)}. Algunos campos quedarán vacíos.")
    
    # Procesar filas
    total_processed = 0
    total_inserted = 0
    total_duplicates = 0
    total_invalid = 0
    errors = []
    
    # Obtener emails existentes
    existing_emails = set(email[0].lower() for email in db.query(Correo.email).all())
    
    correos_to_insert = []
    
    for row_num, row in enumerate(rows[1:], start=2):  # Empezar en 2 (1 es header)
        total_processed += 1
        
        try:
            # Validar que la fila tenga el número correcto de columnas
            if len(row) != len(headers):
                errors.append(f"Fila {row_num}: Número incorrecto de columnas. Esperadas {len(headers)}, encontradas {len(row)}")
                total_invalid += 1
                continue
            
            # Limpiar valores de la fila
            row_values = [str(val).strip().strip('"').strip("'") if val else '' for val in row]
            
            # Extraer email (obligatorio)
            email_idx = col_indices.get('email')
            email = row_values[email_idx] if email_idx is not None and email_idx < len(row_values) else ''
            
            if not email:
                errors.append(f"Fila {row_num}: Email vacío")
                total_invalid += 1
                continue
            
            email = email.lower()
            
            # Validar formato de email
            if not validate_email(email):
                errors.append(f"Fila {row_num}: Formato de email inválido '{email}'")
                total_invalid += 1
                continue
            
            # Verificar duplicados
            if email in existing_emails:
                total_duplicates += 1
                continue
            
            # Extraer otros campos
            codigo = row_values[col_indices['codigo']] if 'codigo' in col_indices and col_indices['codigo'] < len(row_values) else None
            razon_social = row_values[col_indices['razon_social']] if 'razon_social' in col_indices and col_indices['razon_social'] < len(row_values) else None
            tipo_tercero = row_values[col_indices['tipo_tercero']] if 'tipo_tercero' in col_indices and col_indices['tipo_tercero'] < len(row_values) else None
            numero_identificacion = row_values[col_indices['numero_identificacion']] if 'numero_identificacion' in col_indices and col_indices['numero_identificacion'] < len(row_values) else None
            
            # Limpiar valores vacíos
            codigo = codigo if codigo and codigo.strip() else None
            razon_social = razon_social if razon_social and razon_social.strip() else None
            tipo_tercero = tipo_tercero if tipo_tercero and tipo_tercero.strip() else None
            numero_identificacion = numero_identificacion if numero_identificacion and numero_identificacion.strip() else None
            
            # Crear objeto Correo
            correo = Correo(
                codigo=codigo,
                razon_social=razon_social,
                tipo_tercero=tipo_tercero,
                numero_identificacion=numero_identificacion,
                email=email
            )
            
            correos_to_insert.append(correo)
            existing_emails.add(email)
            total_inserted += 1
            
        except Exception as e:
            errors.append(f"Fila {row_num}: {str(e)}")
            total_invalid += 1
    
    # Insertar en lote
    if correos_to_insert:
        db.bulk_save_objects(correos_to_insert)
        db.commit()
    
    # Construir mensaje de respuesta
    message = f"CSV procesado correctamente. Insertados {total_inserted} registros."
    if warnings:
        message += f" Advertencias: {'; '.join(warnings)}"
    
    return CSVUploadResponse(
        message=message,
        total_processed=total_processed,
        total_inserted=total_inserted,
        total_duplicates=total_duplicates,
        total_invalid=total_invalid,
        errors=errors[:50]  # Limitar errores a los primeros 50
    )


@router.post("/validate-emails", response_model=dict)
async def validate_emails(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Validate all emails in the database and return invalid ones"""
    correos = db.query(Correo).all()
    
    invalid_emails = []
    for correo in correos:
        if not validate_email(correo.email):
            invalid_emails.append({
                "id": correo.id,
                "email": correo.email,
                "razon_social": correo.razon_social
            })
    
    return {
        "total_checked": len(correos),
        "invalid_count": len(invalid_emails),
        "invalid_emails": invalid_emails
    }