from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.modules.profesores.dto.profesor_dto import ProfesorCreateDTO, ProfesorReadDTO, MateriaReadDTO, CursoReadDTO, AsignacionCreateDTO, AsignacionReadDTO, AsignacionReadNombreDTO, ProfesorFullDTO
from app.modules.profesores.services.profesor_service import ProfesorService, MateriaService, CursoService, AsignacionService

router = APIRouter(prefix="/api/profesores", tags=["Profesores"])

@router.post("/", response_model=ProfesorReadDTO)
def crear_profesor(profesor: ProfesorCreateDTO, db: Session = Depends(get_db)):
    return ProfesorService.crear_profesor(db, profesor)

# @router.get("/", response_model=List[dict])
# def listar_profesores(db: Session = Depends(get_db)):
#     """Lista profesores con sus materias y cursos asignados"""
#     return ProfesorService.listar_profesores(db)

@router.get("/", response_model=List[ProfesorFullDTO])
def listar_profesores(db: Session = Depends(get_db)):
    """
    Lista profesores con sus materias, cursos y estado laboral
    """
    return ProfesorService.listar_profesores_completo(db)

# Endpoints para materias
@router.get("/materias", response_model=List[MateriaReadDTO])
def listar_materias(db: Session = Depends(get_db)):
    return MateriaService.listar_materias(db)

# Endpoints para cursos
@router.get("/cursos", response_model=List[CursoReadDTO])
def listar_cursos(db: Session = Depends(get_db)):
    return CursoService.listar_cursos(db)

@router.post("/asignaciones", response_model=AsignacionReadDTO)
def asignar_materia(data: AsignacionCreateDTO, db: Session = Depends(get_db)):
    return AsignacionService.asignar_materia(db, data)

@router.get("/asignaciones", response_model=List[AsignacionReadDTO])
def listar_asignaciones(db: Session = Depends(get_db)):
    return AsignacionService.listar_asignaciones(db)

#Por IDS
# @router.get("/asignaciones/{id_profesor}", response_model=List[AsignacionReadDTO])
# def listar_asignaciones_profesor(id_profesor: int, db: Session = Depends(get_db)):
#     return AsignacionService.listar_por_profesor(db, id_profesor)

@router.get("/asignaciones/{id_profesor}", response_model=List[AsignacionReadNombreDTO])
def listar_asignaciones_profesor(id_profesor: int, db: Session = Depends(get_db)):
    return AsignacionService.listar_por_profesor(db, id_profesor)

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


