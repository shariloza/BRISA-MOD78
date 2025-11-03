from sqlalchemy.orm import Session
from app.modules.profesores.models.profesor_models import Profesor
from app.modules.profesores.dto.profesor_dto import ProfesorCreateDTO

class ProfesorService:

    @staticmethod
    def crear_profesor(db: Session, data: ProfesorCreateDTO) -> Profesor:
        nuevo_profesor = Profesor(**data.dict())
        db.add(nuevo_profesor)
        db.commit()
        db.refresh(nuevo_profesor)
        return nuevo_profesor

    @staticmethod
    def listar_profesores(db: Session):
        return db.query(Profesor).all()

    @staticmethod
    def obtener_profesor(db: Session, id_persona: int):
        return db.query(Profesor).filter(Profesor.id_persona == id_persona).first()

    @staticmethod
    def actualizar_profesor(db: Session, id_persona: int, data: dict):
        profesor = db.query(Profesor).filter(Profesor.id_persona == id_persona).first()
        if not profesor:
            return None
        for key, value in data.items():
            setattr(profesor, key, value)
        db.commit()
        db.refresh(profesor)
        return profesor

    @staticmethod
    def eliminar_profesor(db: Session, id_persona: int):
        profesor = db.query(Profesor).filter(Profesor.id_persona == id_persona).first()
        if not profesor:
            return None
        db.delete(profesor)
        db.commit()
        return profesor
