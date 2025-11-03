from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.modules.profesores.dto.profesor_dto import ProfesorCreateDTO, ProfesorReadDTO
from app.modules.profesores.services.profesor_service import ProfesorService

router = APIRouter(
    prefix="/api/profesores",
    tags=["Profesores"]
)

@router.post("/", response_model=ProfesorReadDTO)
def crear_profesor(profesor: ProfesorCreateDTO, db: Session = Depends(get_db)):
    return ProfesorService.crear_profesor(db, profesor)

@router.get("/", response_model=List[ProfesorReadDTO])
def listar_profesores(db: Session = Depends(get_db)):
    return ProfesorService.listar_profesores(db)

@router.get("/{id_persona}", response_model=ProfesorReadDTO)
def obtener_profesor(id_persona: int, db: Session = Depends(get_db)):
    profesor = ProfesorService.obtener_profesor(db, id_persona)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor

@router.put("/{id_persona}", response_model=ProfesorReadDTO)
def actualizar_profesor(id_persona: int, data: ProfesorCreateDTO, db: Session = Depends(get_db)):
    profesor_actualizado = ProfesorService.actualizar_profesor(db, id_persona, data.dict())
    if not profesor_actualizado:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor_actualizado

@router.delete("/{id_persona}", response_model=ProfesorReadDTO)
def eliminar_profesor(id_persona: int, db: Session = Depends(get_db)):
    profesor_eliminado = ProfesorService.eliminar_profesor(db, id_persona)
    if not profesor_eliminado:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor_eliminado
