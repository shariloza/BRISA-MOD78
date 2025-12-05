<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import AsignarMaterias from "../Materias/AsignarMaterias.svelte";
  import AsignarCursos from "../Cursos/AsignarCursos.svelte";
  import AsignarCarga from "../Cargas/AsignarCarga.svelte";

  export let profesorInit: any = null;

  const API_URL = "http://localhost:8000/api/profesores";
  const dispatch = createEventDispatcher();

  type AlertType = "success" | "error" | "warning" | "info" | null;

  interface Profesor {
    id_persona?: number | null;
    id_profesor?: number | null;
    ci: string;
    nombres: string;
    apellido_paterno: string;
    apellido_materno?: string;
    direccion?: string;
    telefono?: string;
    correo: string;
    tipo_persona: string;
    estado_laboral: string;
    id_cargo: number | null;
    años_experiencia: number;
    fecha_ingreso: string;
    especialidad: string;
    titulo_academico: string;
    nivel_enseñanza: string;
    observaciones_profesor?: string;
  }

  interface FormErrors {
    ci: boolean;
    nombres: boolean;
    apellido_paterno: boolean;
    correo: boolean;
    especialidad: boolean;
    titulo_academico: boolean;
  }

  let profesor: Profesor = {
    ci: "",
    nombres: "",
    apellido_paterno: "",
    apellido_materno: "",
    direccion: "",
    telefono: "",
    correo: "",
    tipo_persona: "profesor",
    estado_laboral: "activo",
    id_cargo: null,
    años_experiencia: 0,
    fecha_ingreso: new Date().toISOString().split("T")[0],
    especialidad: "",
    titulo_academico: "",
    nivel_enseñanza: "todos",
    observaciones_profesor: "",
  };

  let formErrors: FormErrors = {
    ci: false,
    nombres: false,
    apellido_paterno: false,
    correo: false,
    especialidad: false,
    titulo_academico: false,
  };

  let profesorCreado: any = null;
  let asignacionesPendientes: any[] = [];
  let asignacionesGuardadas: any[] = [];
  let asignacionesParaEliminar: any[] = [];

  let isEditMode = false;
  let profesorId: number | null = null;
  let cargos: any[] = [];

  // Bloques pendientes (para integración con AsignarCarga)
  let bloquesPendientesCrear: any[] = [];
  let bloquesPendientesActualizar: any[] = [];
  let bloquesPendientesEliminar: any[] = [];
  let hayCambiosPendientes = false;

  // Alertas
  let alertType: AlertType = null;
  let alertMessage = "";
  let cargando = false;

  // Estados para los modales de selección
  let mostrarModalMaterias = false;
  let mostrarModalCursos = false;
  let mostrarModalCarga = false;
  let materiaSeleccionada: any = null;
  let cursoSeleccionado: any = null;

  async function cargarAuxiliares() {
    try {
      const res = await fetch(`${API_URL}/cargos`);
      if (res.ok) cargos = await res.json();
    } catch (err) {
      console.error(err);
    }
  }

  // Cargar datos iniciales si llega profesorInit
  $: if (profesorInit) {
    const id = profesorInit.id_persona || profesorInit.id_profesor;
    if (id && id !== profesorId) {
      isEditMode = true;
      profesorId = id;
      profesor = {
        ci: profesorInit.ci || "",
        nombres: profesorInit.nombres || "",
        apellido_paterno: profesorInit.apellido_paterno || "",
        apellido_materno: profesorInit.apellido_materno || "",
        direccion: profesorInit.direccion || "",
        telefono: profesorInit.telefono || "",
        correo: profesorInit.correo || "",
        tipo_persona: profesorInit.tipo_persona || "profesor",
        estado_laboral: profesorInit.estado_laboral || "activo",
        id_cargo: profesorInit.id_cargo ?? null,
        años_experiencia: profesorInit.años_experiencia || 0,
        fecha_ingreso:
          profesorInit.fecha_ingreso ||
          new Date().toISOString().split("T")[0],
        especialidad: profesorInit.especialidad || "",
        titulo_academico: profesorInit.titulo_academico || "",
        nivel_enseñanza: profesorInit.nivel_enseñanza || "todos",
        observaciones_profesor: profesorInit.observaciones_profesor || "",
      };
      profesorCreado = { ...profesorInit };
      hayCambiosPendientes = false;
    }
  }

  function resetForm() {
    profesor = {
      ci: "",
      nombres: "",
      apellido_paterno: "",
      apellido_materno: "",
      direccion: "",
      telefono: "",
      correo: "",
      tipo_persona: "profesor",
      estado_laboral: "activo",
      id_cargo: null,
      años_experiencia: 0,
      fecha_ingreso: new Date().toISOString().split("T")[0],
      especialidad: "",
      titulo_academico: "",
      nivel_enseñanza: "todos",
      observaciones_profesor: "",
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
    isEditMode = false;
    profesorId = null;
    profesorCreado = null;
    materiaSeleccionada = null;
    cursoSeleccionado = null;
    bloquesPendientesCrear = [];
    bloquesPendientesActualizar = [];
    bloquesPendientesEliminar = [];
    hayCambiosPendientes = false;
    alertType = "info";
    alertMessage = "Formulario reiniciado.";
  }

  function validar() {
    let ok = true;
    formErrors = {
      ci: false,
      nombres: false,
      apellido_paterno: false,
      correo: false,
      especialidad: false,
      titulo_academico: false,
    };

    if (!profesor.ci?.trim()) {
      formErrors.ci = true;
      ok = false;
    }
    if (!profesor.nombres?.trim()) {
      formErrors.nombres = true;
      ok = false;
    }
    if (!profesor.apellido_paterno?.trim()) {
      formErrors.apellido_paterno = true;
      ok = false;
    }
    if (!profesor.correo?.includes("@")) {
      formErrors.correo = true;
      ok = false;
    }
    if (!profesor.especialidad?.trim()) {
      formErrors.especialidad = true;
      ok = false;
    }
    if (!profesor.titulo_academico?.trim()) {
      formErrors.titulo_academico = true;
      ok = false;
    }

    return ok;
  }

  async function guardarTodo() {
    if (!validar()) {
      alertType = "warning";
      alertMessage = "Complete todos los campos requeridos marcados con (*).";
      return;
    }

    cargando = true;
    alertType = null;
    alertMessage = "";

    const data = {
      ...profesor,
      id_cargo: profesor.id_cargo ? Number(profesor.id_cargo) : null,
    };
    const method = isEditMode ? "PUT" : "POST";
    const url = isEditMode ? `${API_URL}/${profesorId}` : API_URL;

    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        let detail = "Error al guardar profesor";
        try {
          const errData = await res.json();
          if (errData?.detail) detail = errData.detail;
        } catch {
          // ignore parse error
        }
        throw new Error(detail);
      }

      profesorCreado = await res.json();
      const idProf = profesorCreado.id_profesor;

      // Guardar asignaciones pendientes
      if (asignacionesPendientes.length > 0) {
        await Promise.all(
          asignacionesPendientes.map((a) =>
            fetch(`${API_URL}/asignaciones`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                id_profesor: idProf,
                id_materia: a.id_materia,
                id_curso: a.id_curso,
              }),
            }),
          ),
        );
      }

      // Eliminar bloques
      if (bloquesPendientesEliminar.length > 0) {
        for (const b of bloquesPendientesEliminar) {
          if (b.id_bloque) {
            await fetch(`${API_URL}/bloques/${b.id_bloque}`, {
              method: "DELETE",
            });
          }
        }
      }

      // Actualizar bloques
      if (bloquesPendientesActualizar.length > 0) {
        for (const b of bloquesPendientesActualizar) {
          const body = {
            id_profesor: idProf,
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
            gestion: b.gestion || "2025",
            observaciones: b.observaciones || null,
          };
          if (b.id_bloque) {
            await fetch(`${API_URL}/bloques/${b.id_bloque}`, {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(body),
            });
          }
        }
      }

      // Crear bloques nuevos
      if (bloquesPendientesCrear.length > 0) {
        for (const b of bloquesPendientesCrear) {
          const body = {
            id_profesor: idProf,
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
            gestion: b.gestion || "2025",
            observaciones: b.observaciones || null,
          };
          await fetch(`${API_URL}/bloques`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          });
        }
      }

      bloquesPendientesCrear = [];
      bloquesPendientesActualizar = [];
      bloquesPendientesEliminar = [];
      hayCambiosPendientes = false;

      alertType = "success";
      alertMessage = `Profesor ${isEditMode ? "actualizado" : "creado"} correctamente.`;

      dispatch("save", {
        ...profesorCreado,
        asignaciones: asignacionesPendientes,
      });

      // Para alta: limpiamos; para edición, mantenemos valores
      if (!isEditMode) {
        resetForm();
      }
    } catch (err: any) {
      alertType = "error";
      alertMessage = `Error: ${err?.message || "No se pudo completar la operación"}`;
    } finally {
      cargando = false;
    }
  }

  // Abrir modal de materias
  function abrirModalMaterias() {
    mostrarModalMaterias = true;
  }

  // Abrir modal de cursos
  function abrirModalCursos() {
    if (!materiaSeleccionada) {
      alertType = "warning";
      alertMessage = "Primero seleccione una materia.";
      return;
    }
    mostrarModalCursos = true;
  }

  // Abrir modal de carga horaria
  function abrirModalCarga() {
    const totalAsignaciones =
      asignacionesGuardadas.length + asignacionesPendientes.length;

    if (!profesorCreado && totalAsignaciones === 0) {
      alertType = "info";
      alertMessage =
        "Asigne al menos una materia y curso antes de gestionar la carga horaria.";
      return;
    }
    mostrarModalCarga = true;
  }

  // Cuando se selecciona una materia
  function onMateriaSeleccionada(event: CustomEvent) {
    materiaSeleccionada = event.detail.materia;
    mostrarModalMaterias = false;
    cursoSeleccionado = null;
  }

  // Cuando se selecciona un curso
  function onCursoSeleccionado(event: CustomEvent) {
    cursoSeleccionado = event.detail.curso;
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
        materiaSeleccionada = null;
        cursoSeleccionado = null;
        hayCambiosPendientes = true;
      } else {
        alertType = "warning";
        alertMessage = "Esta combinación de materia y curso ya está registrada.";
      }
    }
  }

  // Cambios temporales del modal AsignarCarga
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
    alertType = "success";
    alertMessage =
      "Cambios de carga horaria preparados. Se guardarán al guardar el profesor.";
  }

  function eliminarAsignacion(index: number) {
    asignacionesPendientes = asignacionesPendientes.filter(
      (_, i) => i !== index,
    );
    hayCambiosPendientes =
      asignacionesPendientes.length > 0 ||
      bloquesPendientesCrear.length > 0 ||
      bloquesPendientesActualizar.length > 0 ||
      bloquesPendientesEliminar.length > 0;
  }

  function cancelar() {
    if (hayCambiosPendientes) {
      const confirmar = confirm(
        "Tiene cambios sin guardar. ¿Desea salir de todas formas?",
      );
      if (!confirmar) return;
    }
    dispatch("cancel");
  }

  function onInputChange() {
    hayCambiosPendientes = true;
  }

  onMount(cargarAuxiliares);
</script>

<div class="profesor-page">
  <div class="profesor-container">
    <div class="profesor-card">
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
            <div>
              <h1>{isEditMode ? "Editar Profesor" : "Nuevo Profesor"}</h1>
              <p class="subtitle">
                Registro y gestión del perfil docente para el sistema académico.
              </p>
            </div>
          </div>
          {#if profesorId}
            <span class="profesor-id">
              <span>ID</span>
              <span class="profesor-id-value">{profesorId}</span>
            </span>
          {/if}
        </div>

        <div class="actions">
          <button
            class="btn-outline"
            type="button"
            on:click={cancelar}
            disabled={cargando}
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
            type="button"
            on:click={guardarTodo}
            disabled={cargando}
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
              <span>{isEditMode ? "Actualizar" : "Guardar"}</span>
            {/if}
          </button>
        </div>
      </div>

      <!-- ALERTAS -->
      {#if alertMessage}
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
          <span>{alertMessage}</span>
        </div>
      {/if}

      {#if hayCambiosPendientes}
        <div class="alert alert-warning subtle">
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

      <!-- FORMULARIO -->
      <div class="form-content" on:input={onInputChange}>
        <!-- Información Personal -->
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
                <p>Datos de identificación y estado laboral del docente.</p>
              </div>
            </div>
          </div>

          <div class="form-row single">
            <div class="form-group">
              <label class:error={formErrors.ci}>
                Cédula de Identidad <span class="required">*</span>
              </label>
              <input
                type="text"
                bind:value={profesor.ci}
                disabled={isEditMode}
                class:error={formErrors.ci}
                placeholder="Ej: 1234567"
              />
            </div>
            <div class="form-group">
              <label>Estado Laboral</label>
              <select bind:value={profesor.estado_laboral}>
                <option value="activo">Activo</option>
                <option value="inactivo">Inactivo</option>
                <option value="licencia">Licencia</option>
                <option value="jubilado">Jubilado</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group full-width">
              <label class:error={formErrors.nombres}>
                Nombres Completos <span class="required">*</span>
              </label>
              <input
                type="text"
                bind:value={profesor.nombres}
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
                bind:value={profesor.apellido_paterno}
                class:error={formErrors.apellido_paterno}
                placeholder="Ej: Apellido"
              />
            </div>
            <div class="form-group">
              <label>Apellido Materno</label>
              <input
                type="text"
                bind:value={profesor.apellido_materno}
                placeholder="Ej: Apellido"
              />
            </div>
          </div>
        </section>

        <!-- Contacto -->
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
                <p>Datos de comunicación y ubicación del docente.</p>
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
                bind:value={profesor.correo}
                class:error={formErrors.correo}
                placeholder="Ej: ejemplo@colegio.edu"
              />
            </div>
            <div class="form-group">
              <label>Teléfono / Celular</label>
              <input
                type="tel"
                bind:value={profesor.telefono}
                placeholder="Ej: 77712345"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group full-width">
              <label>Dirección</label>
              <input
                type="text"
                bind:value={profesor.direccion}
                placeholder="Ej: Dirección completa"
              />
            </div>
          </div>
        </section>

        <!-- Datos Académicos -->
        <section>
          <div class="section-header">
            <div class="section-title">
              <span class="section-icon">
                <svg viewBox="0 0 24 24" class="icon" aria-hidden="true">
                  <path d="M3 7 12 3l9 4-9 4Z" fill="currentColor" />
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
                <h2>Datos Académicos</h2>
                <p>Perfil profesional y nivel de enseñanza que imparte.</p>
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
                bind:value={profesor.especialidad}
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
                bind:value={profesor.titulo_academico}
                class:error={formErrors.titulo_academico}
                placeholder="Ej: Licenciatura en Educación"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Nivel de Enseñanza</label>
              <select bind:value={profesor.nivel_enseñanza}>
                <option value="todos">Todos los niveles</option>
                <option value="inicial">Educación Inicial</option>
                <option value="primaria">Educación Primaria</option>
                <option value="secundaria">Educación Secundaria</option>
              </select>
            </div>
            <div class="form-group">
              <label>Años de Experiencia</label>
              <input
                type="number"
                bind:value={profesor.años_experiencia}
                min="0"
                placeholder="Ej: 5"
              />
            </div>
          </div>
        </section>

        <!-- Datos Laborales -->
        <section>
          <div class="section-header">
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
                <h2>Datos Laborales</h2>
                <p>Cargo institucional y observaciones internas.</p>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Cargo</label>
              <select bind:value={profesor.id_cargo}>
                <option value={null}>Sin cargo asignado</option>
                {#each cargos as c}
                  <option value={c.id_cargo}>{c.nombre_cargo}</option>
                {/each}
              </select>
            </div>
            <div class="form-group">
              <label>Fecha de Ingreso</label>
              <input type="date" bind:value={profesor.fecha_ingreso} />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group full-width">
              <label>Observaciones</label>
              <textarea
                rows="3"
                bind:value={profesor.observaciones_profesor}
                placeholder="Notas internas sobre el desempeño o acuerdos específicos."
              ></textarea>
            </div>
          </div>
        </section>

        <!-- ASIGNACIÓN DE MATERIAS Y CURSOS -->
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
                <h2>Asignación de Materias y Cursos</h2>
                <p>Defina la carga académica del docente por materia y curso.</p>
              </div>
            </div>
          </div>

        <!-- Selectores tipo dropdown -->
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

          <div class="carga-horaria-row">
            <button
              class="btn-carga-horaria"
              type="button"
              on:click={abrirModalCarga}
              disabled={!profesorCreado &&
                asignacionesGuardadas.concat(asignacionesPendientes).length === 0}
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
            {#if !profesorCreado}
              <small class="carga-horaria-hint">
                Disponible después de crear el profesor o si ya agregó al menos
                una materia y curso.
              </small>
            {/if}
          </div>

          <!-- Lista de asignaciones pendientes -->
          {#if asignacionesPendientes.length > 0}
            <div class="asignaciones-lista">
              <h3>Asignaciones Pendientes ({asignacionesPendientes.length})</h3>
              {#each asignacionesPendientes as asignacion, index}
                <div class="asignacion-item">
                  <div class="asignacion-info">
                    <span class="materia">{asignacion.nombre_materia}</span>
                    <span class="separador">—</span>
                    <span class="curso">{asignacion.nombre_curso}</span>
                  </div>
                  <button
                    class="btn-eliminar-asignacion"
                    type="button"
                    on:click={() => eliminarAsignacion(index)}
                  >
                    ×
                  </button>
                </div>
              {/each}
            </div>
          {:else}
            <div class="sin-asignaciones">
              No hay asignaciones pendientes de registrar.
            </div>
          {/if}
        </section>
      </div>
    </div>
  </div>
</div>

<!-- Modales de selección -->
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
  profesor={profesorCreado || profesor}
  asignaciones={asignacionesGuardadas.concat(asignacionesPendientes)}
  autoSave={false}
  on:guardarTemporal={onGuardarCargaTemporal}
  on:cerrar={() => (mostrarModalCarga = false)}
/>

<style>
  :root {
    --primary: #02c7c9;
    --primary-hover: #00afb2;
    --surface: #ffffff;
    --surface-alt: #f9fafb;
    --border-subtle: #e5e7eb;
    --text-main: #111827;
    --text-muted: #6b7280;
    --danger: #ef4444;
    --danger-hover: #dc2626;
  }

  .profesor-page {
    min-height: 100vh;
    background: #f3f4f6;
    padding: 24px;
    box-sizing: border-box;
  }

  .profesor-container {
    max-width: 1120px;
    margin: 0 auto;
  }

  .profesor-card {
    background: var(--surface);
    border-radius: 14px;
    padding: 22px 26px 30px;
    box-shadow: 0 14px 40px rgba(15, 23, 42, 0.07);
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
    gap: 6px;
  }

  .title-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .title-icon {
    width: 34px;
    height: 34px;
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

  .subtitle {
    margin: 0;
    font-size: 0.86rem;
    color: var(--text-muted);
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
  .btn-primary {
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

  .btn-primary:disabled,
  .btn-outline:disabled {
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

  .alert.subtle {
    margin-top: -4px;
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

  .section-header {
    margin-bottom: 14px;
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
    gap: 14px;
    margin-bottom: 12px;
  }

  .form-row.single {
    grid-template-columns: 1fr 1fr;
  }

  .full-width {
    grid-column: 1 / -1;
  }

  .form-group {
    display: flex;
    flex-direction: column;
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

  /* Selectores de materias y cursos */
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

  .carga-horaria-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
  }

  .btn-carga-horaria {
    background: #0ea5e9;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 999px;
    cursor: pointer;
    font-size: 0.88rem;
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
    opacity: 0.8;
    box-shadow: none;
  }

  .carga-horaria-hint {
    color: #64748b;
    font-size: 0.8rem;
  }

  /* Asignaciones */
  .asignaciones-lista {
    display: flex;
    flex-direction: column;
    gap: 7px;
  }

  .asignaciones-lista h3 {
    margin: 0 0 6px;
    font-size: 0.9rem;
    color: #374151;
    font-weight: 600;
  }

  .asignacion-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
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

  .asignacion-info {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .materia {
    font-weight: 500;
    color: #111827;
  }

  .separador {
    color: #9ca3af;
  }

  .curso {
    color: #4b5563;
  }

  .btn-eliminar-asignacion {
    background: var(--danger);
    color: #ffffff;
    border: none;
    width: 26px;
    height: 26px;
    border-radius: 999px;
    cursor: pointer;
    font-size: 16px;
    line-height: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.18s ease, transform 0.18s ease;
  }

  .btn-eliminar-asignacion:hover:not(:disabled) {
    background: var(--danger-hover);
    transform: translateY(-0.5px);
  }

  .sin-asignaciones {
    text-align: center;
    color: #9ca3af;
    font-style: italic;
    padding: 16px;
    background: #f9fafb;
    border: 1px dashed #e5e7eb;
    border-radius: 10px;
  }

  /* Responsive */
  @media (max-width: 900px) {
    .profesor-page {
      padding: 16px;
    }

    .profesor-card {
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
    .btn-primary {
      flex: 1;
      min-width: 120px;
      justify-content: center;
    }

    .form-row.single {
      grid-template-columns: 1fr;
    }

    .selectores-container {
      grid-template-columns: 1fr;
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
    .profesor-page {
      padding: 10px;
    }

    .actions {
      flex-direction: column;
      align-items: stretch;
    }

    .btn-outline,
    .btn-primary {
      width: 100%;
    }

    .carga-horaria-row {
      flex-direction: column;
      align-items: flex-start;
    }
  }
</style>
