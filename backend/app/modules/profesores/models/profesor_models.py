from sqlalchemy import Column, Integer, String
from app.config.database import Base

class Profesor(Base):
    __tablename__ = "personas"

    id_persona = Column(Integer, primary_key=True, autoincrement=True)
    ci = Column(String(20), nullable=False, unique=True)
    nombres = Column(String(100), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=True)
    direccion = Column(String(200), nullable=True)
    tipo_persona = Column(String(50), nullable=False, default="profesor")
    correo = Column(String(100), nullable=False, unique=True)
    telefono = Column(String(20), nullable=True)
