"""
Inventario TI router - CRUD for Equipos, Memorias RAM, Almacenamiento, Salida Bodega
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Equipo, MemoriaRAM, Almacenamiento, SalidaBodega
from app.schemas import (
    EquipoCreate, EquipoUpdate, EquipoResponse, EquipoListResponse,
    MemoriaRAMCreate, MemoriaRAMUpdate, MemoriaRAMResponse, MemoriaRAMListResponse,
    AlmacenamientoCreate, AlmacenamientoUpdate, AlmacenamientoResponse, AlmacenamientoListResponse,
    SalidaBodegaCreate, SalidaBodegaUpdate, SalidaBodegaResponse, SalidaBodegaListResponse,
    MessageResponse
)
from app.auth import get_current_user
from app.schemas import UserResponse

router = APIRouter(
    prefix="/inventario",
    tags=["Inventario TI"]
)


# ==========================================
# EQUIPOS
# ==========================================

@router.get("/equipos", response_model=EquipoListResponse)
async def list_equipos(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """List all equipos with pagination and search"""
    query = db.query(Equipo)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Equipo.nombre_equipo.ilike(search_term),
                Equipo.puesto.ilike(search_term),
                Equipo.nombre_usuario.ilike(search_term),
                Equipo.empleado.ilike(search_term),
                Equipo.marca.ilike(search_term),
                Equipo.estado_licencia.ilike(search_term),
            )
        )

    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    items = query.order_by(Equipo.id.desc()).offset(offset).limit(page_size).all()

    return EquipoListResponse(
        items=[EquipoResponse.model_validate(item) for item in items],
        total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/equipos/{equipo_id}", response_model=EquipoResponse)
async def get_equipo(
    equipo_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific equipo by ID"""
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo {equipo_id} no encontrado")
    return EquipoResponse.model_validate(equipo)


@router.post("/equipos", response_model=EquipoResponse, status_code=status.HTTP_201_CREATED)
async def create_equipo(
    data: EquipoCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new equipo"""
    equipo = Equipo(**data.model_dump())
    db.add(equipo)
    db.commit()
    db.refresh(equipo)
    return EquipoResponse.model_validate(equipo)


@router.put("/equipos/{equipo_id}", response_model=EquipoResponse)
async def update_equipo(
    equipo_id: int,
    data: EquipoUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update an equipo"""
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo {equipo_id} no encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(equipo, key, value)
    db.commit()
    db.refresh(equipo)
    return EquipoResponse.model_validate(equipo)


@router.delete("/equipos/{equipo_id}", response_model=MessageResponse)
async def delete_equipo(
    equipo_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete an equipo"""
    equipo = db.query(Equipo).filter(Equipo.id == equipo_id).first()
    if not equipo:
        raise HTTPException(status_code=404, detail=f"Equipo {equipo_id} no encontrado")
    db.delete(equipo)
    db.commit()
    return MessageResponse(message=f"Equipo {equipo_id} eliminado correctamente")


# ==========================================
# MEMORIAS RAM
# ==========================================

@router.get("/memorias-ram", response_model=MemoriaRAMListResponse)
async def list_memorias_ram(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """List all memorias RAM with pagination and search"""
    query = db.query(MemoriaRAM)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                MemoriaRAM.tipo.ilike(search_term),
                MemoriaRAM.capacidad.ilike(search_term),
                MemoriaRAM.equipo.ilike(search_term),
                MemoriaRAM.observaciones.ilike(search_term),
            )
        )

    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    items = query.order_by(MemoriaRAM.id.desc()).offset(offset).limit(page_size).all()

    return MemoriaRAMListResponse(
        items=[MemoriaRAMResponse.model_validate(item) for item in items],
        total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/memorias-ram/{memoria_id}", response_model=MemoriaRAMResponse)
async def get_memoria_ram(
    memoria_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific memoria RAM by ID"""
    memoria = db.query(MemoriaRAM).filter(MemoriaRAM.id == memoria_id).first()
    if not memoria:
        raise HTTPException(status_code=404, detail=f"Memoria RAM {memoria_id} no encontrada")
    return MemoriaRAMResponse.model_validate(memoria)


@router.post("/memorias-ram", response_model=MemoriaRAMResponse, status_code=status.HTTP_201_CREATED)
async def create_memoria_ram(
    data: MemoriaRAMCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new memoria RAM"""
    memoria = MemoriaRAM(**data.model_dump())
    db.add(memoria)
    db.commit()
    db.refresh(memoria)
    return MemoriaRAMResponse.model_validate(memoria)


@router.put("/memorias-ram/{memoria_id}", response_model=MemoriaRAMResponse)
async def update_memoria_ram(
    memoria_id: int,
    data: MemoriaRAMUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a memoria RAM"""
    memoria = db.query(MemoriaRAM).filter(MemoriaRAM.id == memoria_id).first()
    if not memoria:
        raise HTTPException(status_code=404, detail=f"Memoria RAM {memoria_id} no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(memoria, key, value)
    db.commit()
    db.refresh(memoria)
    return MemoriaRAMResponse.model_validate(memoria)


@router.delete("/memorias-ram/{memoria_id}", response_model=MessageResponse)
async def delete_memoria_ram(
    memoria_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a memoria RAM"""
    memoria = db.query(MemoriaRAM).filter(MemoriaRAM.id == memoria_id).first()
    if not memoria:
        raise HTTPException(status_code=404, detail=f"Memoria RAM {memoria_id} no encontrada")
    db.delete(memoria)
    db.commit()
    return MessageResponse(message=f"Memoria RAM {memoria_id} eliminada correctamente")


# ==========================================
# ALMACENAMIENTO
# ==========================================

@router.get("/almacenamiento", response_model=AlmacenamientoListResponse)
async def list_almacenamiento(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """List all almacenamiento with pagination and search"""
    query = db.query(Almacenamiento)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Almacenamiento.tipo.ilike(search_term),
                Almacenamiento.capacidad.ilike(search_term),
                Almacenamiento.marca.ilike(search_term),
                Almacenamiento.asignado_por.ilike(search_term),
                Almacenamiento.responsable.ilike(search_term),
            )
        )

    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    items = query.order_by(Almacenamiento.id.desc()).offset(offset).limit(page_size).all()

    return AlmacenamientoListResponse(
        items=[AlmacenamientoResponse.model_validate(item) for item in items],
        total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/almacenamiento/{alm_id}", response_model=AlmacenamientoResponse)
async def get_almacenamiento(
    alm_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific almacenamiento by ID"""
    alm = db.query(Almacenamiento).filter(Almacenamiento.id == alm_id).first()
    if not alm:
        raise HTTPException(status_code=404, detail=f"Almacenamiento {alm_id} no encontrado")
    return AlmacenamientoResponse.model_validate(alm)


@router.post("/almacenamiento", response_model=AlmacenamientoResponse, status_code=status.HTTP_201_CREATED)
async def create_almacenamiento(
    data: AlmacenamientoCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new almacenamiento"""
    alm = Almacenamiento(**data.model_dump())
    db.add(alm)
    db.commit()
    db.refresh(alm)
    return AlmacenamientoResponse.model_validate(alm)


@router.put("/almacenamiento/{alm_id}", response_model=AlmacenamientoResponse)
async def update_almacenamiento(
    alm_id: int,
    data: AlmacenamientoUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update an almacenamiento"""
    alm = db.query(Almacenamiento).filter(Almacenamiento.id == alm_id).first()
    if not alm:
        raise HTTPException(status_code=404, detail=f"Almacenamiento {alm_id} no encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(alm, key, value)
    db.commit()
    db.refresh(alm)
    return AlmacenamientoResponse.model_validate(alm)


@router.delete("/almacenamiento/{alm_id}", response_model=MessageResponse)
async def delete_almacenamiento(
    alm_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete an almacenamiento"""
    alm = db.query(Almacenamiento).filter(Almacenamiento.id == alm_id).first()
    if not alm:
        raise HTTPException(status_code=404, detail=f"Almacenamiento {alm_id} no encontrado")
    db.delete(alm)
    db.commit()
    return MessageResponse(message=f"Almacenamiento {alm_id} eliminado correctamente")


# ==========================================
# SALIDA BODEGA
# ==========================================

@router.get("/salida-bodega", response_model=SalidaBodegaListResponse)
async def list_salida_bodega(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """List all salida bodega with pagination and search"""
    query = db.query(SalidaBodega)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                SalidaBodega.periferico.ilike(search_term),
                SalidaBodega.marca.ilike(search_term),
                SalidaBodega.modelo_serie.ilike(search_term),
                SalidaBodega.asignado.ilike(search_term),
                SalidaBodega.retirado_por.ilike(search_term),
            )
        )

    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    items = query.order_by(SalidaBodega.id.desc()).offset(offset).limit(page_size).all()

    return SalidaBodegaListResponse(
        items=[SalidaBodegaResponse.model_validate(item) for item in items],
        total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@router.get("/salida-bodega/{salida_id}", response_model=SalidaBodegaResponse)
async def get_salida_bodega(
    salida_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Get a specific salida bodega by ID"""
    salida = db.query(SalidaBodega).filter(SalidaBodega.id == salida_id).first()
    if not salida:
        raise HTTPException(status_code=404, detail=f"Salida Bodega {salida_id} no encontrada")
    return SalidaBodegaResponse.model_validate(salida)


@router.post("/salida-bodega", response_model=SalidaBodegaResponse, status_code=status.HTTP_201_CREATED)
async def create_salida_bodega(
    data: SalidaBodegaCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new salida bodega"""
    salida = SalidaBodega(**data.model_dump())
    db.add(salida)
    db.commit()
    db.refresh(salida)
    return SalidaBodegaResponse.model_validate(salida)


@router.put("/salida-bodega/{salida_id}", response_model=SalidaBodegaResponse)
async def update_salida_bodega(
    salida_id: int,
    data: SalidaBodegaUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a salida bodega"""
    salida = db.query(SalidaBodega).filter(SalidaBodega.id == salida_id).first()
    if not salida:
        raise HTTPException(status_code=404, detail=f"Salida Bodega {salida_id} no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(salida, key, value)
    db.commit()
    db.refresh(salida)
    return SalidaBodegaResponse.model_validate(salida)


@router.delete("/salida-bodega/{salida_id}", response_model=MessageResponse)
async def delete_salida_bodega(
    salida_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a salida bodega"""
    salida = db.query(SalidaBodega).filter(SalidaBodega.id == salida_id).first()
    if not salida:
        raise HTTPException(status_code=404, detail=f"Salida Bodega {salida_id} no encontrada")
    db.delete(salida)
    db.commit()
    return MessageResponse(message=f"Salida Bodega {salida_id} eliminada correctamente")