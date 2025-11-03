from pydantic import BaseModel, EmailStr
from typing import Optional

class ProfesorCreateDTO(BaseModel):
    ci: str
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    direccion: Optional[str] = None
    correo: EmailStr
    telefono: Optional[str] = None

class ProfesorReadDTO(BaseModel):
    id_persona: int
    ci: str
    nombres: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    direccion: Optional[str] = None
    tipo_persona: str
    correo: str
    telefono: Optional[str] = None

    class Config:
        orm_mode = True
