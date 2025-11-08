from sqlalchemy.orm import Session
from collections import defaultdict
from app.modules.profesores.dto.profesor_dto import ProfesorCreateDTO, ProfesorReadDTO, MateriaReadDTO, CursoReadDTO, AsignacionCreateDTO, AsignacionReadDTO, AsignacionReadNombreDTO, ProfesorFullDTO
from app.modules.profesores.repositories.profesor_repository import ProfesorRepository, MateriaRepository, CursoRepository, AsignacionRepository
from app.modules.profesores.models.profesor_models import Profesor, Curso, Materia, ProfesorCursoMateria
class ProfesorService:

    @staticmethod
    def crear_profesor(db: Session, data: ProfesorCreateDTO):
        profesor = ProfesorRepository.create(db, data.dict())
        # Asegurar que se cargue el cargo (si tiene)
        if profesor.id_cargo:
           db.refresh(profesor)  # recarga desde BD para traer relaciones
        dto = ProfesorReadDTO.from_orm(profesor)
        dto.nombre_cargo = profesor.cargo.nombre_cargo if profesor.cargo else None
        return dto

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
    def listar_profesores_completo(db: Session):
         # Traer todos los profesores
        profesores = db.query(Profesor).all()
        # Traer todas las asignaciones
        asignaciones = db.query(ProfesorCursoMateria).all()

        # Map profesor -> sets de cursos y materias
        prof_map = defaultdict(lambda: {"cursos": set(), "materias": set()})
        for a in asignaciones:
            prof_map[a.id_profesor]["cursos"].add(a.id_curso)
            prof_map[a.id_profesor]["materias"].add(a.id_materia)

        resultado = []
        for p in profesores:
            dto = ProfesorFullDTO.from_orm(p)
            dto.nombre_cargo = p.cargo.nombre_cargo if p.cargo else None

            # Traer nombres de cursos y materias evitando duplicados
            dto.cursos = [
                c.nombre_curso
                for c in db.query(Curso).filter(Curso.id_curso.in_(prof_map[p.id_persona]["cursos"])).all()
            ]
            dto.materias = [
                m.nombre_materia
                for m in db.query(Materia).filter(Materia.id_materia.in_(prof_map[p.id_persona]["materias"])).all()
            ]

            resultado.append(dto)

        return resultado
    

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
        asign = AsignacionRepository.create(db, data.dict())
        # devolver DTO simple con ids
        return AsignacionReadDTO.from_orm(asign)

    @staticmethod
    def listar_asignaciones(db: Session):
        asignaciones = AsignacionRepository.get_all(db)
        return [AsignacionReadDTO.from_orm(a) for a in asignaciones]

    @staticmethod
    def listar_por_profesor(db: Session, id_profesor: int):
        asignaciones = AsignacionRepository.get_by_profesor_con_nombres(db, id_profesor)
        return [AsignacionReadNombreDTO.from_orm(a) for a in asignaciones]

