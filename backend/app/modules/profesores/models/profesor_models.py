from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Time, Text, Enum, Date
from sqlalchemy.orm import relationship
from app.config.database import Base
from datetime import datetime

class Cargo(Base):
    __tablename__ = "cargos"

    id_cargo = Column(Integer, primary_key=True, autoincrement=True)
    nombre_cargo = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    estado = Column(Enum('activo', 'inactivo'), nullable=False, default='activo')
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relación inversa
    personas = relationship("Persona", back_populates="cargo")


class Persona(Base):
    __tablename__ = "personas"

    id_persona = Column(Integer, primary_key=True, autoincrement=True)
    ci = Column(String(20), nullable=False, unique=True)
    nombres = Column(String(50), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=True)
    direccion = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(50), nullable=True, unique=True)
    tipo_persona = Column(Enum('profesor', 'administrativo'), nullable=False)
    id_cargo = Column(Integer, ForeignKey("cargos.id_cargo"), nullable=True)
    estado_laboral = Column(Enum('activo', 'retirado', 'licencia', 'suspendido'), 
                           nullable=False, default='activo')
    años_experiencia = Column(Integer, default=0)
    fecha_ingreso = Column(Date, nullable=True)
    fecha_retiro = Column(Date, nullable=True)
    motivo_retiro = Column(Text, nullable=True)
    
    # Relaciones
    cargo = relationship("Cargo", back_populates="personas")
    profesor = relationship("Profesor", back_populates="persona", uselist=False, cascade="all, delete-orphan")


class Profesor(Base):
    __tablename__ = "profesores"

    id_profesor = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(Integer, ForeignKey("personas.id_persona", ondelete="CASCADE"), nullable=False, unique=True)
    especialidad = Column(String(100), nullable=True)
    titulo_academico = Column(String(100), nullable=True)
    nivel_enseñanza = Column(Enum('foundation', 'primary', 'secondary', 'todos'), 
                            nullable=False, default='todos')
    observaciones = Column(Text, nullable=True)

    # Relaciones
    persona = relationship("Persona", back_populates="profesor")
    asignaciones = relationship("ProfesorCursoMateria", back_populates="profesor", cascade="all, delete-orphan")
    bloques_horarios = relationship("BloqueHorario", back_populates="profesor", cascade="all, delete-orphan")


class Materia(Base):
    __tablename__ = "materias"
    
    id_materia = Column(Integer, primary_key=True, autoincrement=True)
    nombre_materia = Column(String(50), nullable=False)
    nivel = Column(Enum('inicial', 'primaria', 'secundaria'), nullable=False)

    # Relaciones
    asignaciones = relationship("ProfesorCursoMateria", back_populates="materia", cascade="all, delete-orphan")
    bloques = relationship("BloqueHorario", back_populates="materia", cascade="all, delete-orphan")


class Curso(Base):
    __tablename__ = "cursos"
    
    id_curso = Column(Integer, primary_key=True, autoincrement=True)
    nombre_curso = Column(String(50), nullable=False)
    nivel = Column(Enum('inicial', 'primaria', 'secundaria'), nullable=False)
    gestion = Column(String(20), nullable=False)

    # Relaciones
    asignaciones = relationship("ProfesorCursoMateria", back_populates="curso", cascade="all, delete-orphan")
    bloques = relationship("BloqueHorario", back_populates="curso", cascade="all, delete-orphan")


class ProfesorCursoMateria(Base):
    __tablename__ = "profesores_cursos_materias"

    id_profesor = Column(Integer, ForeignKey("profesores.id_profesor", ondelete="CASCADE"), primary_key=True)
    id_curso = Column(Integer, ForeignKey("cursos.id_curso", ondelete="CASCADE"), primary_key=True)
    id_materia = Column(Integer, ForeignKey("materias.id_materia", ondelete="CASCADE"), primary_key=True)

    # Relaciones
    profesor = relationship("Profesor", back_populates="asignaciones")
    curso = relationship("Curso", back_populates="asignaciones")
    materia = relationship("Materia", back_populates="asignaciones")


class BloqueHorario(Base):
    __tablename__ = "bloques_horarios"

    id_bloque = Column(Integer, primary_key=True, autoincrement=True)
    id_profesor = Column(Integer, ForeignKey("profesores.id_profesor", ondelete="CASCADE"), nullable=False)
    id_curso = Column(Integer, ForeignKey("cursos.id_curso", ondelete="CASCADE"), nullable=False)
    id_materia = Column(Integer, ForeignKey("materias.id_materia", ondelete="CASCADE"), nullable=False)
    dia_semana = Column(Enum('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado'), nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    gestion = Column(String(10), nullable=False, default='2025')
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    observaciones = Column(Text, nullable=True)

    # Relaciones
    profesor = relationship("Profesor", back_populates="bloques_horarios")
    curso = relationship("Curso", back_populates="bloques")
    materia = relationship("Materia", back_populates="bloques")