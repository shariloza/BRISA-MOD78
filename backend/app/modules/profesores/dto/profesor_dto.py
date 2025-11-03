from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ------------------------------
# DTOs PROFESOR
# ------------------------------
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
        orm_mode = True

# ------------------------------
# DTOs CARGO
# ------------------------------
class CargoReadDTO(BaseModel):
    id_cargo: int
    nombre_cargo: str
    descripcion: Optional[str] = None
    estado: str
    fecha_creacion: datetime

    class Config:
        orm_mode = True
