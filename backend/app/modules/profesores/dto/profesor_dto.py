from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# ============ CARGO DTOs ============
class CargoReadDTO(BaseModel):
    id_cargo: int
    nombre_cargo: str
    descripcion: Optional[str] = None
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True

# ============ PROFESOR DTOs ============
class ProfesorCreateDTO(BaseModel):
    ci: str = Field(..., min_length=7, max_length=20)
    nombres: str = Field(..., min_length=2, max_length=100)
    apellido_paterno: str = Field(..., min_length=2, max_length=50)
    apellido_materno: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=200)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: EmailStr
    tipo_persona: Optional[str] = "profesor"
    id_cargo: Optional[int] = None
    estado_laboral: Optional[str] = "activo"
    fecha_retiro: Optional[datetime] = None
    motivo_retiro: Optional[str] = Field(None, max_length=200)

class ProfesorUpdateDTO(BaseModel):
    ci: Optional[str] = None
    nombres: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    tipo_persona: Optional[str] = None
    id_cargo: Optional[int] = None
    estado_laboral: Optional[str] = None
    fecha_retiro: Optional[datetime] = None
    motivo_retiro: Optional[str] = None

    class Config:
        extra = "ignore"  # Ignora campos extras como 'id'

class ProfesorReadDTO(BaseModel):
    id_persona: int
    ci: str
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: str
    tipo_persona: str
    id_cargo: Optional[int] = None
    nombre_cargo: Optional[str] = None
    estado_laboral: str
    fecha_retiro: Optional[datetime] = None
    motivo_retiro: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProfesorFullDTO(BaseModel):
    id_persona: int
    ci: str
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: str
    tipo_persona: str
    id_cargo: Optional[int] = None
    nombre_cargo: Optional[str] = None
    estado_laboral: str
    fecha_retiro: Optional[datetime] = None
    motivo_retiro: Optional[str] = None
    materias: List[str] = []
    cursos: List[str] = []

    class Config:
        from_attributes = True

# ============ MATERIA DTOs ============
class MateriaCreateDTO(BaseModel):
    nombre_materia: str = Field(..., min_length=2, max_length=100)
    nivel: str = Field(..., min_length=2, max_length=50)

class MateriaReadDTO(BaseModel):
    id_materia: int
    nombre_materia: str
    nivel: str

    class Config:
        from_attributes = True

# ============ CURSO DTOs ============
class CursoCreateDTO(BaseModel):
    nombre_curso: str = Field(..., min_length=2, max_length=100)
    nivel: str = Field(..., min_length=2, max_length=50)
    gestion: str = Field(..., min_length=4, max_length=10)

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

class AsignacionDeleteDTO(BaseModel):
    id_profesor: int = Field(..., gt=0)
    id_curso: int = Field(..., gt=0)
    id_materia: int = Field(..., gt=0)