from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, text
from app.modules.profesores.models.profesor_models import (
    Persona, Profesor, Materia, Curso, ProfesorCursoMateria, 
    Cargo, BloqueHorario
)
from typing import Optional, List

# ============ PERSONA REPOSITORY ============
class PersonaRepository:

    @staticmethod
    def create(db: Session, persona_data: dict) -> Persona:
        """Crea una persona"""
        nueva_persona = Persona(**persona_data)
        db.add(nueva_persona)
        db.commit()
        db.refresh(nueva_persona)
        return nueva_persona

    @staticmethod
    def get_by_id(db: Session, id_persona: int) -> Optional[Persona]:
        """Obtiene una persona por ID con su cargo"""
        return (
            db.query(Persona)
            .options(joinedload(Persona.cargo))
            .filter(Persona.id_persona == id_persona)
            .first()
        )

    @staticmethod
    def get_by_ci(db: Session, ci: str) -> Optional[Persona]:
        """Obtiene una persona por CI"""
        return db.query(Persona).filter(Persona.ci == ci).first()

    @staticmethod
    def get_by_correo(db: Session, correo: str) -> Optional[Persona]:
        """Obtiene una persona por correo"""
        return db.query(Persona).filter(Persona.correo == correo).first()

    @staticmethod
    def update(db: Session, persona: Persona, data: dict) -> Persona:
        """Actualiza una persona"""
        for key, value in data.items():
            if value is not None:
                setattr(persona, key, value)
        db.commit()
        db.refresh(persona)
        return persona

    @staticmethod
    def delete(db: Session, persona: Persona) -> None:
        """Elimina una persona"""
        try:
            db.delete(persona)
            db.commit()
        except Exception as e:
            db.rollback()
            raise

    @staticmethod
    def exists_by_ci(db: Session, ci: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si existe una persona con el CI dado"""
        query = db.query(Persona).filter(Persona.ci == ci)
        if exclude_id:
            query = query.filter(Persona.id_persona != exclude_id)
        return query.first() is not None

    @staticmethod
    def exists_by_correo(db: Session, correo: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si existe una persona con el correo dado"""
        if not correo:
            return False
        query = db.query(Persona).filter(Persona.correo == correo)
        if exclude_id:
            query = query.filter(Persona.id_persona != exclude_id)
        return query.first() is not None


# ============ PROFESOR REPOSITORY ============
class ProfesorRepository:

    @staticmethod
    def create(db: Session, persona_data: dict, profesor_data: dict) -> Profesor:
        """Crea una persona y su registro de profesor"""
        # Crear persona
        nueva_persona = PersonaRepository.create(db, persona_data)
        
        # Crear profesor vinculado
        nuevo_profesor = Profesor(
            id_persona=nueva_persona.id_persona,
            **profesor_data
        )
        db.add(nuevo_profesor)
        db.commit()
        db.refresh(nuevo_profesor)
        return nuevo_profesor

    @staticmethod
    def get_all(db: Session) -> List[Profesor]:
        """Obtiene todos los profesores con sus personas y cargos"""
        return (
            db.query(Profesor)
            .join(Persona, Persona.id_persona == Profesor.id_persona)
            .options(
                joinedload(Profesor.persona).joinedload(Persona.cargo)
            )
            .all()
        )

    @staticmethod
    def get_by_id_persona(db: Session, id_persona: int) -> Optional[Profesor]:
        """Obtiene un profesor por id_persona"""
        return (
            db.query(Profesor)
            .join(Persona, Persona.id_persona == Profesor.id_persona)
            .options(
                joinedload(Profesor.persona).joinedload(Persona.cargo)
            )
            .filter(Persona.id_persona == id_persona)
            .first()
        )

    @staticmethod
    def get_by_id_profesor(db: Session, id_profesor: int) -> Optional[Profesor]:
        """Obtiene un profesor por id_profesor"""
        return (
            db.query(Profesor)
            .options(
                joinedload(Profesor.persona).joinedload(Persona.cargo)
            )
            .filter(Profesor.id_profesor == id_profesor)
            .first()
        )

    @staticmethod
    def update(db: Session, profesor: Profesor, persona_data: dict, profesor_data: dict) -> Profesor:
        """Actualiza persona y profesor"""
        # Actualizar persona
        if persona_data:
            PersonaRepository.update(db, profesor.persona, persona_data)
        
        # Actualizar profesor
        for key, value in profesor_data.items():
            if value is not None:
                setattr(profesor, key, value)
        
        db.commit()
        db.refresh(profesor)
        return profesor

    @staticmethod
    def delete(db: Session, profesor: Profesor) -> None:
        """Elimina un profesor (elimina la persona, profesor se elimina en cascada)"""
        PersonaRepository.delete(db, profesor.persona)


# ============ MATERIA REPOSITORY ============
class MateriaRepository:

    @staticmethod
    def create(db: Session, materia_data: dict) -> Materia:
        nueva_materia = Materia(**materia_data)
        db.add(nueva_materia)
        db.commit()
        db.refresh(nueva_materia)
        return nueva_materia

    @staticmethod
    def get_all(db: Session) -> List[Materia]:
        return db.query(Materia).all()

    @staticmethod
    def get_by_id(db: Session, id_materia: int) -> Optional[Materia]:
        return db.query(Materia).filter(Materia.id_materia == id_materia).first()

    @staticmethod
    def get_by_ids(db: Session, ids: List[int]) -> List[Materia]:
        return db.query(Materia).filter(Materia.id_materia.in_(ids)).all()

    @staticmethod
    def update(db: Session, materia: Materia, data: dict) -> Materia:
        for key, value in data.items():
            if value is not None:
                setattr(materia, key, value)
        db.commit()
        db.refresh(materia)
        return materia

    @staticmethod
    def delete(db: Session, materia: Materia) -> Materia:
        db.delete(materia)
        db.commit()
        return materia


# ============ CURSO REPOSITORY ============
class CursoRepository:

    @staticmethod
    def create(db: Session, curso_data: dict) -> Curso:
        nuevo_curso = Curso(**curso_data)
        db.add(nuevo_curso)
        db.commit()
        db.refresh(nuevo_curso)
        return nuevo_curso

    @staticmethod
    def get_all(db: Session) -> List[Curso]:
        return db.query(Curso).all()

    @staticmethod
    def get_by_id(db: Session, id_curso: int) -> Optional[Curso]:
        return db.query(Curso).filter(Curso.id_curso == id_curso).first()

    @staticmethod
    def get_by_ids(db: Session, ids: List[int]) -> List[Curso]:
        return db.query(Curso).filter(Curso.id_curso.in_(ids)).all()

    @staticmethod
    def update(db: Session, curso: Curso, data: dict) -> Curso:
        for key, value in data.items():
            if value is not None:
                setattr(curso, key, value)
        db.commit()
        db.refresh(curso)
        return curso

    @staticmethod
    def delete(db: Session, curso: Curso) -> Curso:
        db.delete(curso)
        db.commit()
        return curso


# ============ ASIGNACIÓN REPOSITORY ============
class AsignacionRepository:

    @staticmethod
    def create(db: Session, data: dict) -> ProfesorCursoMateria:
        """Crea una nueva asignación"""
        id_profesor = int(data.get("id_profesor"))
        id_curso = int(data.get("id_curso"))
        id_materia = int(data.get("id_materia"))

        # Verificar si ya existe
        existente = db.query(ProfesorCursoMateria).filter_by(
            id_profesor=id_profesor,
            id_curso=id_curso,
            id_materia=id_materia
        ).first()
        
        if existente:
            return existente

        asignacion = ProfesorCursoMateria(
            id_profesor=id_profesor,
            id_curso=id_curso,
            id_materia=id_materia
        )
        db.add(asignacion)
        db.commit()
        db.refresh(asignacion)
        return asignacion

    @staticmethod
    def get_all(db: Session) -> List[ProfesorCursoMateria]:
        """Obtiene todas las asignaciones"""
        return db.query(ProfesorCursoMateria).all()

    @staticmethod
    def get_by_profesor(db: Session, id_profesor: int) -> List[ProfesorCursoMateria]:
        """Obtiene todas las asignaciones de un profesor"""
        return (
            db.query(ProfesorCursoMateria)
            .filter(ProfesorCursoMateria.id_profesor == id_profesor)
            .all()
        )

    @staticmethod
    def get_by_profesor_con_nombres(db: Session, id_profesor: int):
        """Obtiene asignaciones de un profesor con los nombres"""
        return (
            db.query(
                ProfesorCursoMateria.id_profesor,
                ProfesorCursoMateria.id_curso,
                ProfesorCursoMateria.id_materia,
                func.concat(Persona.nombres, ' ', Persona.apellido_paterno).label("nombre_profesor"),
                Curso.nombre_curso.label("nombre_curso"),
                Materia.nombre_materia.label("nombre_materia")
            )
            .join(Profesor, Profesor.id_profesor == ProfesorCursoMateria.id_profesor)
            .join(Persona, Persona.id_persona == Profesor.id_persona)
            .join(Curso, Curso.id_curso == ProfesorCursoMateria.id_curso)
            .join(Materia, Materia.id_materia == ProfesorCursoMateria.id_materia)
            .filter(Profesor.id_profesor == id_profesor)
            .all()
        )

    @staticmethod
    def delete(db: Session, id_profesor: int, id_curso: int, id_materia: int) -> bool:
        """Elimina una asignación específica"""
        asignacion = db.query(ProfesorCursoMateria).filter_by(
            id_profesor=id_profesor,
            id_curso=id_curso,
            id_materia=id_materia
        ).first()
        
        if asignacion:
            db.delete(asignacion)
            db.commit()
            return True
        return False

    @staticmethod
    def exists(db: Session, id_profesor: int, id_curso: int, id_materia: int) -> bool:
        """Verifica si existe una asignación"""
        return db.query(ProfesorCursoMateria).filter_by(
            id_profesor=id_profesor,
            id_curso=id_curso,
            id_materia=id_materia
        ).first() is not None


# ============ CARGO REPOSITORY ============
class CargoRepository:

    @staticmethod
    def get_all(db: Session) -> List[Cargo]:
        """Obtiene todos los cargos"""
        return db.query(Cargo).all()

    @staticmethod
    def get_by_id(db: Session, id_cargo: int) -> Optional[Cargo]:
        """Obtiene un cargo por ID"""
        return db.query(Cargo).filter(Cargo.id_cargo == id_cargo).first()


# ============ BLOQUE HORARIO REPOSITORY ============
class BloqueHorarioRepository:

    @staticmethod
    def create(db: Session, data: dict) -> BloqueHorario:
        """Crea un bloque horario"""
        bloque = BloqueHorario(**data)
        db.add(bloque)
        db.commit()
        db.refresh(bloque)
        return bloque

    @staticmethod
    def get_all(db: Session, gestion: Optional[str] = None) -> List[BloqueHorario]:
        """Obtiene todos los bloques horarios"""
        query = db.query(BloqueHorario)
        
        if gestion:
            query = query.filter(BloqueHorario.gestion == gestion)
        
        return query.all()

    @staticmethod
    def get_by_id(db: Session, id_bloque: int) -> Optional[BloqueHorario]:
        """Obtiene un bloque por ID"""
        return (
            db.query(BloqueHorario)
            .filter(BloqueHorario.id_bloque == id_bloque)
            .first()
        )

    @staticmethod
    def get_by_profesor(db: Session, id_profesor: int, gestion: Optional[str] = None) -> List[BloqueHorario]:
        """Obtiene bloques de un profesor"""
        query = (
            db.query(BloqueHorario)
            .filter(BloqueHorario.id_profesor == id_profesor)
        )
        
        if gestion:
            query = query.filter(BloqueHorario.gestion == gestion)
        
        return query.all()

    @staticmethod
    def get_vista_bloques_profesor(db: Session, id_persona: Optional[int] = None, gestion: Optional[str] = None):
        """Consulta la vista vista_bloques_profesor"""
        query = "SELECT * FROM vista_bloques_profesor WHERE 1=1"
        params = {}
        
        if id_persona:
            query += " AND id_persona = :id_persona"
            params["id_persona"] = id_persona
        
        if gestion:
            query += " AND gestion = :gestion"
            params["gestion"] = gestion
        
        result = db.execute(text(query), params)
        return result.fetchall()

    @staticmethod
    def get_vista_carga_horaria(db: Session, id_persona: Optional[int] = None, gestion: Optional[str] = None):
        """Consulta la vista vista_carga_horaria_profesores"""
        query = "SELECT * FROM vista_carga_horaria_profesores WHERE 1=1"
        params = {}
        
        if id_persona:
            query += " AND id_persona = :id_persona"
            params["id_persona"] = id_persona
        
        if gestion:
            query += " AND gestion = :gestion"
            params["gestion"] = gestion
        
        result = db.execute(text(query), params)
        return result.fetchall()

    @staticmethod
    def get_vista_horario_semanal(db: Session, id_persona: Optional[int] = None, gestion: Optional[str] = None):
        """Consulta la vista vista_horario_semanal_profesor"""
        query = "SELECT * FROM vista_horario_semanal_profesor WHERE 1=1"
        params = {}
        
        if id_persona:
            query += " AND id_persona = :id_persona"
            params["id_persona"] = id_persona
        
        if gestion:
            query += " AND gestion = :gestion"
            params["gestion"] = gestion
        
        result = db.execute(text(query), params)
        return result.fetchall()

    @staticmethod
    def update(db: Session, bloque: BloqueHorario, data: dict) -> BloqueHorario:
        """Actualiza un bloque horario"""
        for key, value in data.items():
            if value is not None:
                setattr(bloque, key, value)
        db.commit()
        db.refresh(bloque)
        return bloque

    @staticmethod
    def delete(db: Session, bloque: BloqueHorario) -> None:
        """Elimina un bloque horario"""
        db.delete(bloque)
        db.commit()

    @staticmethod
    def check_conflicts(db: Session, id_profesor: int, dia_semana: str, 
                       hora_inicio, hora_fin, exclude_id: Optional[int] = None) -> bool:
        """Verifica si hay conflictos de horario para un profesor"""
        query = (
            db.query(BloqueHorario)
            .filter(
                BloqueHorario.id_profesor == id_profesor,
                BloqueHorario.dia_semana == dia_semana,
                BloqueHorario.hora_inicio < hora_fin,
                BloqueHorario.hora_fin > hora_inicio
            )
        )
        
        if exclude_id:
            query = query.filter(BloqueHorario.id_bloque != exclude_id)
        
        return query.first() is not None