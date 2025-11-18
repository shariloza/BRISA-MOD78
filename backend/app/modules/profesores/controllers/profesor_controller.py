from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.config.database import get_db
from app.modules.profesores.dto.profesor_dto import (
    ProfesorCreateDTO, ProfesorReadDTO, ProfesorFullDTO, ProfesorUpdateDTO,
    MateriaReadDTO, MateriaCreateDTO,
    CursoReadDTO, CursoCreateDTO,
    AsignacionCreateDTO, AsignacionReadDTO, AsignacionReadNombreDTO,
    CargoReadDTO,
    BloqueHorarioCreateDTO, BloqueHorarioReadDTO, BloqueHorarioUpdateDTO
)
from app.modules.profesores.services.profesor_service import (
    ProfesorService, MateriaService, CursoService, AsignacionService, 
    CargoService, BloqueHorarioService
)

router = APIRouter(prefix="/api/profesores", tags=["Profesores"])


# ============ ENDPOINTS ESTÁTICOS (PRIMERO) ============

# ---- PROFESORES ----
@router.post("/", response_model=ProfesorReadDTO, status_code=status.HTTP_201_CREATED)
def crear_profesor(profesor: dict, db: Session = Depends(get_db)):
    """
    Crea un nuevo profesor con sus datos personales
    
    **Datos de Persona:**
    - ci, nombres, apellido_paterno, apellido_materno
    - direccion, telefono, correo
    - id_cargo, estado_laboral, años_experiencia
    - fecha_ingreso, fecha_retiro, motivo_retiro
    
    **Datos de Profesor:**
    - especialidad, titulo_academico
    - nivel_enseñanza: foundation, primary, secondary, todos
    - observaciones_profesor
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
    completo: bool = Query(True, description="Si es True, incluye materias, cursos y carga horaria"),
    db: Session = Depends(get_db)
):
    """
    Lista todos los profesores
    
    - **completo=True**: Incluye materias, cursos asignados y horas semanales
    - **completo=False**: Solo datos básicos
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
    - **nivel**: inicial, primaria, secundaria
    """
    return MateriaService.crear_materia(db, materia)


@router.get("/materias", response_model=List[MateriaReadDTO])
def listar_materias(db: Session = Depends(get_db)):
    """Lista todas las materias disponibles"""
    return MateriaService.listar_materias(db)


# ---- CURSOS ----
@router.post("/cursos", response_model=CursoReadDTO, status_code=status.HTTP_201_CREATED)
def crear_curso(curso: CursoCreateDTO, db: Session = Depends(get_db)):
    """
    Crea un nuevo curso
    
    - **nombre_curso**: Nombre del curso
    - **nivel**: inicial, primaria, secundaria
    - **gestion**: Año de gestión
    """
    return CursoService.crear_curso(db, curso)


@router.get("/cursos", response_model=List[CursoReadDTO])
def listar_cursos(db: Session = Depends(get_db)):
    """Lista todos los cursos disponibles"""
    return CursoService.listar_cursos(db)


# ---- ASIGNACIONES ----
@router.post("/asignaciones", response_model=AsignacionReadDTO, status_code=status.HTTP_201_CREATED)
def asignar_materia(data: AsignacionCreateDTO, db: Session = Depends(get_db)):
    """
    Asigna una materia a un profesor en un curso específico
    
    - **id_profesor**: ID del profesor (tabla profesores)
    - **id_curso**: ID del curso
    - **id_materia**: ID de la materia
    """
    return AsignacionService.asignar_materia(db, data)


@router.get("/asignaciones", response_model=List[AsignacionReadDTO])
def listar_asignaciones(db: Session = Depends(get_db)):
    """Lista todas las asignaciones (profesor-curso-materia)"""
    return AsignacionService.listar_asignaciones(db)


@router.delete("/asignaciones", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_asignacion(
    id_profesor: int = Query(..., description="ID del profesor (tabla profesores)"),
    id_curso: int = Query(..., description="ID del curso"),
    id_materia: int = Query(..., description="ID de la materia"),
    db: Session = Depends(get_db)
):
    """
    Elimina una asignación específica
    
    Se deben proporcionar los tres IDs como query parameters:
    - id_profesor (de tabla profesores, NO personas)
    - id_curso
    - id_materia
    """
    AsignacionService.eliminar_asignacion(db, id_profesor, id_curso, id_materia)
    return None


# ---- CARGOS ----
@router.get("/cargos", response_model=List[CargoReadDTO], tags=["Cargos"])
def listar_cargos(db: Session = Depends(get_db)):
    """Lista todos los cargos disponibles"""
    return CargoService.listar_cargos(db)


# ---- BLOQUES HORARIOS ----
@router.post("/bloques", response_model=BloqueHorarioReadDTO, status_code=status.HTTP_201_CREATED, 
             tags=["Horarios"])
def crear_bloque_horario(bloque: BloqueHorarioCreateDTO, db: Session = Depends(get_db)):
    """
    Crea un bloque horario para un profesor
    
    - **id_profesor**: ID del profesor (debe tener la asignación previamente)
    - **id_curso**: ID del curso
    - **id_materia**: ID de la materia
    - **dia_semana**: lunes, martes, miercoles, jueves, viernes, sabado
    - **hora_inicio**: Hora de inicio (formato: "08:00" o "08:00:00")
    - **hora_fin**: Hora de fin (formato: "10:00" o "10:00:00")
    - **gestion**: Año (default: 2025)
    - **observaciones**: Texto opcional
    
    Ejemplo:
    ```json
    {
      "id_profesor": 1,
      "id_curso": 1,
      "id_materia": 1,
      "dia_semana": "lunes",
      "hora_inicio": "08:00",
      "hora_fin": "10:00",
      "gestion": "2025",
      "observaciones": "Bloque normal"
    }
    ```
    
    Valida:
    - Que exista la asignación profesor-curso-materia
    - Que no haya conflictos de horario
    """
    return BloqueHorarioService.crear_bloque(db, bloque)


@router.get("/bloques", response_model=List[BloqueHorarioReadDTO], tags=["Horarios"])
def listar_bloques_horarios(
    gestion: Optional[str] = Query(None, description="Filtrar por gestión"),
    db: Session = Depends(get_db)
):
    """
    Lista todos los bloques horarios
    
    Opcionalmente filtrado por gestión
    """
    return BloqueHorarioService.listar_bloques(db, gestion)


# ---- VISTAS SQL ----
@router.get("/vistas/bloques-profesor", tags=["Vistas"])
def obtener_vista_bloques_profesor(
    id_persona: Optional[int] = Query(None, description="Filtrar por ID de persona"),
    gestion: Optional[str] = Query(None, description="Filtrar por gestión"),
    db: Session = Depends(get_db)
):
    """
    Obtiene datos de la vista vista_bloques_profesor
    
    Retorna información detallada de bloques con:
    - Datos del profesor
    - Horas por bloque
    - Materia, curso y nivel
    """
    return BloqueHorarioService.obtener_vista_bloques_profesor(db, id_persona, gestion)


@router.get("/vistas/carga-horaria", tags=["Vistas"])
def obtener_vista_carga_horaria(
    id_persona: Optional[int] = Query(None, description="Filtrar por ID de persona"),
    gestion: Optional[str] = Query(None, description="Filtrar por gestión"),
    db: Session = Depends(get_db)
):
    """
    Obtiene datos de la vista vista_carga_horaria_profesores
    
    Retorna resumen de:
    - Total de bloques
    - Carga horaria semanal
    - Materias y cursos asignados
    """
    return BloqueHorarioService.obtener_vista_carga_horaria(db, id_persona, gestion)


@router.get("/vistas/horario-semanal", tags=["Vistas"])
def obtener_vista_horario_semanal(
    id_persona: Optional[int] = Query(None, description="Filtrar por ID de persona"),
    gestion: Optional[str] = Query(None, description="Filtrar por gestión"),
    db: Session = Depends(get_db)
):
    """
    Obtiene datos de la vista vista_horario_semanal_profesor
    
    Retorna el horario organizado por días de la semana
    """
    return BloqueHorarioService.obtener_vista_horario_semanal(db, id_persona, gestion)


# ============ ENDPOINTS DINÁMICOS (DESPUÉS) ============

# ---- PROFESORES ----
@router.get("/{id_persona}", response_model=ProfesorReadDTO)
def obtener_profesor(id_persona: int, db: Session = Depends(get_db)):
    """
    Obtiene un profesor específico por su id_persona
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
    data: dict,
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


@router.delete("/{id_persona}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_profesor(id_persona: int, db: Session = Depends(get_db)):
    """
    Elimina un profesor y su registro de persona
    
    NOTA: También elimina en cascada:
    - Registro de profesor
    - Asignaciones
    - Bloques horarios
    """
    if not ProfesorService.eliminar_profesor(db, id_persona):
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return None


# ---- MATERIAS ----
@router.get("/materias/{id_materia}", response_model=MateriaReadDTO)
def obtener_materia(id_materia: int, db: Session = Depends(get_db)):
    """Obtiene una materia específica por su ID"""
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
    """Actualiza una materia"""
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
    
    NOTA: También elimina en cascada asignaciones y bloques horarios relacionados
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
    """Obtiene un curso específico por su ID"""
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
    """Actualiza un curso"""
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
    
    NOTA: También elimina en cascada asignaciones y bloques horarios relacionados
    """
    curso_eliminado = CursoService.eliminar_curso(db, id_curso)
    if not curso_eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {id_curso} no encontrado"
        )
    return curso_eliminado


# ---- ASIGNACIONES (POR PROFESOR) ----
@router.get("/{id_persona}/asignaciones", response_model=List[AsignacionReadNombreDTO])
def listar_asignaciones_profesor(id_persona: int, db: Session = Depends(get_db)):
    """
    Lista todas las asignaciones de un profesor con nombres descriptivos
    
    Retorna: nombre del profesor, curso y materia
    
    NOTA: Recibe id_persona pero internamente busca el id_profesor correspondiente
    """
    # Obtener el profesor para conseguir su id_profesor
    profesor = ProfesorService.obtener_profesor(db, id_persona)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    return AsignacionService.listar_por_profesor(db, profesor.id_profesor)


# ---- CARGOS (DINÁMICA) ----
@router.get("/cargos/{id_cargo}", response_model=CargoReadDTO, tags=["Cargos"])
def obtener_cargo(id_cargo: int, db: Session = Depends(get_db)):
    """Obtiene un cargo específico por su ID"""
    cargo = CargoService.obtener_cargo(db, id_cargo)
    if not cargo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cargo con ID {id_cargo} no encontrado"
        )
    return cargo


# ---- BLOQUES HORARIOS (DINÁMICA) ----
@router.get("/bloques/{id_bloque}", response_model=BloqueHorarioReadDTO, tags=["Horarios"])
def obtener_bloque_horario(id_bloque: int, db: Session = Depends(get_db)):
    """Obtiene un bloque horario específico"""
    bloque = BloqueHorarioService.obtener_bloque(db, id_bloque)
    if not bloque:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bloque horario con ID {id_bloque} no encontrado"
        )
    return bloque


@router.put("/bloques/{id_bloque}", response_model=BloqueHorarioReadDTO, tags=["Horarios"])
def actualizar_bloque_horario(
    id_bloque: int,
    data: BloqueHorarioUpdateDTO,
    db: Session = Depends(get_db)
):
    """
    Actualiza un bloque horario
    
    Valida que no se generen conflictos de horario
    """
    bloque_actualizado = BloqueHorarioService.actualizar_bloque(db, id_bloque, data)
    if not bloque_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bloque horario con ID {id_bloque} no encontrado"
        )
    return bloque_actualizado


@router.delete("/bloques/{id_bloque}", status_code=status.HTTP_204_NO_CONTENT, tags=["Horarios"])
def eliminar_bloque_horario(id_bloque: int, db: Session = Depends(get_db)):
    """Elimina un bloque horario"""
    if not BloqueHorarioService.eliminar_bloque(db, id_bloque):
        raise HTTPException(
            status_code=404, 
            detail="Bloque horario no encontrado"
        )
    return None


@router.get("/{id_persona}/bloques", response_model=List[BloqueHorarioReadDTO], tags=["Horarios"])
def listar_bloques_profesor(
    id_persona: int,
    gestion: Optional[str] = Query(None, description="Filtrar por gestión"),
    db: Session = Depends(get_db)
):
    """
    Lista todos los bloques horarios de un profesor
    
    Opcionalmente filtrado por gestión
    
    NOTA: Recibe id_persona pero internamente busca el id_profesor correspondiente
    """
    profesor = ProfesorService.obtener_profesor(db, id_persona)
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    return BloqueHorarioService.listar_por_profesor(db, profesor.id_profesor, gestion)