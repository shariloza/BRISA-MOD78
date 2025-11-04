from sqlalchemy.orm import Session
from app.modules.profesores.models.profesor_models import Profesor,Materia, Curso, ProfesorCursoMateria

class ProfesorRepository:

    @staticmethod
    def create(db: Session, profesor: dict) -> Profesor:
        nuevo_profesor = Profesor(**profesor)
        db.add(nuevo_profesor)
        db.commit()
        db.refresh(nuevo_profesor)
        return nuevo_profesor

    @staticmethod
    def get_all(db: Session):
        return db.query(Profesor).all()

    @staticmethod
    def get_by_id(db: Session, id_persona: int):
        return db.query(Profesor).filter(Profesor.id_persona == id_persona).first()

    @staticmethod
    def update(db: Session, profesor: Profesor, data: dict):
        for key, value in data.items():
            setattr(profesor, key, value)
        db.commit()
        db.refresh(profesor)
        if profesor.id_cargo:
            db.refresh(profesor.cargo) 
        return profesor

    @staticmethod
    def delete(db: Session, profesor: Profesor):
        db.delete(profesor)
        db.commit()
        return profesor

class MateriaRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Materia).all()

class CursoRepository:

    @staticmethod
    def get_all(db: Session):
        return db.query(Curso).all()
    
class AsignacionRepository:

    @staticmethod
    def create(db: Session, data: dict):
        asignacion = ProfesorCursoMateria(**data)
        db.add(asignacion)
        db.commit()
        db.refresh(asignacion)
        return asignacion

    @staticmethod
    def get_all(db: Session):
        return db.query(ProfesorCursoMateria).all()

    @staticmethod
    def get_by_profesor(db: Session, id_profesor: int):
        return db.query(ProfesorCursoMateria).filter_by(id_profesor=id_profesor).all()
    @staticmethod
    def get_by_profesor_con_nombres(db: Session, id_profesor: int):
        return (
            db.query(
                Profesor.nombres.label("nombre_profesor"),
                Curso.nombre_curso.label("nombre_curso"),
                Materia.nombre_materia.label("nombre_materia")
            )
            .join(ProfesorCursoMateria, Profesor.id_persona == ProfesorCursoMateria.id_profesor)
            .join(Curso, Curso.id_curso == ProfesorCursoMateria.id_curso)
            .join(Materia, Materia.id_materia == ProfesorCursoMateria.id_materia)
            .filter(Profesor.id_persona == id_profesor)
            .all()
        )
    
