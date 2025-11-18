from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from collections import defaultdict
from fastapi import HTTPException
from typing import List, Optional

from app.modules.profesores.dto.profesor_dto import (
    ProfesorCreateDTO, ProfesorReadDTO, ProfesorFullDTO, ProfesorUpdateDTO,
    MateriaReadDTO, MateriaCreateDTO,
    CursoReadDTO, CursoCreateDTO,
    AsignacionCreateDTO, AsignacionReadDTO, AsignacionReadNombreDTO,
    CargoReadDTO,
    BloqueHorarioCreateDTO, BloqueHorarioReadDTO, BloqueHorarioUpdateDTO,
    VistaBloqueProfesorDTO, VistaCargaHorariaDTO, VistaHorarioSemanalDTO
)
from app.modules.profesores.repositories.profesor_repository import (
    PersonaRepository, ProfesorRepository, MateriaRepository, CursoRepository, 
    AsignacionRepository, CargoRepository, BloqueHorarioRepository
)
from app.modules.profesores.models.profesor_models import BloqueHorario

# ============ PROFESOR SERVICE ============
class ProfesorService:

    @staticmethod
    def crear_profesor(db: Session, data: ProfesorCreateDTO) -> ProfesorReadDTO:
        """Crea un nuevo profesor con su persona"""
        # Validar CI único
        if PersonaRepository.exists_by_ci(db, data.ci):
            raise HTTPException(status_code=400, detail="Ya existe una persona con este CI")
        
        # Validar correo único si se proporciona
        if data.correo and PersonaRepository.exists_by_correo(db, data.correo):
            raise HTTPException(status_code=400, detail="Ya existe una persona con este correo")
        
        # Validar cargo si se proporciona
        if data.id_cargo:
            cargo = CargoRepository.get_by_id(db, data.id_cargo)
            if not cargo:
                raise HTTPException(status_code=404, detail="El cargo especificado no existe")
        
        try:
            # Separar datos de persona y profesor
            persona_data = {
                "ci": data.ci,
                "nombres": data.nombres,
                "apellido_paterno": data.apellido_paterno,
                "apellido_materno": data.apellido_materno,
                "direccion": data.direccion,
                "telefono": data.telefono,
                "correo": data.correo,
                "tipo_persona": "profesor",
                "id_cargo": data.id_cargo,
                "estado_laboral": data.estado_laboral or "activo",
                "años_experiencia": data.años_experiencia or 0,
                "fecha_ingreso": data.fecha_ingreso,
                "fecha_retiro": data.fecha_retiro,
                "motivo_retiro": data.motivo_retiro
            }
            
            profesor_data = {
                "especialidad": data.especialidad,
                "titulo_academico": data.titulo_academico,
                "nivel_enseñanza": data.nivel_enseñanza or "todos",
                "observaciones": data.observaciones_profesor
            }
            
            profesor = ProfesorRepository.create(db, persona_data, profesor_data)
            return ProfesorService._build_profesor_read_dto(profesor)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Error al crear el profesor: {str(e)}")

    @staticmethod
    def listar_profesores(db: Session) -> List[ProfesorReadDTO]:
        """Lista todos los profesores"""
        profesores = ProfesorRepository.get_all(db)
        return [ProfesorService._build_profesor_read_dto(p) for p in profesores]
    
    @staticmethod
    def listar_profesores_completo(db: Session) -> List[ProfesorFullDTO]:
        """Lista profesores con materias, cursos y carga horaria"""
        profesores = ProfesorRepository.get_all(db)
        asignaciones = AsignacionRepository.get_all(db)

        # Mapear asignaciones por profesor
        prof_map = defaultdict(lambda: {"cursos": set(), "materias": set()})
        for a in asignaciones:
            prof_map[a.id_profesor]["cursos"].add(a.id_curso)
            prof_map[a.id_profesor]["materias"].add(a.id_materia)

        resultado = []
        for p in profesores:
            # Calcular horas semanales desde bloques
            bloques = BloqueHorarioRepository.get_by_profesor(db, p.id_profesor)
            total_horas = sum([
                (b.hora_fin.hour + b.hora_fin.minute/60) - 
                (b.hora_inicio.hour + b.hora_inicio.minute/60) 
                for b in bloques
            ])
            
            dto_data = {
                "id_persona": p.persona.id_persona,
                "id_profesor": p.id_profesor,
                "ci": p.persona.ci,
                "nombres": p.persona.nombres,
                "apellido_paterno": p.persona.apellido_paterno,
                "apellido_materno": p.persona.apellido_materno,
                "direccion": p.persona.direccion,
                "telefono": p.persona.telefono,
                "correo": p.persona.correo,
                "tipo_persona": p.persona.tipo_persona,
                "id_cargo": p.persona.id_cargo,
                "nombre_cargo": p.persona.cargo.nombre_cargo if p.persona.cargo else None,
                "estado_laboral": p.persona.estado_laboral,
                "años_experiencia": p.persona.años_experiencia,
                "fecha_ingreso": p.persona.fecha_ingreso,
                "fecha_retiro": p.persona.fecha_retiro,
                "motivo_retiro": p.persona.motivo_retiro,
                "especialidad": p.especialidad,
                "titulo_academico": p.titulo_academico,
                "nivel_enseñanza": p.nivel_enseñanza,
                "observaciones_profesor": p.observaciones,
                "total_horas_semanales": round(total_horas, 2),
                "materias": [],
                "cursos": []
            }

            # Obtener nombres de cursos y materias
            if prof_map[p.id_profesor]["cursos"]:
                cursos = CursoRepository.get_by_ids(db, list(prof_map[p.id_profesor]["cursos"]))
                dto_data["cursos"] = [c.nombre_curso for c in cursos]

            if prof_map[p.id_profesor]["materias"]:
                materias = MateriaRepository.get_by_ids(db, list(prof_map[p.id_profesor]["materias"]))
                dto_data["materias"] = [m.nombre_materia for m in materias]

            resultado.append(ProfesorFullDTO(**dto_data))

        return resultado

    @staticmethod
    def obtener_profesor(db: Session, id_persona: int) -> Optional[ProfesorReadDTO]:
        """Obtiene un profesor por id_persona"""
        profesor = ProfesorRepository.get_by_id_persona(db, id_persona)
        if not profesor:
            return None
        return ProfesorService._build_profesor_read_dto(profesor)

    @staticmethod
    def actualizar_profesor(db: Session, id_persona: int, data: ProfesorUpdateDTO) -> Optional[ProfesorReadDTO]:
        """Actualiza un profesor"""
        profesor = ProfesorRepository.get_by_id_persona(db, id_persona)
        if not profesor:
            return None
        
        # Validar CI único
        if data.ci and data.ci != profesor.persona.ci:
            if PersonaRepository.exists_by_ci(db, data.ci, exclude_id=id_persona):
                raise HTTPException(status_code=400, detail="Ya existe una persona con este CI")
        
        # Validar correo único
        if data.correo and data.correo != profesor.persona.correo:
            if PersonaRepository.exists_by_correo(db, data.correo, exclude_id=id_persona):
                raise HTTPException(status_code=400, detail="Ya existe una persona con este correo")
        
        # Validar cargo
        if data.id_cargo:
            cargo = CargoRepository.get_by_id(db, data.id_cargo)
            if not cargo:
                raise HTTPException(status_code=404, detail="El cargo especificado no existe")
        
        try:
            # Separar datos
            persona_data = {
                k: v for k, v in data.dict(exclude_unset=True).items()
                if k in ["ci", "nombres", "apellido_paterno", "apellido_materno", 
                        "direccion", "telefono", "correo", "id_cargo", "estado_laboral",
                        "años_experiencia", "fecha_ingreso", "fecha_retiro", "motivo_retiro"]
            }
            
            profesor_data = {
                "especialidad": data.especialidad,
                "titulo_academico": data.titulo_academico,
                "nivel_enseñanza": data.nivel_enseñanza,
                "observaciones": data.observaciones_profesor
            }
            profesor_data = {k: v for k, v in profesor_data.items() if v is not None}
            
            profesor_actualizado = ProfesorRepository.update(db, profesor, persona_data, profesor_data)
            return ProfesorService._build_profesor_read_dto(profesor_actualizado)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al actualizar el profesor")

    @staticmethod
    def eliminar_profesor(db: Session, id_persona: int) -> bool:
        """Elimina un profesor y su persona"""
        profesor = ProfesorRepository.get_by_id_persona(db, id_persona)
        if not profesor:
            return False

        try:
            ProfesorRepository.delete(db, profesor)
            return True
        except Exception as e:
            print(f"[ERROR] No se pudo eliminar profesor {id_persona}: {e}")
            raise HTTPException(status_code=400, detail=f"No se puede eliminar el profesor: {str(e)}")

    @staticmethod
    def _build_profesor_read_dto(profesor) -> ProfesorReadDTO:
        """Construye un ProfesorReadDTO"""
        return ProfesorReadDTO(
            id_persona=profesor.persona.id_persona,
            id_profesor=profesor.id_profesor,
            ci=profesor.persona.ci,
            nombres=profesor.persona.nombres,
            apellido_paterno=profesor.persona.apellido_paterno,
            apellido_materno=profesor.persona.apellido_materno,
            direccion=profesor.persona.direccion,
            telefono=profesor.persona.telefono,
            correo=profesor.persona.correo,
            tipo_persona=profesor.persona.tipo_persona,
            id_cargo=profesor.persona.id_cargo,
            nombre_cargo=profesor.persona.cargo.nombre_cargo if profesor.persona.cargo else None,
            estado_laboral=profesor.persona.estado_laboral,
            años_experiencia=profesor.persona.años_experiencia,
            fecha_ingreso=profesor.persona.fecha_ingreso,
            fecha_retiro=profesor.persona.fecha_retiro,
            motivo_retiro=profesor.persona.motivo_retiro,
            especialidad=profesor.especialidad,
            titulo_academico=profesor.titulo_academico,
            nivel_enseñanza=profesor.nivel_enseñanza,
            observaciones_profesor=profesor.observaciones
        )


# ============ MATERIA SERVICE ============
class MateriaService:

    @staticmethod
    def crear_materia(db: Session, data: MateriaCreateDTO) -> MateriaReadDTO:
        try:
            materia = MateriaRepository.create(db, data.dict())
            return MateriaReadDTO.from_orm(materia)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al crear la materia")

    @staticmethod
    def listar_materias(db: Session) -> List[MateriaReadDTO]:
        materias = MateriaRepository.get_all(db)
        return [MateriaReadDTO.from_orm(m) for m in materias]

    @staticmethod
    def obtener_materia(db: Session, id_materia: int) -> Optional[MateriaReadDTO]:
        materia = MateriaRepository.get_by_id(db, id_materia)
        if not materia:
            return None
        return MateriaReadDTO.from_orm(materia)

    @staticmethod
    def actualizar_materia(db: Session, id_materia: int, data: MateriaCreateDTO) -> Optional[MateriaReadDTO]:
        materia = MateriaRepository.get_by_id(db, id_materia)
        if not materia:
            return None
        
        try:
            materia_actualizada = MateriaRepository.update(db, materia, data.dict())
            return MateriaReadDTO.from_orm(materia_actualizada)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al actualizar la materia")

    @staticmethod
    def eliminar_materia(db: Session, id_materia: int) -> Optional[MateriaReadDTO]:
        materia = MateriaRepository.get_by_id(db, id_materia)
        if not materia:
            return None
        
        try:
            materia_eliminada = MateriaRepository.delete(db, materia)
            return MateriaReadDTO.from_orm(materia_eliminada)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"No se puede eliminar la materia: {str(e)}")


# ============ CURSO SERVICE ============
class CursoService:

    @staticmethod
    def crear_curso(db: Session, data: CursoCreateDTO) -> CursoReadDTO:
        try:
            curso = CursoRepository.create(db, data.dict())
            return CursoReadDTO.from_orm(curso)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al crear el curso")

    @staticmethod
    def listar_cursos(db: Session) -> List[CursoReadDTO]:
        cursos = CursoRepository.get_all(db)
        return [CursoReadDTO.from_orm(c) for c in cursos]

    @staticmethod
    def obtener_curso(db: Session, id_curso: int) -> Optional[CursoReadDTO]:
        curso = CursoRepository.get_by_id(db, id_curso)
        if not curso:
            return None
        return CursoReadDTO.from_orm(curso)

    @staticmethod
    def actualizar_curso(db: Session, id_curso: int, data: CursoCreateDTO) -> Optional[CursoReadDTO]:
        curso = CursoRepository.get_by_id(db, id_curso)
        if not curso:
            return None
        
        try:
            curso_actualizado = CursoRepository.update(db, curso, data.dict())
            return CursoReadDTO.from_orm(curso_actualizado)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al actualizar el curso")

    @staticmethod
    def eliminar_curso(db: Session, id_curso: int) -> Optional[CursoReadDTO]:
        curso = CursoRepository.get_by_id(db, id_curso)
        if not curso:
            return None
        
        try:
            curso_eliminado = CursoRepository.delete(db, curso)
            return CursoReadDTO.from_orm(curso_eliminado)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"No se puede eliminar el curso: {str(e)}")


# ============ ASIGNACIÓN SERVICE ============
class AsignacionService:

    @staticmethod
    def asignar_materia(db: Session, data: AsignacionCreateDTO) -> AsignacionReadDTO:
        # Validar profesor
        profesor = ProfesorRepository.get_by_id_profesor(db, data.id_profesor)
        if not profesor:
            raise HTTPException(status_code=404, detail="El profesor no existe")
        
        # Validar curso
        curso = CursoRepository.get_by_id(db, data.id_curso)
        if not curso:
            raise HTTPException(status_code=404, detail="El curso no existe")
        
        # Validar materia
        materia = MateriaRepository.get_by_id(db, data.id_materia)
        if not materia:
            raise HTTPException(status_code=404, detail="La materia no existe")
        
        try:
            asignacion = AsignacionRepository.create(db, data.dict())
            return AsignacionReadDTO.from_orm(asignacion)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al crear la asignación")

    @staticmethod
    def listar_asignaciones(db: Session) -> List[AsignacionReadDTO]:
        asignaciones = AsignacionRepository.get_all(db)
        return [AsignacionReadDTO.from_orm(a) for a in asignaciones]

    @staticmethod
    def listar_por_profesor(db: Session, id_profesor: int) -> List[AsignacionReadNombreDTO]:
        profesor = ProfesorRepository.get_by_id_profesor(db, id_profesor)
        if not profesor:
            raise HTTPException(status_code=404, detail="El profesor no existe")
        
        asignaciones = AsignacionRepository.get_by_profesor_con_nombres(db, id_profesor)
        return [AsignacionReadNombreDTO.from_orm(a) for a in asignaciones]

    @staticmethod
    def eliminar_asignacion(db: Session, id_profesor: int, id_curso: int, id_materia: int) -> bool:
        if not AsignacionRepository.exists(db, id_profesor, id_curso, id_materia):
            raise HTTPException(status_code=404, detail="La asignación no existe")
        
        # Eliminar primero los bloques horarios asociados
        bloques = db.query(BloqueHorario).filter(
            BloqueHorario.id_profesor == id_profesor,
            BloqueHorario.id_curso == id_curso,
            BloqueHorario.id_materia == id_materia
        ).all()
        
        for bloque in bloques:
            db.delete(bloque)
        
        db.commit()
        
        # Ahora eliminar la asignación
        return AsignacionRepository.delete(db, id_profesor, id_curso, id_materia)


# ============ CARGO SERVICE ============
class CargoService:

    @staticmethod
    def listar_cargos(db: Session) -> List[CargoReadDTO]:
        cargos = CargoRepository.get_all(db)
        return [CargoReadDTO.from_orm(c) for c in cargos]

    @staticmethod
    def obtener_cargo(db: Session, id_cargo: int) -> Optional[CargoReadDTO]:
        cargo = CargoRepository.get_by_id(db, id_cargo)
        if not cargo:
            return None
        return CargoReadDTO.from_orm(cargo)


# ============ BLOQUE HORARIO SERVICE ============
class BloqueHorarioService:

    @staticmethod
    def crear_bloque(db: Session, data: BloqueHorarioCreateDTO) -> BloqueHorarioReadDTO:
        # Validar profesor
        profesor = ProfesorRepository.get_by_id_profesor(db, data.id_profesor)
        if not profesor:
            raise HTTPException(status_code=404, detail="El profesor no existe")
        
        # Validar curso
        curso = CursoRepository.get_by_id(db, data.id_curso)
        if not curso:
            raise HTTPException(status_code=404, detail="El curso no existe")
        
        # Validar materia
        materia = MateriaRepository.get_by_id(db, data.id_materia)
        if not materia:
            raise HTTPException(status_code=404, detail="La materia no existe")
        
        # Nota: permitimos crear bloques incluso si la asignación profesor-curso-materia
        # no está todavía persistida en la BD (p. ej. asignaciones pendientes del frontend).
        # Ya validamos que profesor, curso y materia existen; la integridad referencial está
        # garantizada por las FK en la tabla bloques_horarios.
        # Si en su negocio necesita forzar la existencia de la asignación, vuelva a activar
        # la comprobación usando AsignacionRepository.exists(...)
        
        # Convertir strings de hora a objetos time
        from datetime import datetime, time as dt_time
        try:
            hora_inicio = datetime.strptime(data.hora_inicio, "%H:%M:%S").time()
            hora_fin = datetime.strptime(data.hora_fin, "%H:%M:%S").time()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de hora inválido. Use HH:MM:SS"
            )
        
        # Verificar conflictos
        if BloqueHorarioRepository.check_conflicts(
            db, data.id_profesor, data.dia_semana, 
            hora_inicio, hora_fin
        ):
            raise HTTPException(
                status_code=400, 
                detail="El profesor ya tiene un bloque asignado en este horario"
            )
        
        try:
            bloque_data = data.dict()
            bloque_data['hora_inicio'] = hora_inicio
            bloque_data['hora_fin'] = hora_fin
            bloque = BloqueHorarioRepository.create(db, bloque_data)
            return BloqueHorarioService._build_bloque_dto(db, bloque)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al crear el bloque horario")

    @staticmethod
    def listar_bloques(db: Session, gestion: Optional[str] = None) -> List[BloqueHorarioReadDTO]:
        bloques = BloqueHorarioRepository.get_all(db, gestion)
        return [BloqueHorarioService._build_bloque_dto(db, b) for b in bloques]

    @staticmethod
    def obtener_bloque(db: Session, id_bloque: int) -> Optional[BloqueHorarioReadDTO]:
        bloque = BloqueHorarioRepository.get_by_id(db, id_bloque)
        if not bloque:
            return None
        return BloqueHorarioService._build_bloque_dto(db, bloque)

    @staticmethod
    def listar_por_profesor(db: Session, id_profesor: int, gestion: Optional[str] = None) -> List[BloqueHorarioReadDTO]:
        profesor = ProfesorRepository.get_by_id_profesor(db, id_profesor)
        if not profesor:
            raise HTTPException(status_code=404, detail="El profesor no existe")
        
        bloques = BloqueHorarioRepository.get_by_profesor(db, id_profesor, gestion)
        return [BloqueHorarioService._build_bloque_dto(db, b) for b in bloques]

    @staticmethod
    def actualizar_bloque(db: Session, id_bloque: int, data: BloqueHorarioUpdateDTO) -> Optional[BloqueHorarioReadDTO]:
        bloque = BloqueHorarioRepository.get_by_id(db, id_bloque)
        if not bloque:
            return None
        
        # Convertir strings de hora a objetos time si se proporcionan
        from datetime import datetime
        update_data = data.dict(exclude_unset=True)
        
        if 'hora_inicio' in update_data and update_data['hora_inicio']:
            try:
                update_data['hora_inicio'] = datetime.strptime(update_data['hora_inicio'], "%H:%M:%S").time()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de hora_inicio inválido")
        
        if 'hora_fin' in update_data and update_data['hora_fin']:
            try:
                update_data['hora_fin'] = datetime.strptime(update_data['hora_fin'], "%H:%M:%S").time()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de hora_fin inválido")
        
        # Verificar conflictos si se cambia el horario
        if any(k in update_data for k in ['dia_semana', 'hora_inicio', 'hora_fin']):
            dia = update_data.get('dia_semana', bloque.dia_semana)
            inicio = update_data.get('hora_inicio', bloque.hora_inicio)
            fin = update_data.get('hora_fin', bloque.hora_fin)
            
            if BloqueHorarioRepository.check_conflicts(
                db, bloque.id_profesor, dia, inicio, fin, exclude_id=id_bloque
            ):
                raise HTTPException(
                    status_code=400, 
                    detail="El profesor ya tiene un bloque asignado en este horario"
                )
        
        try:
            bloque_actualizado = BloqueHorarioRepository.update(db, bloque, update_data)
            return BloqueHorarioService._build_bloque_dto(db, bloque_actualizado)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Error al actualizar el bloque horario")

    @staticmethod
    def eliminar_bloque(db: Session, id_bloque: int) -> bool:
        bloque = BloqueHorarioRepository.get_by_id(db, id_bloque)
        if not bloque:
            return False
        
        try:
            BloqueHorarioRepository.delete(db, bloque)
            return True
        except Exception as e:
            print(f"[ERROR] No se pudo eliminar bloque {id_bloque}: {e}")
            raise HTTPException(status_code=400, detail=f"No se puede eliminar el bloque: {str(e)}")

    @staticmethod
    def obtener_vista_bloques_profesor(db: Session, id_persona: Optional[int] = None, gestion: Optional[str] = None):
        """Obtiene datos de la vista vista_bloques_profesor"""
        try:
            resultados = BloqueHorarioRepository.get_vista_bloques_profesor(db, id_persona, gestion)
            if not resultados:
                return []
            
            # Convertir RowMapping a diccionarios simples
            return [{
                'id_persona': row.id_persona,
                'nombre_completo': row.nombre_completo,
                'id_bloque': row.id_bloque,
                'dia_semana': row.dia_semana,
                'hora_inicio': str(row.hora_inicio) if row.hora_inicio else None,
                'hora_fin': str(row.hora_fin) if row.hora_fin else None,
                'horas_bloque': float(row.horas_bloque) if row.horas_bloque else 0.0,
                'nombre_materia': row.nombre_materia,
                'nombre_curso': row.nombre_curso,
                'nivel': row.nivel,
                'gestion': row.gestion,
                'observaciones': row.observaciones
            } for row in resultados]
        except Exception as e:
            print(f"Error en vista_bloques_profesor: {e}")
            raise HTTPException(status_code=500, detail=f"Error al consultar la vista: {str(e)}")

    @staticmethod
    def obtener_vista_carga_horaria(db: Session, id_persona: Optional[int] = None, gestion: Optional[str] = None):
        """Obtiene datos de la vista vista_carga_horaria_profesores"""
        try:
            resultados = BloqueHorarioRepository.get_vista_carga_horaria(db, id_persona, gestion)
            if not resultados:
                return []
            
            return [{
                'id_persona': row.id_persona,
                'ci': row.ci,
                'nombre_completo': row.nombre_completo,
                'estado_laboral': row.estado_laboral,
                'especialidad': row.especialidad,
                'titulo_academico': row.titulo_academico,
                'gestion': row.gestion,
                'total_bloques': int(row.total_bloques) if row.total_bloques else 0,
                'carga_horaria_semanal': float(row.carga_horaria_semanal) if row.carga_horaria_semanal else 0.0,
                'materias': row.materias.split(',') if row.materias else [],
                'cursos': row.cursos.split(',') if row.cursos else []
            } for row in resultados]
        except Exception as e:
            print(f"Error en vista_carga_horaria: {e}")
            raise HTTPException(status_code=500, detail=f"Error al consultar la vista: {str(e)}")

    @staticmethod
    def obtener_vista_horario_semanal(db: Session, id_persona: Optional[int] = None, gestion: Optional[str] = None):
        """Obtiene datos de la vista vista_horario_semanal_profesor"""
        try:
            resultados = BloqueHorarioRepository.get_vista_horario_semanal(db, id_persona, gestion)
            if not resultados:
                return []
            
            return [{
                'id_persona': row.id_persona,
                'nombre_completo': row.nombre_completo,
                'gestion': row.gestion,
                'lunes': row.lunes.split(';') if row.lunes else [],
                'martes': row.martes.split(';') if row.martes else [],
                'miercoles': row.miercoles.split(';') if row.miercoles else [],
                'jueves': row.jueves.split(';') if row.jueves else [],
                'viernes': row.viernes.split(';') if row.viernes else [],
                'sabado': row.sabado.split(';') if row.sabado else []
            } for row in resultados]
        except Exception as e:
            print(f"Error en vista_horario_semanal: {e}")
            raise HTTPException(status_code=500, detail=f"Error al consultar la vista: {str(e)}")

    @staticmethod
    def _build_bloque_dto(db: Session, bloque) -> BloqueHorarioReadDTO:
        """Construye BloqueHorarioReadDTO con nombres"""
        profesor = ProfesorRepository.get_by_id_profesor(db, bloque.id_profesor)
        curso = CursoRepository.get_by_id(db, bloque.id_curso)
        materia = MateriaRepository.get_by_id(db, bloque.id_materia)
        
        return BloqueHorarioReadDTO(
            id_bloque=bloque.id_bloque,
            id_profesor=bloque.id_profesor,
            id_curso=bloque.id_curso,
            id_materia=bloque.id_materia,
            dia_semana=bloque.dia_semana,
            hora_inicio=bloque.hora_inicio,
            hora_fin=bloque.hora_fin,
            gestion=bloque.gestion,
            fecha_registro=bloque.fecha_registro,
            observaciones=bloque.observaciones,
            nombre_profesor=f"{profesor.persona.nombres} {profesor.persona.apellido_paterno}" if profesor else None,
            nombre_curso=curso.nombre_curso if curso else None,
            nombre_materia=materia.nombre_materia if materia else None
        )