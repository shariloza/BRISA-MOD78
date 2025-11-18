from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime, time, date

# ============ CARGO DTOs ============
class CargoReadDTO(BaseModel):
    id_cargo: int
    nombre_cargo: str
    descripcion: Optional[str] = None
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ============ PERSONA/PROFESOR DTOs ============
class ProfesorCreateDTO(BaseModel):
    # Datos de Persona
    ci: str = Field(..., min_length=7, max_length=20)
    nombres: str = Field(..., min_length=2, max_length=50)
    apellido_paterno: str = Field(..., min_length=2, max_length=50)
    apellido_materno: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[EmailStr] = None
    id_cargo: Optional[int] = None
    estado_laboral: Optional[str] = "activo"
    años_experiencia: Optional[int] = 0
    fecha_ingreso: Optional[date] = None
    fecha_retiro: Optional[date] = None
    motivo_retiro: Optional[str] = None
    
    # Datos de Profesor
    especialidad: Optional[str] = Field(None, max_length=100)
    titulo_academico: Optional[str] = Field(None, max_length=100)
    nivel_enseñanza: Optional[str] = "todos"
    observaciones_profesor: Optional[str] = None


class ProfesorUpdateDTO(BaseModel):
    # Datos de Persona
    ci: Optional[str] = None
    nombres: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    id_cargo: Optional[int] = None
    estado_laboral: Optional[str] = None
    años_experiencia: Optional[int] = None
    fecha_ingreso: Optional[date] = None
    fecha_retiro: Optional[date] = None
    motivo_retiro: Optional[str] = None
    
    # Datos de Profesor
    especialidad: Optional[str] = None
    titulo_academico: Optional[str] = None
    nivel_enseñanza: Optional[str] = None
    observaciones_profesor: Optional[str] = None

    class Config:
        extra = "ignore"


class ProfesorReadDTO(BaseModel):
    # IDs
    id_persona: int
    id_profesor: int
    
    # Datos de Persona
    ci: str
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    tipo_persona: str
    id_cargo: Optional[int] = None
    nombre_cargo: Optional[str] = None
    estado_laboral: str
    años_experiencia: int
    fecha_ingreso: Optional[date] = None
    fecha_retiro: Optional[date] = None
    motivo_retiro: Optional[str] = None
    
    # Datos de Profesor
    especialidad: Optional[str] = None
    titulo_academico: Optional[str] = None
    nivel_enseñanza: str
    observaciones_profesor: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProfesorFullDTO(ProfesorReadDTO):
    materias: List[str] = []
    cursos: List[str] = []
    total_horas_semanales: Optional[float] = 0.0

    class Config:
        from_attributes = True


# ============ MATERIA DTOs ============
class MateriaCreateDTO(BaseModel):
    nombre_materia: str = Field(..., min_length=2, max_length=50)
    nivel: str = Field(..., pattern="^(inicial|primaria|secundaria)$")


class MateriaReadDTO(BaseModel):
    id_materia: int
    nombre_materia: str
    nivel: str

    class Config:
        from_attributes = True


# ============ CURSO DTOs ============
class CursoCreateDTO(BaseModel):
    nombre_curso: str = Field(..., min_length=2, max_length=50)
    nivel: str = Field(..., pattern="^(inicial|primaria|secundaria)$")
    gestion: str = Field(..., min_length=4, max_length=20)


class CursoReadDTO(BaseModel):
    id_curso: int
    nombre_curso: str
    nivel: str
    gestion: str

    class Config:
        from_attributes = True


# ============ ASIGNACIÓN DTOs ============
class AsignacionCreateDTO(BaseModel):
    id_profesor: int = Field(..., gt=0)
    id_curso: int = Field(..., gt=0)
    id_materia: int = Field(..., gt=0)


class AsignacionReadDTO(BaseModel):
    id_profesor: int
    id_curso: int
    id_materia: int

    class Config:
        from_attributes = True


class AsignacionReadNombreDTO(BaseModel):
    id_profesor: Optional[int] = None
    id_curso: Optional[int] = None
    id_materia: Optional[int] = None
    nombre_profesor: str
    nombre_curso: str
    nombre_materia: str

    class Config:
        from_attributes = True


# ============ BLOQUE HORARIO DTOs ============
class BloqueHorarioCreateDTO(BaseModel):
    id_profesor: int = Field(..., gt=0)
    id_curso: int = Field(..., gt=0)
    id_materia: int = Field(..., gt=0)
    dia_semana: str = Field(..., pattern="^(lunes|martes|miercoles|jueves|viernes|sabado)$")
    hora_inicio: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$")
    hora_fin: str = Field(..., pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$")
    gestion: str = Field(default="2025", max_length=10)
    observaciones: Optional[str] = None

    @field_validator('hora_inicio', 'hora_fin')
    def validar_formato_hora(cls, v):
        """Convierte string a formato time"""
        if isinstance(v, str):
            try:
                parts = v.split(':')
                if len(parts) == 2:
                    return f"{parts[0]}:{parts[1]}:00"
                return v
            except:
                raise ValueError('Formato de hora inválido. Use HH:MM o HH:MM:SS')
        return v

    @field_validator('hora_fin')
    def validar_hora_fin(cls, v, info):
        if 'hora_inicio' in info.data:
            try:
                inicio_parts = info.data['hora_inicio'].split(':')
                fin_parts = v.split(':')
                inicio_mins = int(inicio_parts[0]) * 60 + int(inicio_parts[1])
                fin_mins = int(fin_parts[0]) * 60 + int(fin_parts[1])
                if fin_mins <= inicio_mins:
                    raise ValueError('La hora de fin debe ser mayor que la hora de inicio')
            except:
                pass
        return v


class BloqueHorarioUpdateDTO(BaseModel):
    id_profesor: Optional[int] = None
    id_curso: Optional[int] = None
    id_materia: Optional[int] = None
    dia_semana: Optional[str] = Field(None, pattern="^(lunes|martes|miercoles|jueves|viernes|sabado)$")
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    gestion: Optional[str] = None
    observaciones: Optional[str] = None

    @field_validator('hora_inicio', 'hora_fin')
    def validar_formato_hora(cls, v):
        """Convierte string a formato time"""
        if v and isinstance(v, str):
            try:
                parts = v.split(':')
                if len(parts) == 2:
                    return f"{parts[0]}:{parts[1]}:00"
                return v
            except:
                raise ValueError('Formato de hora inválido. Use HH:MM o HH:MM:SS')
        return v

    class Config:
        extra = "ignore"


class BloqueHorarioReadDTO(BaseModel):
    id_bloque: int
    id_profesor: int
    id_curso: int
    id_materia: int
    dia_semana: str
    hora_inicio: time
    hora_fin: time
    gestion: str
    fecha_registro: datetime
    observaciones: Optional[str] = None
    
    # Datos relacionados (opcionales)
    nombre_profesor: Optional[str] = None
    nombre_curso: Optional[str] = None
    nombre_materia: Optional[str] = None

    class Config:
        from_attributes = True


# ============ DTOs para Vistas SQL ============
class VistaBloqueProfesorDTO(BaseModel):
    id_persona: int
    nombre_completo: str
    id_bloque: int
    dia_semana: str
    hora_inicio: time
    hora_fin: time
    horas_bloque: float
    nombre_materia: str
    nombre_curso: str
    nivel: str
    gestion: str
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class VistaCargaHorariaDTO(BaseModel):
    id_persona: int
    ci: str
    nombre_completo: str
    estado_laboral: str
    especialidad: Optional[str] = None
    titulo_academico: Optional[str] = None
    gestion: str
    total_bloques: int
    carga_horaria_semanal: float
    materias: Optional[str] = None
    cursos: Optional[str] = None

    class Config:
        from_attributes = True


class VistaHorarioSemanalDTO(BaseModel):
    id_persona: int
    nombre_completo: str
    gestion: str
    lunes: Optional[str] = None
    martes: Optional[str] = None
    miercoles: Optional[str] = None
    jueves: Optional[str] = None
    viernes: Optional[str] = None
    sabado: Optional[str] = None

    class Config:
        from_attributes = True