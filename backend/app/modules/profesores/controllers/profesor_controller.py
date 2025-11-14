from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.modules.profesores.dto.profesor_dto import (
    ProfesorCreateDTO, ProfesorReadDTO, ProfesorFullDTO, ProfesorUpdateDTO,
    MateriaReadDTO, MateriaCreateDTO,
    CursoReadDTO, CursoCreateDTO,
    AsignacionCreateDTO, AsignacionReadDTO, AsignacionReadNombreDTO, AsignacionDeleteDTO,
    CargoReadDTO
)
from app.modules.profesores.services.profesor_service import (
    ProfesorService, MateriaService, CursoService, AsignacionService, CargoService
)

router = APIRouter(prefix="/api/profesores", tags=["Profesores"])


# ============ ENDPOINTS ESTÁTICOS (PRIMERO) ============

# ---- PROFESORES ----
@router.post("/", response_model=ProfesorReadDTO, status_code=status.HTTP_201_CREATED)
def crear_profesor(profesor: dict, db: Session = Depends(get_db)):
    """
    Crea un nuevo profesor
   
    - **ci**: Cédula de identidad (único)
    - **nombres**: Nombres del profesor
    - **apellido_paterno**: Apellido paterno
    - **correo**: Correo electrónico (único)
    - **estado_laboral**: activo, retirado, suspendido, etc.
    """
    try:
        validated_data = ProfesorCreateDTO(**profesor)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Datos inválidos: {str(e)}"
        )
    return ProfesorService.crear_profesor(db, validated_data)

@router.get("/", response_model=List[ProfesorFullDTO])
def listar_profesores(
    completo: bool = Query(True, description="Si es True, incluye materias y cursos asignados"),
    db: Session = Depends(get_db)
):
    """
    Lista todos los profesores
   
    - Si **completo=True**: Incluye las materias y cursos asignados
    - Si **completo=False**: Solo datos básicos del profesor
    """
    if completo:
        return ProfesorService.listar_profesores_completo(db)
    else:
        return ProfesorService.listar_profesores(db)


# ---- MATERIAS ----
@router.post("/materias", response_model=MateriaReadDTO, status_code=status.HTTP_201_CREATED)
def crear_materia(materia: MateriaCreateDTO, db: Session = Depends(get_db)):
    """
    Crea una nueva materia
   
    - **nombre_materia**: Nombre de la materia
    - **nivel**: Nivel educativo (primaria, secundaria, etc.)
    """
    return MateriaService.crear_materia(db, materia)

@router.get("/materias", response_model=List[MateriaReadDTO])
def listar_materias(db: Session = Depends(get_db)):
    """
    Lista todas las materias disponibles
    """
    return MateriaService.listar_materias(db)


# ---- CURSOS ----
@router.post("/cursos", response_model=CursoReadDTO, status_code=status.HTTP_201_CREATED)
def crear_curso(curso: CursoCreateDTO, db: Session = Depends(get_db)):
    """
    Crea un nuevo curso
   
    - **nombre_curso**: Nombre del curso
    - **nivel**: Nivel educativo
    - **gestion**: Año de gestión
    """
    return CursoService.crear_curso(db, curso)

@router.get("/cursos", response_model=List[CursoReadDTO])
def listar_cursos(db: Session = Depends(get_db)):
    """
    Lista todos los cursos disponibles
    """
    return CursoService.listar_cursos(db)


# ---- ASIGNACIONES ----
@router.post("/asignaciones", response_model=AsignacionReadDTO, status_code=status.HTTP_201_CREATED)
def asignar_materia(data: AsignacionCreateDTO, db: Session = Depends(get_db)):
    """
    Asigna una materia a un profesor en un curso específico
   
    - **id_profesor**: ID del profesor
    - **id_curso**: ID del curso
    - **id_materia**: ID de la materia
    """
    return AsignacionService.asignar_materia(db, data)

@router.get("/asignaciones", response_model=List[AsignacionReadDTO])
def listar_asignaciones(db: Session = Depends(get_db)):
    """
    Lista todas las asignaciones (profesor-curso-materia)
    """
    return AsignacionService.listar_asignaciones(db)

@router.delete("/asignaciones", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_asignacion(
    id_profesor: int = Query(..., description="ID del profesor"),
    id_curso: int = Query(..., description="ID del curso"),
    id_materia: int = Query(..., description="ID de la materia"),
    db: Session = Depends(get_db)
):
    """
    Elimina una asignación específica
   
    Se deben proporcionar los tres IDs como query parameters
    """
    AsignacionService.eliminar_asignacion(db, id_profesor, id_curso, id_materia)
    return None


# ---- CARGOS ----
@router.get("/cargos", response_model=List[CargoReadDTO], tags=["Cargos"])
def listar_cargos(db: Session = Depends(get_db)):
    """
    Lista todos los cargos disponibles
    """
    return CargoService.listar_cargos(db)


# ============ ENDPOINTS DINÁMICOS (DESPUÉS) ============

# ---- PROFESORES ----
@router.get("/{id_persona}", response_model=ProfesorReadDTO)
def obtener_profesor(id_persona: int, db: Session = Depends(get_db)):
    """
    Obtiene un profesor específico por su ID
    """
    profesor = ProfesorService.obtener_profesor(db, id_persona)
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesor con ID {id_persona} no encontrado"
        )
    return profesor

@router.put("/{id_persona}", response_model=ProfesorReadDTO)
def actualizar_profesor(
    id_persona: int,
    data: dict, # Aceptar dict para más flexibilidad
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un profesor
   
    - Solo se actualizan los campos proporcionados
    - CI y correo deben ser únicos
    """
    try:
        validated_data = ProfesorUpdateDTO(**data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Datos inválidos: {str(e)}"
        )
   
    profesor_actualizado = ProfesorService.actualizar_profesor(db, id_persona, validated_data)
    if not profesor_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesor con ID {id_persona} no encontrado"
        )
    return profesor_actualizado

@router.delete("/{id_persona}", response_model=ProfesorReadDTO)
def eliminar_profesor(id_persona: int, db: Session = Depends(get_db)):
    """
    Elimina un profesor
   
    - Las asignaciones del profesor se eliminan en cascsin cascada
    """
    profesor_eliminado = ProfesorService.eliminar_profesor(db, id_persona)
    if not profesor_eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesor con ID {id_persona} no encontrado"
        )
    return profesor_eliminado


# ---- MATERIAS ----
@router.get("/materias/{id_materia}", response_model=MateriaReadDTO)
def obtener_materia(id_materia: int, db: Session = Depends(get_db)):
    """
    Obtiene una materia específica por su ID
    """
    materia = MateriaService.obtener_materia(db, id_materia)
    if not materia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Materia con ID {id_materia} no encontrada"
        )
    return materia

@router.put("/materias/{id_materia}", response_model=MateriaReadDTO)
def actualizar_materia(
    id_materia: int,
    data: MateriaCreateDTO,
    db: Session = Depends(get_db)
):
    """
    Actualiza una materia
    """
    materia_actualizada = MateriaService.actualizar_materia(db, id_materia, data)
    if not materia_actualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Materia con ID {id_materia} no encontrada"
        )
    return materia_actualizada

@router.delete("/materias/{id_materia}", response_model=MateriaReadDTO)
def eliminar_materia(id_materia: int, db: Session = Depends(get_db)):
    """
    Elimina una materia
    """
    materia_eliminada = MateriaService.eliminar_materia(db, id_materia)
    if not materia_eliminada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Materia con ID {id_materia} no encontrada"
        )
    return materia_eliminada


# ---- CURSOS ----
@router.get("/cursos/{id_curso}", response_model=CursoReadDTO)
def obtener_curso(id_curso: int, db: Session = Depends(get_db)):
    """
    Obtiene un curso específico por su ID
    """
    curso = CursoService.obtener_curso(db, id_curso)
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {id_curso} no encontrado"
        )
    return curso

@router.put("/cursos/{id_curso}", response_model=CursoReadDTO)
def actualizar_curso(
    id_curso: int,
    data: CursoCreateDTO,
    db: Session = Depends(get_db)
):
    """
    Actualiza un curso
    """
    curso_actualizado = CursoService.actualizar_curso(db, id_curso, data)
    if not curso_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {id_curso} no encontrado"
        )
    return curso_actualizado

@router.delete("/cursos/{id_curso}", response_model=CursoReadDTO)
def eliminar_curso(id_curso: int, db: Session = Depends(get_db)):
    """
    Elimina un curso
    """
    curso_eliminado = CursoService.eliminar_curso(db, id_curso)
    if not curso_eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {id_curso} no encontrado"
        )
    return curso_eliminado


# ---- ASIGNACIONES (DINÁMICA) ----
@router.get("/{id_persona}/asignaciones", response_model=List[AsignacionReadNombreDTO])
def listar_asignaciones_profesor_alt(id_persona: int, db: Session = Depends(get_db)):
    """
    Lista todas las asignaciones de un profesor específico con nombres descriptivos
    (Ruta alternativa para compatibilidad con frontend)
   
    Retorna: nombre del profesor, curso y materia
    """
    return AsignacionService.listar_por_profesor(db, id_persona)


# ---- CARGOS (DINÁMICA) ----
@router.get("/cargos/{id_cargo}", response_model=CargoReadDTO, tags=["Cargos"])
def obtener_cargo(id_cargo: int, db: Session = Depends(get_db)):
    """
    Obtiene un cargo específico por su ID
    """
    cargo = CargoService.obtener_cargo(db, id_cargo)
    if not cargo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cargo con ID {id_cargo} no encontrado"
        )
    return cargo