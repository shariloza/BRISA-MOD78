from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.modules.profesores.models.profesor_models import (
    Profesor, Materia, Curso, ProfesorCursoMateria, Cargo
)
from typing import Optional, List

# ============ PROFESOR REPOSITORY ============
class ProfesorRepository:

    @staticmethod
    def create(db: Session, profesor_data: dict) -> Profesor:
        """Crea un nuevo profesor"""
        nuevo_profesor = Profesor(**profesor_data)
        db.add(nuevo_profesor)
        db.commit()
        db.refresh(nuevo_profesor)
        return nuevo_profesor

    @staticmethod
    def get_all(db: Session) -> List[Profesor]:
        """Obtiene todos los profesores con sus cargos"""
        return db.query(Profesor).options(joinedload(Profesor.cargo)).all()

    @staticmethod
    def get_by_id(db: Session, id_persona: int) -> Optional[Profesor]:
        """Obtiene un profesor por ID con su cargo"""
        return (
            db.query(Profesor)
            .options(joinedload(Profesor.cargo))
            .filter(Profesor.id_persona == id_persona)
            .first()
        )

    @staticmethod
    def get_by_ci(db: Session, ci: str) -> Optional[Profesor]:
        """Obtiene un profesor por CI"""
        return db.query(Profesor).filter(Profesor.ci == ci).first()

    @staticmethod
    def get_by_correo(db: Session, correo: str) -> Optional[Profesor]:
        """Obtiene un profesor por correo"""
        return db.query(Profesor).filter(Profesor.correo == correo).first()

    @staticmethod
    def update(db: Session, profesor: Profesor, data: dict) -> Profesor:
        """Actualiza un profesor"""
        for key, value in data.items():
            if value is not None:  # Solo actualiza campos no nulos
                setattr(profesor, key, value)
        db.commit()
        db.refresh(profesor)
        return profesor

    @staticmethod
    def delete(db: Session, profesor: Profesor) -> Profesor:
        """Elimina un profesor (las asignaciones se eliminan en cascada)"""
        db.delete(profesor)
        db.commit()
        return profesor

    @staticmethod
    def exists_by_ci(db: Session, ci: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si existe un profesor con el CI dado"""
        query = db.query(Profesor).filter(Profesor.ci == ci)
        if exclude_id:
            query = query.filter(Profesor.id_persona != exclude_id)
        return query.first() is not None

    @staticmethod
    def exists_by_correo(db: Session, correo: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si existe un profesor con el correo dado"""
        query = db.query(Profesor).filter(Profesor.correo == correo)
        if exclude_id:
            query = query.filter(Profesor.id_persona != exclude_id)
        return query.first() is not None

# ============ MATERIA REPOSITORY ============
class MateriaRepository:

    @staticmethod
    def create(db: Session, materia_data: dict) -> Materia:
        """Crea una nueva materia"""
        nueva_materia = Materia(**materia_data)
        db.add(nueva_materia)
        db.commit()
        db.refresh(nueva_materia)
        return nueva_materia

    @staticmethod
    def get_all(db: Session) -> List[Materia]:
        """Obtiene todas las materias"""
        return db.query(Materia).all()

    @staticmethod
    def get_by_id(db: Session, id_materia: int) -> Optional[Materia]:
        """Obtiene una materia por ID"""
        return db.query(Materia).filter(Materia.id_materia == id_materia).first()

    @staticmethod
    def get_by_ids(db: Session, ids: List[int]) -> List[Materia]:
        """Obtiene múltiples materias por IDs"""
        return db.query(Materia).filter(Materia.id_materia.in_(ids)).all()

    @staticmethod
    def update(db: Session, materia: Materia, data: dict) -> Materia:
        """Actualiza una materia"""
        for key, value in data.items():
            if value is not None:
                setattr(materia, key, value)
        db.commit()
        db.refresh(materia)
        return materia

    @staticmethod
    def delete(db: Session, materia: Materia) -> Materia:
        """Elimina una materia"""
        db.delete(materia)
        db.commit()
        return materia

# ============ CURSO REPOSITORY ============
class CursoRepository:

    @staticmethod
    def create(db: Session, curso_data: dict) -> Curso:
        """Crea un nuevo curso"""
        nuevo_curso = Curso(**curso_data)
        db.add(nuevo_curso)
        db.commit()
        db.refresh(nuevo_curso)
        return nuevo_curso

    @staticmethod
    def get_all(db: Session) -> List[Curso]:
        """Obtiene todos los cursos"""
        return db.query(Curso).all()

    @staticmethod
    def get_by_id(db: Session, id_curso: int) -> Optional[Curso]:
        """Obtiene un curso por ID"""
        return db.query(Curso).filter(Curso.id_curso == id_curso).first()

    @staticmethod
    def get_by_ids(db: Session, ids: List[int]) -> List[Curso]:
        """Obtiene múltiples cursos por IDs"""
        return db.query(Curso).filter(Curso.id_curso.in_(ids)).all()

    @staticmethod
    def update(db: Session, curso: Curso, data: dict) -> Curso:
        """Actualiza un curso"""
        for key, value in data.items():
            if value is not None:
                setattr(curso, key, value)
        db.commit()
        db.refresh(curso)
        return curso

    @staticmethod
    def delete(db: Session, curso: Curso) -> Curso:
        """Elimina un curso"""
        db.delete(curso)
        db.commit()
        return curso

# ============ ASIGNACIÓN REPOSITORY ============
class AsignacionRepository:

    @staticmethod
    def create(db: Session, data: dict) -> ProfesorCursoMateria:
        """Crea una nueva asignación"""
        id_profesor = int(data.get("id_profesor"))
        id_curso = int(data.get("id_curso"))
        id_materia = int(data.get("id_materia"))

        # Verificar si ya existe
        existente = db.query(ProfesorCursoMateria).filter_by(
            id_profesor=id_profesor,
            id_curso=id_curso,
            id_materia=id_materia
        ).first()
        
        if existente:
            return existente

        asignacion = ProfesorCursoMateria(
            id_profesor=id_profesor,
            id_curso=id_curso,
            id_materia=id_materia
        )
        db.add(asignacion)
        db.commit()
        return asignacion

    @staticmethod
    def get_all(db: Session) -> List[ProfesorCursoMateria]:
        """Obtiene todas las asignaciones"""
        return db.query(ProfesorCursoMateria).all()

    @staticmethod
    def get_by_profesor(db: Session, id_profesor: int) -> List[ProfesorCursoMateria]:
        """Obtiene todas las asignaciones de un profesor"""
        return (
            db.query(ProfesorCursoMateria)
            .filter(ProfesorCursoMateria.id_profesor == id_profesor)
            .all()
        )

    @staticmethod
    def get_by_profesor_con_nombres(db: Session, id_profesor: int):
        """Obtiene asignaciones de un profesor con los nombres"""
        return (
            db.query(
                ProfesorCursoMateria.id_profesor,
                ProfesorCursoMateria.id_curso,
                ProfesorCursoMateria.id_materia,
                Profesor.nombres.label("nombre_profesor"),
                Curso.nombre_curso.label("nombre_curso"),
                Materia.nombre_materia.label("nombre_materia")
            )
            .join(Profesor, Profesor.id_persona == ProfesorCursoMateria.id_profesor)
            .join(Curso, Curso.id_curso == ProfesorCursoMateria.id_curso)
            .join(Materia, Materia.id_materia == ProfesorCursoMateria.id_materia)
            .filter(Profesor.id_persona == id_profesor)
            .all()
        )

    @staticmethod
    def delete(db: Session, id_profesor: int, id_curso: int, id_materia: int) -> bool:
        """Elimina una asignación específica"""
        asignacion = db.query(ProfesorCursoMateria).filter_by(
            id_profesor=id_profesor,
            id_curso=id_curso,
            id_materia=id_materia
        ).first()
        
        if asignacion:
            db.delete(asignacion)
            db.commit()
            return True
        return False

    @staticmethod
    def exists(db: Session, id_profesor: int, id_curso: int, id_materia: int) -> bool:
        """Verifica si existe una asignación"""
        return db.query(ProfesorCursoMateria).filter_by(
            id_profesor=id_profesor,
            id_curso=id_curso,
            id_materia=id_materia
        ).first() is not None

# ============ CARGO REPOSITORY ============
class CargoRepository:

    @staticmethod
    def get_all(db: Session) -> List[Cargo]:
        """Obtiene todos los cargos"""
        return db.query(Cargo).all()

    @staticmethod
    def get_by_id(db: Session, id_cargo: int) -> Optional[Cargo]:
        """Obtiene un cargo por ID"""
        return db.query(Cargo).filter(Cargo.id_cargo == id_cargo).first()