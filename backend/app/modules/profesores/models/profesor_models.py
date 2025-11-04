from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Cargo(Base):
    __tablename__ = "cargos"

    id_cargo = Column(Integer, primary_key=True, autoincrement=True)
    nombre_cargo = Column(String(100), nullable=False)
    descripcion = Column(String(200), nullable=True)
    estado = Column(String(20), nullable=False, default="activo")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

class Profesor(Base):
    __tablename__ = "personas"

    id_persona = Column(Integer, primary_key=True, autoincrement=True)
    ci = Column(String(20), nullable=False, unique=True)
    nombres = Column(String(100), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=True)
    direccion = Column(String(200), nullable=True)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(100), nullable=False, unique=True)
    tipo_persona = Column(String(50), nullable=False, default="profesor")

    # Relación con cargo
    id_cargo = Column(Integer, ForeignKey("cargos.id_cargo"), nullable=True)
    cargo = relationship("Cargo", backref="profesores")

class Materia(Base):
    __tablename__ = "materias"
    
    id_materia = Column(Integer, primary_key=True, autoincrement=True)
    nombre_materia = Column(String(100), nullable=False)
    nivel = Column(String(50), nullable=False)

class Curso(Base):
    __tablename__ = "cursos"
    
    id_curso = Column(Integer, primary_key=True, autoincrement=True)
    nombre_curso = Column(String(100), nullable=False)
    nivel = Column(String(50), nullable=False)
    gestion = Column(String(10), nullable=False)
    
class ProfesorCursoMateria(Base):
    __tablename__ = "profesores_cursos_materias"

    id_profesor = Column(Integer, ForeignKey("personas.id_persona"), primary_key=True)
    id_curso = Column(Integer, ForeignKey("cursos.id_curso"), primary_key=True)
    id_materia = Column(Integer, ForeignKey("materias.id_materia"), primary_key=True)


  