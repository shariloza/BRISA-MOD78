from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ProfesorCreateDTO(BaseModel):
    ci: str
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: EmailStr
    tipo_persona: Optional[str] = "profesor"
    id_cargo: Optional[int] = None

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

    class Config:
        from_attributes = True

class CargoReadDTO(BaseModel):
    id_cargo: int
    nombre_cargo: str
    descripcion: Optional[str] = None
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class MateriaReadDTO(BaseModel):
    id_materia: int
    nombre_materia: str
    nivel: str

    class Config:
        from_attributes = True

class CursoReadDTO(BaseModel):
    id_curso: int
    nombre_curso: str
    nivel: str
    gestion: str

    class Config:
        from_attributes = True
        
class AsignacionCreateDTO(BaseModel):
    id_profesor: int
    id_curso: int
    id_materia: int

class AsignacionReadDTO(BaseModel):
    id_profesor: int
    id_curso: int
    id_materia: int

    class Config:
        from_attributes = True
        
class AsignacionReadNombreDTO(BaseModel):
    nombre_profesor: str
    nombre_curso: str
    nombre_materia: str

    class Config:
        from_attributes = True
