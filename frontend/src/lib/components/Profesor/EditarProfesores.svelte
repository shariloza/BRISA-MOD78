<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import AsignarMaterias from "../Materias/AsignarMaterias.svelte";
  import AsignarCursos from "../Cursos/AsignarCursos.svelte";
  import AsignarCarga from "../Cargas/AsignarCarga.svelte";

  interface Profesor {
    id_persona?: number;
    id_profesor?: number;
    ci: string;
    nombres: string;
    apellido_paterno: string;
    apellido_materno?: string;
    direccion?: string;
    telefono?: string;
    correo: string;
    tipo_persona?: string;
    estado_laboral?: string;
    especialidad?: string;
    titulo_academico?: string;
    nivel_enseñanza?: string;
    observaciones_profesor?: string;
    asignaciones?: any[];
  }

  export let profesor: Profesor | null = null;

  const API_URL = "http://localhost:8000/api/profesores";

  const dispatch = createEventDispatcher<{
    save: any;
    cancel: void;
    delete: { id: number };
  }>();

  type AlertType = "success" | "error" | "warning" | "info" | null;

  // === ESTADOS PRINCIPALES DEL FORM ===
  let formData = {
    ci: "",
    nombres: "",
    apellido_paterno: "",
    apellido_materno: "",
    direccion: "",
    telefono: "",
    correo: "",
    tipo_persona: "profesor",
    estado_laboral: "activo",
    id_persona: null as number | null,
    id_profesor: null as number | null,
    especialidad: "",
    titulo_academico: "",
    nivel_enseñanza: "todos",
    observaciones_profesor: "",
    id_cargo: null as number | null,
  };

  let formErrors = {
    ci: false,
    nombres: false,
    apellido_paterno: false,
    correo: false,
    especialidad: false,
    titulo_academico: false,
  };

  let cargando = false;
  let eliminando = false;
  let errorMessage = "";
  let alertType: AlertType = null;
  let cargandoDatos = false;
  let hayCambiosPendientes = false;

  // === ASIGNACIONES ===
  let asignacionesPendientes: any[] = [];
  let asignacionesGuardadas: any[] = [];
  let asignacionesParaEliminar: any[] = [];

  // === BLOQUES PENDIENTES (desde modal AsignarCarga) ===
  let bloquesPendientesCrear: any[] = [];
  let bloquesPendientesActualizar: any[] = [];
  let bloquesPendientesEliminar: any[] = [];

  // === CARGOS ===
  let cargos: any[] = [];

  // === ESTADOS PARA MODALES DE ASIGNACIÓN ===
  let mostrarModalMaterias = false;
  let mostrarModalCursos = false;
  let mostrarModalCarga = false;
  let materiaSeleccionada: any = null;
  let cursoSeleccionado: any = null;

  // ========= CARGA DE DATOS DESDE API =========
  async function cargarCargos() {
    try {
      const res = await fetch(`${API_URL}/cargos`);
      if (res.ok) cargos = await res.json();
    } catch (err) {
      console.error("Error cargando cargos:", err);
    }
  }

  async function cargarProfesor(p: Profesor) {
    if (!p?.id_persona) {
      resetForm();
      return;
    }

    cargandoDatos = true;
    errorMessage = "";
    alertType = null;

    try {
      const res = await fetch(`${API_URL}/${p.id_persona}`);
      if (!res.ok) throw new Error("No se pudo cargar el profesor");
      const data = await res.json();

      formData = {
        ci: data.ci || "",
        nombres: data.nombres || "",
        apellido_paterno: data.apellido_paterno || "",
        apellido_materno: data.apellido_materno || "",
        direccion: data.direccion || "",
        telefono: data.telefono || "",
        correo: data.correo || "",
        tipo_persona: data.tipo_persona || "profesor",
        estado_laboral: data.estado_laboral || "activo",
        id_persona: data.id_persona,
        id_profesor: data.id_profesor,
        especialidad: data.especialidad || "",
        titulo_academico: data.titulo_academico || "",
        nivel_enseñanza: data.nivel_enseñanza || "todos",
        observaciones_profesor: data.observaciones_profesor || "",
        id_cargo: data.id_cargo || null,
      };

      await cargarAsignaciones(data.id_persona);
      hayCambiosPendientes = false;
    } catch (err: any) {
      alertType = "error";
      errorMessage = `Error: ${err.message}`;
    } finally {
      cargandoDatos = false;
    }
  }

  async function cargarAsignaciones(idPersona: number) {
    try {
      const res = await fetch(`${API_URL}/${idPersona}/asignaciones`);
      if (res.ok) {
        const data = await res.json();
        asignacionesGuardadas = Array.isArray(data)
          ? data.map((a: any) => ({
              id_materia: a.id_materia,
              id_curso: a.id_curso,
              nombre_materia: a.nombre_materia,
              nombre_curso: a.nombre_curso,
              existeEnBD: true,
            }))
          : [];
      } else {
        console.error("Error cargando asignaciones:", res.status);
      }
    } catch (err) {
      console.error("Error cargando asignaciones:", err);
    }
  }

  function resetForm() {
    formData = {
      ci: "",
      nombres: "",
      apellido_paterno: "",
      apellido_materno: "",
      direccion: "",
      telefono: "",
      correo: "",
      tipo_persona: "profesor",
      estado_laboral: "activo",
      id_persona: null,
      id_profesor: null,
      especialidad: "",
      titulo_academico: "",
      nivel_enseñanza: "todos",
      observaciones_profesor: "",
      id_cargo: null,
    };

    asignacionesPendientes = [];
    asignacionesGuardadas = [];
    asignacionesParaEliminar = [];

    formErrors = {
      ci: false,
      nombres: false,
      apellido_paterno: false,
      correo: false,
      especialidad: false,
      titulo_academico: false,
    };

    errorMessage = "";
    alertType = null;
    hayCambiosPendientes = false;
    materiaSeleccionada = null;
    cursoSeleccionado = null;

    bloquesPendientesCrear = [];
    bloquesPendientesActualizar = [];
    bloquesPendientesEliminar = [];
  }

  // ========= VALIDACIÓN =========
  function validarForm() {
    let ok = true;
    formErrors = {
      ci: false,
      nombres: false,
      apellido_paterno: false,
      correo: false,
      especialidad: false,
      titulo_academico: false,
    };

    if (!formData.ci?.trim()) {
      formErrors.ci = true;
      ok = false;
    }
    if (!formData.nombres?.trim()) {
      formErrors.nombres = true;
      ok = false;
    }
    if (!formData.apellido_paterno?.trim()) {
      formErrors.apellido_paterno = true;
      ok = false;
    }
    if (!formData.correo?.includes("@")) {
      formErrors.correo = true;
      ok = false;
    }
    if (!formData.especialidad?.trim()) {
      formErrors.especialidad = true;
      ok = false;
    }
    if (!formData.titulo_academico?.trim()) {
      formErrors.titulo_academico = true;
      ok = false;
    }

    return ok;
  }

  // ========= GUARDADO GENERAL =========
  async function guardarCambios() {
    if (!validarForm()) {
      alertType = "warning";
      errorMessage = "Complete todos los campos requeridos (*)";
      return;
    }

    if (!formData.id_persona) {
      alertType = "error";
      errorMessage = "ID de profesor no válido";
      return;
    }

    cargando = true;
    errorMessage = "";
    alertType = null;

    try {
      // Actualizar datos principales
      const resProf = await fetch(`${API_URL}/${formData.id_persona}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ci: formData.ci,
          nombres: formData.nombres,
          apellido_paterno: formData.apellido_paterno,
          apellido_materno: formData.apellido_materno || null,
          direccion: formData.direccion || null,
          telefono: formData.telefono || null,
          correo: formData.correo,
          estado_laboral: formData.estado_laboral,
          especialidad: formData.especialidad,
          titulo_academico: formData.titulo_academico,
          nivel_enseñanza: formData.nivel_enseñanza,
          observaciones_profesor: formData.observaciones_profesor || null,
          id_cargo: formData.id_cargo,
        }),
      });

      if (!resProf.ok) {
        const errorData = await resProf.json();
        throw new Error(
          errorData.detail || "Error al actualizar los datos del profesor",
        );
      }

      const profActualizado = await resProf.json();

      // Eliminar asignaciones
      if (asignacionesParaEliminar.length > 0) {
        for (const asignacion of asignacionesParaEliminar) {
          const res = await fetch(
            `${API_URL}/asignaciones?id_profesor=${profActualizado.id_profesor}&id_curso=${asignacion.id_curso}&id_materia=${asignacion.id_materia}`,
            { method: "DELETE" },
          );
          if (!res.ok) {
            throw new Error(
              `Error al eliminar asignación: ${asignacion.nombre_materia}`,
            );
          }
        }
      }

      // Crear nuevas asignaciones
      if (asignacionesPendientes.length > 0) {
        for (const asignacion of asignacionesPendientes) {
          const res = await fetch(`${API_URL}/asignaciones`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              id_profesor: profActualizado.id_profesor,
              id_materia: asignacion.id_materia,
              id_curso: asignacion.id_curso,
            }),
          });
          if (!res.ok) {
            throw new Error(
              `Error al crear asignación: ${asignacion.nombre_materia}`,
            );
          }
        }
      }

      // BLOQUES: eliminar
      if (bloquesPendientesEliminar.length > 0) {
        for (const b of bloquesPendientesEliminar) {
          if (b.id_bloque) {
            const res = await fetch(`${API_URL}/bloques/${b.id_bloque}`, {
              method: "DELETE",
            });
            if (!res.ok) {
              throw new Error(`Error al eliminar bloque ${b.id_bloque}`);
            }
          }
        }
      }

      // BLOQUES: actualizar
      if (bloquesPendientesActualizar.length > 0) {
        for (const b of bloquesPendientesActualizar) {
          const body = {
            id_profesor: profActualizado.id_profesor,
            id_curso: b.id_curso,
            id_materia: b.id_materia,
            dia_semana: b.dia_semana,
            hora_inicio:
              b.hora_inicio && b.hora_inicio.split(":").length === 2
                ? `${b.hora_inicio}:00`
                : b.hora_inicio,
            hora_fin:
              b.hora_fin && b.hora_fin.split(":").length === 2
                ? `${b.hora_fin}:00`
                : b.hora_fin,
            gestion: b.gestion,
            observaciones: b.observaciones || null,
          };
          const res = await fetch(`${API_URL}/bloques/${b.id_bloque}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          });
          if (!res.ok) {
            throw new Error(`Error al actualizar bloque ${b.id_bloque}`);
          }
        }
      }

      // BLOQUES: crear
      if (bloquesPendientesCrear.length > 0) {
        for (const b of bloquesPendientesCrear) {
          const body = {
            id_profesor: profActualizado.id_profesor,
            id_curso: b.id_curso,
            id_materia: b.id_materia,
            dia_semana: b.dia_semana,
            hora_inicio:
              b.hora_inicio && b.hora_inicio.split(":").length === 2
                ? `${b.hora_inicio}:00`
                : b.hora_inicio,
            hora_fin:
              b.hora_fin && b.hora_fin.split(":").length === 2
                ? `${b.hora_fin}:00`
                : b.hora_fin,
            gestion: b.gestion,
            observaciones: b.observaciones || null,
          };
          const res = await fetch(`${API_URL}/bloques`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          });
          if (!res.ok) {
            throw new Error(`Error al crear bloque para ${b.nombre_materia}`);
          }
        }
      }

      bloquesPendientesCrear = [];
      bloquesPendientesActualizar = [];
      bloquesPendientesEliminar = [];

      alertType = "success";
      errorMessage = "Profesor actualizado exitosamente";
      hayCambiosPendientes = false;

      setTimeout(() => {
        cargarProfesor(profActualizado);
        dispatch("save", profActualizado);
      }, 800);
    } catch (err: any) {
      alertType = "error";
      errorMessage = `Error: ${err.message}`;
    } finally {
      cargando = false;
    }
  }

  // ========= MANEJO DE MODALES =========
  function abrirModalMaterias() {
    mostrarModalMaterias = true;
  }

  function abrirModalCursos() {
    if (!materiaSeleccionada) {
      alertType = "warning";
      errorMessage = "Primero seleccione una materia";
      return;
    }
    mostrarModalCursos = true;
  }

  function abrirModalCarga() {
    if (!formData.id_profesor) {
      alertType = "warning";
      errorMessage = "Guarde primero los datos del profesor";
      return;
    }
    mostrarModalCarga = true;
  }

  function onGuardarCargaTemporal(e: CustomEvent) {
    const { bloques, eliminar } = e.detail;
    bloquesPendientesCrear = bloques
      .filter((b: any) => !b.id_bloque)
      .map((b: any) => ({ ...b }));
    bloquesPendientesActualizar = bloques
      .filter((b: any) => b.id_bloque)
      .map((b: any) => ({ ...b }));
    bloquesPendientesEliminar = eliminar || [];

    hayCambiosPendientes = true;
    mostrarModalCarga = false;
    alertType = "info";
    errorMessage =
      "Cambios de carga horaria preparados. Presione “Guardar Cambios” para persistirlos.";
  }

  function onMateriaSeleccionada(e: CustomEvent) {
    materiaSeleccionada = e.detail.materia;
    mostrarModalMaterias = false;
    cursoSeleccionado = null;
  }

  function onCursoSeleccionado(e: CustomEvent) {
    cursoSeleccionado = e.detail.curso;
    mostrarModalCursos = false;

    if (materiaSeleccionada && cursoSeleccionado) {
      const nuevaAsignacion = {
        id_materia: materiaSeleccionada.id_materia,
        id_curso: cursoSeleccionado.id_curso,
        nombre_materia: materiaSeleccionada.nombre_materia,
        nombre_curso: cursoSeleccionado.nombre_curso,
      };

      const existe =
        asignacionesPendientes.some(
          (a) =>
            a.id_materia === nuevaAsignacion.id_materia &&
            a.id_curso === nuevaAsignacion.id_curso,
        ) ||
        asignacionesGuardadas.some(
          (a) =>
            a.id_materia === nuevaAsignacion.id_materia &&
            a.id_curso === nuevaAsignacion.id_curso,
        );

      if (!existe) {
        asignacionesPendientes = [...asignacionesPendientes, nuevaAsignacion];
        hayCambiosPendientes = true;
        materiaSeleccionada = null;
        cursoSeleccionado = null;
      } else {
        alertType = "warning";
        errorMessage = "Esta combinación ya existe";
      }
    }
  }

  function eliminarAsignacionPendiente(index: number) {
    asignacionesPendientes = asignacionesPendientes.filter(
      (_, i) => i !== index,
    );
    hayCambiosPendientes =
      asignacionesPendientes.length > 0 || asignacionesParaEliminar.length > 0;
  }

  function onMarcarEliminar(e: { detail: { index: number; asignacion: any } }) {
    const { index, asignacion } = e.detail;
    asignacionesGuardadas = asignacionesGuardadas.filter((_, i) => i !== index);
    asignacionesParaEliminar = [...asignacionesParaEliminar, asignacion];
    hayCambiosPendientes = true;
  }

  function onRestaurarAsignacion(e: { detail: { index: number } }) {
    const { index } = e.detail;
    const asig = asignacionesParaEliminar[index];
    asignacionesGuardadas = [...asignacionesGuardadas, asig];
    asignacionesParaEliminar = asignacionesParaEliminar.filter(
      (_, i) => i !== index,
    );
    hayCambiosPendientes =
      asignacionesPendientes.length > 0 || asignacionesParaEliminar.length > 0;
  }

  // ========= ELIMINAR PROFESOR =========
  async function eliminarProfesor() {
    if (!formData.id_persona) return;

    if (
      !confirm(
        "¿Está seguro de eliminar este profesor? Esta acción no se puede deshacer.",
      )
    ) {
      return;
    }

    eliminando = true;
    try {
      const res = await fetch(`${API_URL}/${formData.id_persona}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error("Error al eliminar el profesor");

      dispatch("delete", { id: formData.id_persona });
      alertType = "success";
      errorMessage = "Profesor eliminado exitosamente";
      resetForm();
    } catch (err: any) {
      alertType = "error";
      errorMessage = `Error: ${err.message}`;
    } finally {
      eliminando = false;
    }
  }

  // ========= CANCELAR =========
  function cancelar() {
    if (hayCambiosPendientes) {
      if (!confirm("Tiene cambios pendientes. ¿Está seguro de cancelar?")) {
        return;
      }
    }
    dispatch("cancel");
  }

  function onInputChange() {
    hayCambiosPendientes = true;
  }

  onMount(() => {
    cargarCargos();
    if (profesor) {
      cargarProfesor(profesor);
    }
  });

  $: if (profesor && profesor.id_persona !== formData.id_persona) {
    cargarProfesor(profesor);
  }
</script>

<div class="editar-profesor-page">
  <div class="editar-profesor-container">
    <div class="editar-profesor">
      <!-- HEADER -->
      <div class="header">
        <div class="header-left">
          <div class="title-row">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                <path
                  d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4 0-7 2-7 4v1h14v-1c0-2-3-4-7-4Z"
                  fill="currentColor"
                />
              </svg>
            </span>
            <h1>Editar Profesor</h1>
          </div>
          {#if formData.id_persona}
            <span class="profesor-id">
              <span>ID</span>
              <span class="profesor-id-value">{formData.id_persona}</span>
            </span>
          {/if}
        </div>

        <div class="actions">
          <button
            class="btn-delete"
            on:click={eliminarProfesor}
            disabled={eliminando || cargando}
          >
            {#if eliminando}
              <span class="spinner"></span>
              <span>Eliminando</span>
            {:else}
              <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                <path
                  d="M3 6h18"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                />
                <path
                  d="M10 4h4a1 1 0 0 1 1 1v1H9V5a1 1 0 0 1 1-1Z"
                  fill="currentColor"
                />
                <rect
                  x="6"
                  y="7"
                  width="12"
                  height="13"
                  rx="1"
                  stroke="currentColor"
                  stroke-width="1.5"
                  fill="none"
                />
                <path
                  d="M10 11v6M14 11v6"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                />
              </svg>
              <span>Eliminar</span>
            {/if}
          </button>

          <button
            class="btn-outline"
            on:click={cancelar}
            disabled={cargando || eliminando}
          >
            <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
              <path
                d="M15 5 8 12l7 7"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <span>Cancelar</span>
          </button>

          <button
            class="btn-primary"
            on:click={guardarCambios}
            disabled={cargando || eliminando || !hayCambiosPendientes}
          >
            {#if cargando}
              <span class="spinner"></span>
              <span>Guardando</span>
            {:else}
              <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                <path
                  d="M5 5h14v14H5Z"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linejoin="round"
                />
                <path
                  d="M9 12.5 11 14.5 15 9.5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              <span>Guardar Cambios</span>
            {/if}
          </button>
        </div>
      </div>

      <!-- ALERTAS -->
      {#if errorMessage}
        <div
          class="alert {alertType === 'success'
            ? 'alert-success'
            : alertType === 'error'
              ? 'alert-error'
              : alertType === 'warning'
                ? 'alert-warning'
                : 'alert-info'}"
        >
          <span class="alert-icon">
            {#if alertType === "success"}
              <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                <path
                  d="M12 2a10 10 0 1 0 10 10A10.011 10.011 0 0 0 12 2Zm-1 13.5-3.5-3.5L9 10.5l2 2 4-4 1.5 1.5Z"
                  fill="currentColor"
                />
              </svg>
            {:else if alertType === "error"}
              <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                <path
                  d="M12 2a10 10 0 1 0 10 10A10.011 10.011 0 0 0 12 2Zm3 13.59L15.59 15 12 11.41 8.41 15 7 13.59 10.59 10 7 6.41 8.41 5 12 8.59 15.59 5 17 6.41 13.41 10 17 13.59Z"
                  fill="currentColor"
                />
              </svg>
            {:else if alertType === "warning"}
              <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                <path
                  d="M1 21h22L12 2 1 21Zm12-3h-2v-2h2Zm0-4h-2v-4h2Z"
                  fill="currentColor"
                />
              </svg>
            {:else}
              <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                <path
                  d="M12 2a10 10 0 1 0 10 10A10.011 10.011 0 0 0 12 2Zm1 15h-2v-6h2Zm0-8h-2V7h2Z"
                  fill="currentColor"
                />
              </svg>
            {/if}
          </span>
          <span>{errorMessage}</span>
        </div>
      {/if}

      {#if cargandoDatos}
        <div class="alert alert-info">
          <span class="alert-icon">
            <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
              <path
                d="M12 2a10 10 0 1 0 10 10A10.011 10.011 0 0 0 12 2Zm1 15h-2v-6h2Zm0-8h-2V7h2Z"
                fill="currentColor"
              />
            </svg>
          </span>
          <span>
            <span class="spinner"></span>
            Cargando datos del profesor...
          </span>
        </div>
      {/if}

      {#if hayCambiosPendientes && !cargandoDatos}
        <div class="alert alert-warning">
          <span class="alert-icon">
            <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
              <path
                d="M1 21h22L12 2 1 21Zm12-3h-2v-2h2Zm0-4h-2v-4h2Z"
                fill="currentColor"
              />
            </svg>
          </span>
          <span>Tiene cambios pendientes. No olvide guardar.</span>
        </div>
      {/if}

      <!-- FORMULARIO PRINCIPAL -->
      <div class="form-content" on:input={onInputChange}>
        <!-- INFORMACIÓN PERSONAL -->
        <section>
          <div class="section-header">
            <div class="section-title">
              <span class="section-icon">
                <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                  <path
                    d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4 0-7 2-7 4v1h14v-1c0-2-3-4-7-4Z"
                    fill="currentColor"
                  />
                </svg>
              </span>
              <div>
                <h2>Información Personal</h2>
                <p>Datos de identificación del profesor.</p>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class:error={formErrors.ci}>
                Cédula de Identidad <span class="required">*</span>
              </label>
              <input
                type="text"
                bind:value={formData.ci}
                disabled={cargando || eliminando}
                class:error={formErrors.ci}
                placeholder="Ej: 1234567"
              />
            </div>
            <div class="form-group">
              <label>Estado Laboral</label>
              <select
                bind:value={formData.estado_laboral}
                disabled={cargando || eliminando}
              >
                <option value="activo">Activo</option>
                <option value="inactivo">Inactivo</option>
                <option value="licencia">Licencia</option>
                <option value="jubilado">Jubilado</option>
              </select>
            </div>
          </div>

          <div class="form-row full-row">
            <div class="form-group full-width">
              <label class:error={formErrors.nombres}>
                Nombres Completos <span class="required">*</span>
              </label>
              <input
                type="text"
                bind:value={formData.nombres}
                disabled={cargando || eliminando}
                class:error={formErrors.nombres}
                placeholder="Ej: Nombre completo"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class:error={formErrors.apellido_paterno}>
                Apellido Paterno <span class="required">*</span>
              </label>
              <input
                type="text"
                bind:value={formData.apellido_paterno}
                disabled={cargando || eliminando}
                class:error={formErrors.apellido_paterno}
                placeholder="Ej: Apellido"
              />
            </div>
            <div class="form-group">
              <label>Apellido Materno</label>
              <input
                type="text"
                bind:value={formData.apellido_materno}
                disabled={cargando || eliminando}
                placeholder="Ej: Apellido"
              />
            </div>
          </div>
        </section>

        <!-- CONTACTO -->
        <section>
          <div class="section-header">
            <div class="section-title">
              <span class="section-icon">
                <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                  <path
                    d="M4 4h16v16H4Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  />
                  <path
                    d="M4 8 12 13 20 8"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </span>
              <div>
                <h2>Información de Contacto</h2>
                <p>Datos de comunicación del profesor.</p>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class:error={formErrors.correo}>
                Correo Electrónico <span class="required">*</span>
              </label>
              <input
                type="email"
                bind:value={formData.correo}
                disabled={cargando || eliminando}
                class:error={formErrors.correo}
                placeholder="Ej: ejemplo@colegio.edu"
              />
            </div>
            <div class="form-group">
              <label>Teléfono / Celular</label>
              <input
                type="tel"
                bind:value={formData.telefono}
                disabled={cargando || eliminando}
                placeholder="Ej: 77712345"
              />
            </div>
          </div>

          <div class="form-row full-row">
            <div class="form-group full-width">
              <label>Dirección</label>
              <input
                type="text"
                bind:value={formData.direccion}
                disabled={cargando || eliminando}
                placeholder="Ej: Dirección completa"
              />
            </div>
          </div>
        </section>

        <!-- ACADÉMICO / CARGO -->
        <section>
          <div class="section-header">
            <div class="section-title">
              <span class="section-icon">
                <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                  <path
                    d="M3 7 12 3l9 4-9 4Z"
                    fill="currentColor"
                  />
                  <path
                    d="M7 11v5a5 5 0 0 0 10 0v-5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                  />
                </svg>
              </span>
              <div>
                <h2>Información Académica</h2>
                <p>Perfil académico y cargo institucional.</p>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class:error={formErrors.especialidad}>
                Especialidad <span class="required">*</span>
              </label>
              <input
                type="text"
                bind:value={formData.especialidad}
                disabled={cargando || eliminando}
                class:error={formErrors.especialidad}
                placeholder="Ej: Matemáticas"
              />
            </div>
            <div class="form-group">
              <label class:error={formErrors.titulo_academico}>
                Título Académico <span class="required">*</span>
              </label>
              <input
                type="text"
                bind:value={formData.titulo_academico}
                disabled={cargando || eliminando}
                class:error={formErrors.titulo_academico}
                placeholder="Ej: Licenciatura en Educación"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Nivel de Enseñanza</label>
              <select
                bind:value={formData.nivel_enseñanza}
                disabled={cargando || eliminando}
              >
                <option value="todos">Todos los niveles</option>
                <option value="inicial">Educación Inicial</option>
                <option value="primaria">Educación Primaria</option>
                <option value="secundaria">Educación Secundaria</option>
              </select>
            </div>
            <div class="form-group">
              <label>Cargo</label>
              <select
                bind:value={formData.id_cargo}
                disabled={cargando || eliminando}
              >
                <option value={null}>Seleccione un cargo</option>
                {#each cargos as cargo}
                  <option value={cargo.id_cargo}>{cargo.nombre_cargo}</option>
                {/each}
              </select>
            </div>
          </div>

          <div class="form-row full-row">
            <div class="form-group full-width">
              <label>Observaciones</label>
              <textarea
                bind:value={formData.observaciones_profesor}
                disabled={cargando || eliminando}
                rows="3"
                placeholder="Observaciones adicionales..."
              ></textarea>
            </div>
          </div>
        </section>

        <!-- ASIGNACIONES EXISTENTES -->
        <section>
          <div class="section-header">
            <div class="section-title">
              <span class="section-icon">
                <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                  <path
                    d="M4 4h16v16H4Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  />
                  <path
                    d="M7 8h10M7 12h7M7 16h5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                  />
                </svg>
              </span>
              <div>
                <h2>Materias y Cursos Asignados</h2>
                <p>
                  Asignaciones actuales del profesor. Puede marcarlas para
                  eliminación.
                </p>
              </div>
            </div>
          </div>

          {#if asignacionesGuardadas.length === 0}
            <div class="no-asignaciones">
              <p>
                <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                  <path
                    d="M6 2h9l5 5v15H6Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  />
                  <path
                    d="M15 2v5h5"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  />
                  <path
                    d="M9 11h6M9 15h4"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                  />
                </svg>
                <span>Este profesor no tiene asignaciones actualmente.</span>
              </p>
            </div>
          {:else}
            <div class="asignaciones-lista">
              {#each asignacionesGuardadas as asignacion, index}
                <div class="asignacion-item">
                  <div class="asignacion-info">
                    <span class="materia-nombre"
                      >{asignacion.nombre_materia}</span
                    >
                    <span class="separator">—</span>
                    <span class="curso-nombre">{asignacion.nombre_curso}</span>
                  </div>
                  <button
                    class="btn-eliminar-asignacion"
                    on:click={() =>
                      onMarcarEliminar({ detail: { index, asignacion } })}
                    disabled={cargando || eliminando}
                    title="Eliminar asignación"
                    aria-label="Eliminar asignación"
                  >
                    <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                      <path
                        d="M3 6h18"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                      />
                      <path
                        d="M10 4h4a1 1 0 0 1 1 1v1H9V5a1 1 0 0 1 1-1Z"
                        fill="currentColor"
                      />
                      <rect
                        x="6"
                        y="7"
                        width="12"
                        height="13"
                        rx="1"
                        stroke="currentColor"
                        stroke-width="1.5"
                        fill="none"
                      />
                      <path
                        d="M10 11v6M14 11v6"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                      />
                    </svg>
                  </button>
                </div>
              {/each}
            </div>
          {/if}
        </section>

        <!-- ASIGNACIONES MARCADAS PARA ELIMINAR -->
        {#if asignacionesParaEliminar.length > 0}
          <section class="asignaciones-eliminar">
            <div class="section-header">
              <div class="section-title">
                <span class="section-icon">
                  <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                    <path
                      d="M4 4h16v16H4Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />
                    <path
                      d="M8 8 16 16M16 8 8 16"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                    />
                  </svg>
                </span>
                <div>
                  <h2>Asignaciones Marcadas para Eliminar</h2>
                  <p>Se eliminarán definitivamente al guardar los cambios.</p>
                </div>
              </div>
            </div>

            <div class="asignaciones-lista eliminar">
              {#each asignacionesParaEliminar as asignacion, index}
                <div class="asignacion-item eliminada">
                  <div class="asignacion-info">
                    <span class="materia-nombre"
                      >{asignacion.nombre_materia}</span
                    >
                    <span class="separator">—</span>
                    <span class="curso-nombre">{asignacion.nombre_curso}</span>
                  </div>
                  <button
                    class="btn-restaurar-asignacion"
                    on:click={() => onRestaurarAsignacion({ detail: { index } })}
                    disabled={cargando || eliminando}
                    title="Restaurar asignación"
                    aria-label="Restaurar asignación"
                  >
                    <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                      <path
                        d="M7 7v4H3"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                      <path
                        d="M5 11a7 7 0 1 0 2-5"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                  </button>
                </div>
              {/each}
            </div>
          </section>
        {/if}

        <!-- NUEVAS ASIGNACIONES -->
        <section>
          <div class="section-header">
            <div class="section-title">
              <span class="section-icon">
                <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                  <path
                    d="M5 5h14v14H5Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                  />
                  <path
                    d="M12 7v10M7 12h10"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                  />
                </svg>
              </span>
              <div>
                <h2>Asignar Nuevas Materias y Cursos</h2>
                <p>
                  Seleccione materia y curso para generar nuevas asignaciones.
                </p>
              </div>
            </div>
          </div>

          <div class="selectores-container">
            <div class="selector-group">
              <label>Materia</label>
              <div class="selector-input" on:click={abrirModalMaterias}>
                {#if materiaSeleccionada}
                  <span class="seleccionado"
                    >{materiaSeleccionada.nombre_materia}</span
                  >
                {:else}
                  <span class="placeholder">Seleccione una materia</span>
                {/if}
                <span class="dropdown-arrow">▾</span>
              </div>
            </div>

            <div class="selector-group">
              <label>Curso</label>
              <div
                class="selector-input {!materiaSeleccionada ? 'disabled' : ''}"
                on:click={abrirModalCursos}
              >
                {#if cursoSeleccionado}
                  <span class="seleccionado"
                    >{cursoSeleccionado.nombre_curso}</span
                  >
                {:else}
                  <span class="placeholder">Seleccione un curso</span>
                {/if}
                <span class="dropdown-arrow">▾</span>
              </div>
            </div>
          </div>

          {#if asignacionesPendientes.length > 0}
            <div class="asignaciones-pendientes-lista">
              <h3>Asignaciones Pendientes ({asignacionesPendientes.length})</h3>
              {#each asignacionesPendientes as asignacion, index}
                <div class="asignacion-item pendiente">
                  <div class="asignacion-info">
                    <span class="materia-nombre"
                      >{asignacion.nombre_materia}</span
                    >
                    <span class="separator">—</span>
                    <span class="curso-nombre">{asignacion.nombre_curso}</span>
                  </div>
                  <button
                    class="btn-eliminar-pendiente"
                    on:click={() => eliminarAsignacionPendiente(index)}
                    disabled={cargando || eliminando}
                    title="Eliminar asignación pendiente"
                    aria-label="Eliminar asignación pendiente"
                  >
                    ×
                  </button>
                </div>
              {/each}
            </div>
          {:else}
            <div class="sin-asignaciones-pendientes">
              No hay asignaciones pendientes
            </div>
          {/if}
        </section>

        <!-- CARGA HORARIA -->
        <section class="carga-horaria-section">
          <div class="carga-horaria-header">
            <div class="section-header no-margin">
              <div class="section-title">
                <span class="section-icon">
                  <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                    <rect
                      x="3"
                      y="4"
                      width="18"
                      height="17"
                      rx="2"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />
                    <path
                      d="M8 2v4M16 2v4M3 9h18"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                    />
                  </svg>
                </span>
                <div>
                  <h2>Gestión de Carga Horaria</h2>
                  <p>
                    Configure los horarios de las materias y cursos asignados al
                    profesor.
                  </p>
                </div>
              </div>
            </div>

            <button
              class="btn-carga-horaria"
              on:click={abrirModalCarga}
              disabled={!formData.id_profesor || cargando || eliminando}
            >
              <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                <rect
                  x="3"
                  y="4"
                  width="18"
                  height="17"
                  rx="2"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                />
                <path
                  d="M8 2v4M16 2v4M3 9h18"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                />
                <rect
                  x="7"
                  y="11"
                  width="4"
                  height="4"
                  rx="0.5"
                  fill="currentColor"
                />
              </svg>
              <span>Asignar Carga Horaria</span>
            </button>
          </div>

          {#if !formData.id_profesor}
            <div class="advertencia-carga">
              <p>
                <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                  <path
                    d="M1 21h22L12 2 1 21Zm12-3h-2v-2h2Zm0-4h-2v-4h2Z"
                    fill="currentColor"
                  />
                </svg>
                <span>
                  Guarde primero los datos del profesor para poder asignar la
                  carga horaria.
                </span>
              </p>
            </div>
          {/if}
        </section>

        <!-- RESUMEN DE CAMBIOS -->
        {#if asignacionesPendientes.length > 0 || asignacionesParaEliminar.length > 0}
          <section class="resumen-cambios">
            <div class="section-header">
              <div class="section-title">
                <span class="section-icon">
                  <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                    <path
                      d="M4 4h16v16H4Z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                    />
                    <path
                      d="M8 9h8M8 13h6"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.5"
                      stroke-linecap="round"
                    />
                  </svg>
                </span>
                <div>
                  <h2>Resumen de Cambios</h2>
                  <p>Revise las asignaciones nuevas y las que se eliminarán.</p>
                </div>
              </div>
            </div>

            <div class="cambios-lista">
              {#if asignacionesPendientes.length > 0}
                <div class="cambio-grupo">
                  <h3>Nuevas Asignaciones</h3>
                  {#each asignacionesPendientes as asignacion}
                    <div class="cambio-item nueva">
                      <span class="cambio-icon">
                        <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                          <path
                            d="M12 5v14M5 12h14"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.5"
                            stroke-linecap="round"
                          />
                        </svg>
                      </span>
                      <span class="cambio-text">
                        {asignacion.nombre_materia} — {asignacion.nombre_curso}
                      </span>
                    </div>
                  {/each}
                </div>
              {/if}

              {#if asignacionesParaEliminar.length > 0}
                <div class="cambio-grupo">
                  <h3>Asignaciones a Eliminar</h3>
                  {#each asignacionesParaEliminar as asignacion}
                    <div class="cambio-item eliminar">
                      <span class="cambio-icon">
                        <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                          <path
                            d="M5 12h14"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.5"
                            stroke-linecap="round"
                          />
                        </svg>
                      </span>
                      <span class="cambio-text">
                        {asignacion.nombre_materia} — {asignacion.nombre_curso}
                      </span>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          </section>
        {/if}
      </div>
    </div>
  </div>
</div>

<!-- MODALES -->
<AsignarMaterias
  mostrar={mostrarModalMaterias}
  {materiaSeleccionada}
  on:materiaSeleccionada={onMateriaSeleccionada}
  on:cerrar={() => (mostrarModalMaterias = false)}
/>

<AsignarCursos
  mostrar={mostrarModalCursos}
  {cursoSeleccionado}
  on:cursoSeleccionado={onCursoSeleccionado}
  on:cerrar={() => (mostrarModalCursos = false)}
/>

<AsignarCarga
  mostrar={mostrarModalCarga}
  profesor={formData}
  asignaciones={asignacionesGuardadas.concat(asignacionesPendientes)}
  autoSave={false}
  on:guardarTemporal={onGuardarCargaTemporal}
  on:cerrar={() => (mostrarModalCarga = false)}
/>

<style>
  :root {
    --primary: #02c7c9;
    --primary-hover: #00afb2;
    --danger: #ef5350;
    --danger-hover: #e53935;
    --surface: #ffffff;
    --surface-alt: #f9fafb;
    --border-subtle: #e5e7eb;
    --text-main: #111827;
    --text-muted: #6b7280;
  }

  .editar-profesor-page {
    min-height: 100vh;
    background: #f3f4f6;
    padding: 24px;
    box-sizing: border-box;
  }

  .editar-profesor-container {
    max-width: 1120px;
    margin: 0 auto;
  }

  .editar-profesor {
    background: var(--surface);
    border-radius: 16px;
    padding: 22px 26px 30px;
    box-shadow: 0 14px 40px rgba(15, 23, 42, 0.08);
    border: 1px solid #e5e7eb;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    padding-bottom: 18px;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 20px;
  }

  .header-left {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .title-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .title-icon {
    width: 32px;
    height: 32px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #ecfeff;
    color: #0891b2;
  }

  .header-left h1 {
    margin: 0;
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--text-main);
    letter-spacing: 0.01em;
  }

  .profesor-id {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 2px 10px;
    border-radius: 999px;
    background: #e0f2fe;
    color: #1d4ed8;
    font-size: 0.78rem;
    border: 1px solid #bfdbfe;
  }

  .profesor-id-value {
    font-weight: 600;
  }

  .actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .btn-outline,
  .btn-primary,
  .btn-delete {
    padding: 9px 18px;
    border-radius: 999px;
    font-size: 0.9rem;
    cursor: pointer;
    border: none;
    font-weight: 500;
    transition: all 0.18s ease-out;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
      sans-serif;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    line-height: 1;
    white-space: nowrap;
  }

  .btn-outline {
    background: var(--surface);
    color: var(--text-muted);
    border: 1px solid #d4d4d8;
  }

  .btn-outline:hover:not(:disabled) {
    background: #f4f4f5;
    border-color: #c4c4cf;
    transform: translateY(-0.5px);
  }

  .btn-primary {
    background: var(--primary);
    color: #ffffff;
    box-shadow: 0 10px 24px rgba(34, 211, 238, 0.25);
  }

  .btn-primary:hover:not(:disabled) {
    background: var(--primary-hover);
    box-shadow: 0 12px 26px rgba(34, 211, 238, 0.32);
    transform: translateY(-1px);
  }

  .btn-primary:disabled {
    background: #cbd5e1;
    color: #f8fafc;
    box-shadow: none;
    cursor: not-allowed;
  }

  .btn-delete {
    background: var(--danger);
    color: #ffffff;
    box-shadow: 0 10px 22px rgba(239, 83, 80, 0.25);
  }

  .btn-delete:hover:not(:disabled) {
    background: var(--danger-hover);
    box-shadow: 0 12px 26px rgba(239, 83, 80, 0.32);
    transform: translateY(-1px);
  }

  .btn-outline:disabled,
  .btn-delete:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
  }

  .icon {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  .alert {
    padding: 11px 15px;
    border-radius: 12px;
    margin-bottom: 14px;
    font-size: 0.9rem;
    border: 1px solid;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
      sans-serif;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .alert-icon .icon {
    width: 18px;
    height: 18px;
  }

  .alert-success {
    background: #ecfdf3;
    color: #166534;
    border-color: #bbf7d0;
  }

  .alert-error {
    background: #fef2f2;
    color: #b91c1c;
    border-color: #fecaca;
  }

  .alert-warning {
    background: #fffbeb;
    color: #92400e;
    border-color: #fcd34d;
  }

  .alert-info {
    background: #eff6ff;
    color: #1d4ed8;
    border-color: #bfdbfe;
  }

  .form-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  section {
    background: var(--surface-alt);
    padding: 18px 18px 16px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
  }

  .asignaciones-eliminar {
    background: #fef2f2;
    border-color: #fecaca;
  }

  .resumen-cambios {
    background: #fff7ed;
    border-color: #fed7aa;
  }

  .carga-horaria-section {
    background: #f0f9ff;
    border-color: #bae6fd;
  }

  .section-header {
    margin-bottom: 14px;
  }

  .section-header.no-margin {
    margin-bottom: 0;
  }

  .section-title {
    display: flex;
    align-items: flex-start;
    gap: 8px;
  }

  .section-icon {
    width: 28px;
    height: 28px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #e0f2fe;
    color: #0369a1;
    margin-top: 2px;
  }

  .section-header h2 {
    margin: 0;
    font-size: 0.98rem;
    font-weight: 600;
    color: #111827;
  }

  .section-header p {
    margin: 3px 0 0;
    color: var(--text-muted);
    font-size: 0.84rem;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 12px;
  }

  .form-row.full-row {
    grid-template-columns: 1fr;
  }

  .form-row:last-child {
    margin-bottom: 0;
  }

  .form-group {
    display: flex;
    flex-direction: column;
  }

  .full-width {
    grid-column: 1 / -1;
  }

  label {
    margin-bottom: 5px;
    font-size: 0.84rem;
    color: #4b5563;
    font-weight: 500;
  }

  .required {
    color: #ef4444;
    margin-left: 2px;
  }

  .error {
    color: #dc2626;
  }

  input,
  select,
  textarea {
    padding: 8px 11px;
    border: 1.5px solid #e5e7eb;
    border-radius: 9px;
    font-size: 0.9rem;
    background: #ffffff;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
      sans-serif;
    color: #111827;
    transition: border-color 0.18s ease, box-shadow 0.18s ease,
      background-color 0.18s ease;
  }

  input:focus,
  select:focus,
  textarea:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.18);
    background: #f9feff;
  }

  input.error,
  select.error,
  textarea.error {
    border-color: #dc2626;
  }

  textarea {
    resize: vertical;
    min-height: 70px;
  }

  .selectores-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 16px;
  }

  .selector-group {
    display: flex;
    flex-direction: column;
  }

  .selector-input {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 11px;
    border: 1px solid #e5e7eb;
    border-radius: 9px;
    background: #ffffff;
    cursor: pointer;
    transition: border-color 0.18s ease, box-shadow 0.18s ease,
      background-color 0.18s ease;
    min-height: 38px;
  }

  .selector-input:hover {
    border-color: var(--primary);
    box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.12);
  }

  .selector-input.disabled {
    background: #f3f4f6;
    cursor: not-allowed;
    color: #9ca3af;
    box-shadow: none;
  }

  .selector-input.disabled:hover {
    border-color: #e5e7eb;
  }

  .seleccionado {
    font-weight: 500;
    color: #111827;
  }

  .placeholder {
    color: #9ca3af;
  }

  .dropdown-arrow {
    color: #6b7280;
    font-size: 0.78rem;
  }

  .no-asignaciones {
    text-align: center;
    padding: 18px;
    color: #64748b;
    border-radius: 12px;
    background: #f9fafb;
    border: 1px dashed #e5e7eb;
  }

  .no-asignaciones p {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin: 0;
  }

  .asignaciones-lista,
  .asignaciones-pendientes-lista {
    display: flex;
    flex-direction: column;
    gap: 7px;
  }

  .asignacion-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 13px;
    background: #ffffff;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    transition: all 0.18s ease;
  }

  .asignacion-item:hover {
    border-color: #cbd5e1;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
  }

  .asignacion-item.eliminada {
    background: #fef2f2;
    border-color: #fecaca;
    color: #b91c1c;
  }

  .asignacion-item.pendiente {
    background: #f0fdf4;
    border-color: #bbf7d0;
  }

  .asignacion-info {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .materia-nombre {
    font-weight: 500;
    color: #111827;
  }

  .separator {
    color: #9ca3af;
  }

  .curso-nombre {
    color: #4b5563;
  }

  .btn-eliminar-asignacion,
  .btn-restaurar-asignacion,
  .btn-eliminar-pendiente {
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px;
    border-radius: 999px;
    transition: background-color 0.18s ease, transform 0.18s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .btn-eliminar-asignacion:hover:not(:disabled) {
    background: #fee2e2;
    transform: translateY(-0.5px);
  }

  .btn-restaurar-asignacion:hover:not(:disabled) {
    background: #dcfce7;
    transform: translateY(-0.5px);
  }

  .btn-eliminar-pendiente {
    background: var(--danger);
    color: #ffffff;
    width: 26px;
    height: 26px;
    border-radius: 999px;
    font-size: 16px;
    line-height: 1;
  }

  .btn-eliminar-pendiente:hover:not(:disabled) {
    background: var(--danger-hover);
  }

  .btn-eliminar-asignacion:disabled,
  .btn-restaurar-asignacion:disabled,
  .btn-eliminar-pendiente:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .sin-asignaciones-pendientes {
    text-align: center;
    color: #9ca3af;
    font-style: italic;
    padding: 16px;
    background: #f9fafb;
    border: 1px dashed #e5e7eb;
    border-radius: 10px;
  }

  .carga-horaria-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 14px;
  }

  .btn-carga-horaria {
    background: #0ea5e9;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 999px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    white-space: nowrap;
    transition: background-color 0.18s ease, box-shadow 0.18s ease,
      transform 0.18s ease;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 9px 20px rgba(14, 165, 233, 0.22);
  }

  .btn-carga-horaria:hover:not(:disabled) {
    background: #0284c7;
    box-shadow: 0 11px 24px rgba(14, 165, 233, 0.3);
    transform: translateY(-1px);
  }

  .btn-carga-horaria:disabled {
    background: #cbd5e1;
    cursor: not-allowed;
    opacity: 0.7;
    box-shadow: none;
  }

  .advertencia-carga {
    background: #fffbeb;
    border: 1px solid #fcd34d;
    border-radius: 12px;
    padding: 9px 13px;
    margin-top: 12px;
  }

  .advertencia-carga p {
    margin: 0;
    color: #92400e;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .cambios-lista {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .cambio-grupo h3 {
    margin: 0 0 5px;
    font-size: 0.9rem;
    color: #374151;
    font-weight: 600;
  }

  .cambio-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 10px;
    background: #ffffff;
    border-radius: 10px;
    border-left: 4px solid;
  }

  .cambio-item.nueva {
    border-left-color: #10b981;
  }

  .cambio-item.eliminar {
    border-left-color: #ef4444;
  }

  .cambio-icon .icon {
    width: 16px;
    height: 16px;
  }

  .cambio-text {
    color: #111827;
    font-size: 0.88rem;
  }

  .spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-right: 6px;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  @media (max-width: 900px) {
    .editar-profesor-page {
      padding: 16px;
    }

    .editar-profesor {
      padding: 18px 16px 22px;
    }

    .header {
      flex-direction: column;
      align-items: flex-start;
    }

    .actions {
      width: 100%;
      justify-content: flex-end;
      flex-wrap: wrap;
    }

    .btn-outline,
    .btn-primary,
    .btn-delete {
      flex: 1;
      min-width: 120px;
      justify-content: center;
    }

    .form-row {
      grid-template-columns: 1fr;
    }

    .selectores-container {
      grid-template-columns: 1fr;
    }

    .carga-horaria-header {
      flex-direction: column;
      align-items: stretch;
    }

    .btn-carga-horaria {
      align-self: flex-start;
    }

    .asignacion-item {
      flex-direction: column;
      align-items: stretch;
      gap: 8px;
    }

    .asignacion-info {
      justify-content: flex-start;
    }
  }

  @media (max-width: 520px) {
    .editar-profesor-page {
      padding: 10px;
    }

    .actions {
      flex-direction: column;
      align-items: stretch;
    }

    .btn-outline,
    .btn-primary,
    .btn-delete {
      width: 100%;
    }
  }
</style>
