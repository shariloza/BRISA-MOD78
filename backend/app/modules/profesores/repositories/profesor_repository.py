from sqlalchemy.orm import Session
from app.modules.profesores.models.profesor_models import Profesor
from app.modules.profesores.dto.profesor_dto import ProfesorCreateDTO

class ProfesorRepository:

    @staticmethod
    def create(db: Session, profesor: ProfesorCreateDTO):
        db_profesor = Profesor(**profesor.dict())
        db.add(db_profesor)
        db.commit()
        db.refresh(db_profesor)
        return db_profesor

    @staticmethod
    def get_all(db: Session):
        return db.query(Profesor).all()
