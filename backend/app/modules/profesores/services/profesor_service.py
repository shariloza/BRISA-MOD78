from sqlalchemy.orm import Session
from app.modules.profesores.dto.profesor_dto import ProfesorCreateDTO, ProfesorReadDTO, MateriaReadDTO, CursoReadDTO, AsignacionCreateDTO, AsignacionReadDTO, AsignacionReadNombreDTO
from app.modules.profesores.repositories.profesor_repository import ProfesorRepository, MateriaRepository, CursoRepository, AsignacionRepository

class ProfesorService:

    @staticmethod
    def crear_profesor(db: Session, data: ProfesorCreateDTO):
        return ProfesorRepository.create(db, data.dict())

    @staticmethod
    def listar_profesores(db: Session):
        profesores = ProfesorRepository.get_all(db)
        result = []
        for p in profesores:
            dto = ProfesorReadDTO.from_orm(p)
            dto.nombre_cargo = p.cargo.nombre_cargo if p.cargo else None
            result.append(dto)
        return result

    @staticmethod
    def obtener_profesor(db: Session, id_persona: int):
        profesor = ProfesorRepository.get_by_id(db, id_persona)
        if not profesor:
            return None
        dto = ProfesorReadDTO.from_orm(profesor)
        dto.nombre_cargo = profesor.cargo.nombre_cargo if profesor.cargo else None
        return dto

    @staticmethod
    def actualizar_profesor(db: Session, id_persona: int, data: dict):
        profesor = ProfesorRepository.get_by_id(db, id_persona)
        if not profesor:
         return None
        profesor_actualizado = ProfesorRepository.update(db, profesor, data)
        dto = ProfesorReadDTO.from_orm(profesor_actualizado)
        dto.nombre_cargo = profesor_actualizado.cargo.nombre_cargo if profesor_actualizado.cargo else None
        return dto
        
       

    @staticmethod
    def eliminar_profesor(db: Session, id_persona: int):
        profesor = ProfesorRepository.get_by_id(db, id_persona)
        if not profesor:
            return None
        return ProfesorRepository.delete(db, profesor)

class MateriaService:

    @staticmethod
    def listar_materias(db: Session):
        materias = MateriaRepository.get_all(db)
        return [MateriaReadDTO.from_orm(m) for m in materias]

class CursoService:

    @staticmethod
    def listar_cursos(db: Session):
        cursos = CursoRepository.get_all(db)
        return [CursoReadDTO.from_orm(c) for c in cursos]
    
class AsignacionService:

    @staticmethod
    def asignar_materia(db: Session, data: AsignacionCreateDTO):
        return AsignacionRepository.create(db, data.dict())

    @staticmethod
    def listar_asignaciones(db: Session):
        asignaciones = AsignacionRepository.get_all(db)
        return [AsignacionReadDTO.from_orm(a) for a in asignaciones]

    @staticmethod
    def listar_por_profesor(db: Session, id_profesor: int):
        asignaciones = AsignacionRepository.get_by_profesor(db, id_profesor)
        return [AsignacionReadDTO.from_orm(a) for a in asignaciones]
    @staticmethod
    def listar_por_profesor(db: Session, id_profesor: int):
        asignaciones = AsignacionRepository.get_by_profesor_con_nombres(db, id_profesor)
        return [AsignacionReadNombreDTO.from_orm(a) for a in asignaciones]
    
