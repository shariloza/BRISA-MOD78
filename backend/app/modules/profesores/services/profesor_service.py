from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from collections import defaultdict
from fastapi import HTTPException
from typing import List, Optional

from app.modules.profesores.dto.profesor_dto import (
    ProfesorCreateDTO, ProfesorReadDTO, ProfesorFullDTO, ProfesorUpdateDTO,
    MateriaReadDTO, MateriaCreateDTO,
    CursoReadDTO, CursoCreateDTO,
    AsignacionCreateDTO, AsignacionReadDTO, AsignacionReadNombreDTO,
    CargoReadDTO
)
from app.modules.profesores.repositories.profesor_repository import (
    ProfesorRepository, MateriaRepository, CursoRepository, 
    AsignacionRepository, CargoRepository
)
from app.modules.profesores.models.profesor_models import Profesor, Curso, Materia

# ============ PROFESOR SERVICE ============
class ProfesorService:

    @staticmethod
    def crear_profesor(db: Session, data: ProfesorCreateDTO) -> ProfesorReadDTO:
        """Crea un nuevo profesor"""
        # Validar CI único
        if ProfesorRepository.exists_by_ci(db, data.ci):
            raise HTTPException(status_code=400, detail="Ya existe un profesor con este CI")
        
        # Validar correo único
        if ProfesorRepository.exists_by_correo(db, data.correo):
            raise HTTPException(status_code=400, detail="Ya existe un profesor con este correo")
        
        # Validar cargo si se proporciona
        if data.id_cargo:
            cargo = CargoRepository.get_by_id(db, data.id_cargo)
            if not cargo:
                raise HTTPException(status_code=404, detail="El cargo especificado no existe")
        
        try:
            profesor = ProfesorRepository.create(db, data.dict())
            return ProfesorService._build_profesor_read_dto(profesor)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al crear el profesor")

    @staticmethod
    def listar_profesores(db: Session) -> List[ProfesorReadDTO]:
        """Lista todos los profesores"""
        profesores = ProfesorRepository.get_all(db)
        return [ProfesorService._build_profesor_read_dto(p) for p in profesores]
    
    @staticmethod
    def listar_profesores_completo(db: Session) -> List[ProfesorFullDTO]:
        """Lista profesores con sus materias y cursos asignados"""
        profesores = ProfesorRepository.get_all(db)
        asignaciones = AsignacionRepository.get_all(db)

        # Mapear asignaciones por profesor
        prof_map = defaultdict(lambda: {"cursos": set(), "materias": set()})
        for a in asignaciones:
            prof_map[a.id_profesor]["cursos"].add(a.id_curso)
            prof_map[a.id_profesor]["materias"].add(a.id_materia)

        resultado = []
        for p in profesores:
            dto = ProfesorFullDTO.from_orm(p)
            dto.nombre_cargo = p.cargo.nombre_cargo if p.cargo else None

            # Obtener nombres únicos de cursos y materias
            if prof_map[p.id_persona]["cursos"]:
                cursos = CursoRepository.get_by_ids(
                    db, list(prof_map[p.id_persona]["cursos"])
                )
                dto.cursos = [c.nombre_curso for c in cursos]

            if prof_map[p.id_persona]["materias"]:
                materias = MateriaRepository.get_by_ids(
                    db, list(prof_map[p.id_persona]["materias"])
                )
                dto.materias = [m.nombre_materia for m in materias]

            resultado.append(dto)

        return resultado

    @staticmethod
    def obtener_profesor(db: Session, id_persona: int) -> Optional[ProfesorReadDTO]:
        """Obtiene un profesor por ID"""
        profesor = ProfesorRepository.get_by_id(db, id_persona)
        if not profesor:
            return None
        return ProfesorService._build_profesor_read_dto(profesor)

    @staticmethod
    def actualizar_profesor(db: Session, id_persona: int, data: ProfesorUpdateDTO) -> Optional[ProfesorReadDTO]:
        """Actualiza un profesor"""
        profesor = ProfesorRepository.get_by_id(db, id_persona)
        if not profesor:
            return None
        
        # Validar CI único (si se está cambiando)
        if data.ci and data.ci != profesor.ci:
            if ProfesorRepository.exists_by_ci(db, data.ci, exclude_id=id_persona):
                raise HTTPException(status_code=400, detail="Ya existe un profesor con este CI")
        
        # Validar correo único (si se está cambiando)
        if data.correo and data.correo != profesor.correo:
            if ProfesorRepository.exists_by_correo(db, data.correo, exclude_id=id_persona):
                raise HTTPException(status_code=400, detail="Ya existe un profesor con este correo")
        
        # Validar cargo si se proporciona
        if data.id_cargo:
            cargo = CargoRepository.get_by_id(db, data.id_cargo)
            if not cargo:
                raise HTTPException(status_code=404, detail="El cargo especificado no existe")
        
        try:
            profesor_actualizado = ProfesorRepository.update(db, profesor, data.dict(exclude_unset=True))
            return ProfesorService._build_profesor_read_dto(profesor_actualizado)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al actualizar el profesor")

    @staticmethod
    def eliminar_profesor(db: Session, id_persona: int) -> Optional[ProfesorReadDTO]:
        """Elimina un profesor"""
        profesor = ProfesorRepository.get_by_id(db, id_persona)
        if not profesor:
            return None
        
        profesor_eliminado = ProfesorRepository.delete(db, profesor)
        return ProfesorService._build_profesor_read_dto(profesor_eliminado)

    @staticmethod
    def _build_profesor_read_dto(profesor: Profesor) -> ProfesorReadDTO:
        """Construye un ProfesorReadDTO a partir de un modelo Profesor"""
        dto = ProfesorReadDTO.from_orm(profesor)
        dto.nombre_cargo = profesor.cargo.nombre_cargo if profesor.cargo else None
        return dto

# ============ MATERIA SERVICE ============
class MateriaService:

    @staticmethod
    def crear_materia(db: Session, data: MateriaCreateDTO) -> MateriaReadDTO:
        """Crea una nueva materia"""
        try:
            materia = MateriaRepository.create(db, data.dict())
            return MateriaReadDTO.from_orm(materia)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al crear la materia")

    @staticmethod
    def listar_materias(db: Session) -> List[MateriaReadDTO]:
        """Lista todas las materias"""
        materias = MateriaRepository.get_all(db)
        return [MateriaReadDTO.from_orm(m) for m in materias]

    @staticmethod
    def obtener_materia(db: Session, id_materia: int) -> Optional[MateriaReadDTO]:
        """Obtiene una materia por ID"""
        materia = MateriaRepository.get_by_id(db, id_materia)
        if not materia:
            return None
        return MateriaReadDTO.from_orm(materia)

    @staticmethod
    def actualizar_materia(db: Session, id_materia: int, data: MateriaCreateDTO) -> Optional[MateriaReadDTO]:
        """Actualiza una materia"""
        materia = MateriaRepository.get_by_id(db, id_materia)
        if not materia:
            return None
        
        try:
            materia_actualizada = MateriaRepository.update(db, materia, data.dict())
            return MateriaReadDTO.from_orm(materia_actualizada)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al actualizar la materia")

    @staticmethod
    def eliminar_materia(db: Session, id_materia: int) -> Optional[MateriaReadDTO]:
        """Elimina una materia"""
        materia = MateriaRepository.get_by_id(db, id_materia)
        if not materia:
            return None
        
        materia_eliminada = MateriaRepository.delete(db, materia)
        return MateriaReadDTO.from_orm(materia_eliminada)

# ============ CURSO SERVICE ============
class CursoService:

    @staticmethod
    def crear_curso(db: Session, data: CursoCreateDTO) -> CursoReadDTO:
        """Crea un nuevo curso"""
        try:
            curso = CursoRepository.create(db, data.dict())
            return CursoReadDTO.from_orm(curso)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al crear el curso")

    @staticmethod
    def listar_cursos(db: Session) -> List[CursoReadDTO]:
        """Lista todos los cursos"""
        cursos = CursoRepository.get_all(db)
        return [CursoReadDTO.from_orm(c) for c in cursos]

    @staticmethod
    def obtener_curso(db: Session, id_curso: int) -> Optional[CursoReadDTO]:
        """Obtiene un curso por ID"""
        curso = CursoRepository.get_by_id(db, id_curso)
        if not curso:
            return None
        return CursoReadDTO.from_orm(curso)

    @staticmethod
    def actualizar_curso(db: Session, id_curso: int, data: CursoCreateDTO) -> Optional[CursoReadDTO]:
        """Actualiza un curso"""
        curso = CursoRepository.get_by_id(db, id_curso)
        if not curso:
            return None
        
        try:
            curso_actualizado = CursoRepository.update(db, curso, data.dict())
            return CursoReadDTO.from_orm(curso_actualizado)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al actualizar el curso")

    @staticmethod
    def eliminar_curso(db: Session, id_curso: int) -> Optional[CursoReadDTO]:
        """Elimina un curso"""
        curso = CursoRepository.get_by_id(db, id_curso)
        if not curso:
            return None
        
        curso_eliminado = CursoRepository.delete(db, curso)
        return CursoReadDTO.from_orm(curso_eliminado)

# ============ ASIGNACIÓN SERVICE ============
class AsignacionService:

    @staticmethod
    def asignar_materia(db: Session, data: AsignacionCreateDTO) -> AsignacionReadDTO:
        """Crea una asignación de materia a profesor y curso"""
        # Validar que exista el profesor
        profesor = ProfesorRepository.get_by_id(db, data.id_profesor)
        if not profesor:
            raise HTTPException(status_code=404, detail="El profesor no existe")
        
        # Validar que exista el curso
        curso = CursoRepository.get_by_id(db, data.id_curso)
        if not curso:
            raise HTTPException(status_code=404, detail="El curso no existe")
        
        # Validar que exista la materia
        materia = MateriaRepository.get_by_id(db, data.id_materia)
        if not materia:
            raise HTTPException(status_code=404, detail="La materia no existe")
        
        try:
            asignacion = AsignacionRepository.create(db, data.dict())
            return AsignacionReadDTO.from_orm(asignacion)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al crear la asignación")

    @staticmethod
    def listar_asignaciones(db: Session) -> List[AsignacionReadDTO]:
        """Lista todas las asignaciones"""
        asignaciones = AsignacionRepository.get_all(db)
        return [AsignacionReadDTO.from_orm(a) for a in asignaciones]

    @staticmethod
    def listar_por_profesor(db: Session, id_profesor: int) -> List[AsignacionReadNombreDTO]:
        """Lista asignaciones de un profesor con nombres"""
        # Validar que exista el profesor
        profesor = ProfesorRepository.get_by_id(db, id_profesor)
        if not profesor:
            raise HTTPException(status_code=404, detail="El profesor no existe")
        
        asignaciones = AsignacionRepository.get_by_profesor_con_nombres(db, id_profesor)
        return [AsignacionReadNombreDTO.from_orm(a) for a in asignaciones]

    @staticmethod
    def eliminar_asignacion(db: Session, id_profesor: int, id_curso: int, id_materia: int) -> bool:
        """Elimina una asignación específica"""
        if not AsignacionRepository.exists(db, id_profesor, id_curso, id_materia):
            raise HTTPException(status_code=404, detail="La asignación no existe")
        
        return AsignacionRepository.delete(db, id_profesor, id_curso, id_materia)

# ============ CARGO SERVICE ============
class CargoService:

    @staticmethod
    def listar_cargos(db: Session) -> List[CargoReadDTO]:
        """Lista todos los cargos"""
        cargos = CargoRepository.get_all(db)
        return [CargoReadDTO.from_orm(c) for c in cargos]

    @staticmethod
    def obtener_cargo(db: Session, id_cargo: int) -> Optional[CargoReadDTO]:
        """Obtiene un cargo por ID"""
        cargo = CargoRepository.get_by_id(db, id_cargo)
        if not cargo:
            return None
        return CargoReadDTO.from_orm(cargo)