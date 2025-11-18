<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import AsignarMaterias from "./AsignarMaterias.svelte";
  import AsignarCursos from "./AsignarCursos.svelte";
  import AsignarCarga from "./AsignarCarga.svelte";

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

  // === ESTADOS ===
  let formData = {
    ci: "", nombres: "", apellido_paterno: "", apellido_materno: "", 
    direccion: "", telefono: "", correo: "",
    tipo_persona: "profesor", estado_laboral: "activo",
    id_persona: null as number | null, id_profesor: null as number | null,
    especialidad: "", titulo_academico: "", nivel_enseñanza: "todos", 
    observaciones_profesor: "",
    id_cargo: null as number | null
  };

  let formErrors = { 
    ci: false, nombres: false, apellido_paterno: false, correo: false,
    especialidad: false, titulo_academico: false 
  };
  
  let cargando = false;
  let eliminando = false;
  let errorMessage = "";
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

  // === CARGAR DATOS ===
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

    try {
      // Cargar datos básicos del profesor
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
        id_cargo: data.id_cargo || null
      };

      // Cargar asignaciones
      await cargarAsignaciones(data.id_persona);

      hayCambiosPendientes = false;
    } catch (err: any) {
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
        asignacionesGuardadas = Array.isArray(data) ? data.map((a: any) => ({
          id_materia: a.id_materia,
          id_curso: a.id_curso,
          nombre_materia: a.nombre_materia,
          nombre_curso: a.nombre_curso,
          existeEnBD: true
        })) : [];
      } else {
        console.error("Error cargando asignaciones:", res.status);
      }
    } catch (err) {
      console.error("Error cargando asignaciones:", err);
    }
  }

  function resetForm() {
    formData = { 
      ci: "", nombres: "", apellido_paterno: "", apellido_materno: "", 
      direccion: "", telefono: "", correo: "",
      tipo_persona: "profesor", estado_laboral: "activo", 
      id_persona: null, id_profesor: null,
      especialidad: "", titulo_academico: "", nivel_enseñanza: "todos", 
      observaciones_profesor: "",
      id_cargo: null
    };
    asignacionesPendientes = [];
    asignacionesGuardadas = [];
    asignacionesParaEliminar = [];
    formErrors = { 
      ci: false, nombres: false, apellido_paterno: false, correo: false,
      especialidad: false, titulo_academico: false 
    };
    errorMessage = "";
    hayCambiosPendientes = false;
    materiaSeleccionada = null;
    cursoSeleccionado = null;
    mostrarModalCarga = false;
  }

  // === VALIDACIÓN ===
  function validarForm() {
    let ok = true;
    formErrors = { 
      ci: false, nombres: false, apellido_paterno: false, correo: false,
      especialidad: false, titulo_academico: false 
    };

    if (!formData.ci?.trim()) { formErrors.ci = true; ok = false; }
    if (!formData.nombres?.trim()) { formErrors.nombres = true; ok = false; }
    if (!formData.apellido_paterno?.trim()) { formErrors.apellido_paterno = true; ok = false; }
    if (!formData.correo?.includes("@")) { formErrors.correo = true; ok = false; }
    if (!formData.especialidad?.trim()) { formErrors.especialidad = true; ok = false; }
    if (!formData.titulo_academico?.trim()) { formErrors.titulo_academico = true; ok = false; }

    return ok;
  }

  // === GUARDAR CAMBIOS ===
  async function guardarCambios() {
    if (!validarForm()) {
      errorMessage = "Complete todos los campos requeridos (*)";
      return;
    }

    if (!formData.id_persona) {
      errorMessage = "ID de profesor no válido";
      return;
    }

    cargando = true;
    errorMessage = "";

    try {
      // 1. Actualizar datos del profesor
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
          id_cargo: formData.id_cargo
        })
      });

      if (!resProf.ok) {
        const errorData = await resProf.json();
        throw new Error(errorData.detail || "Error al actualizar los datos del profesor");
      }
      const profActualizado = await resProf.json();

      // 2. Eliminar asignaciones marcadas
      if (asignacionesParaEliminar.length > 0) {
        for (const asignacion of asignacionesParaEliminar) {
          const res = await fetch(`${API_URL}/asignaciones?id_profesor=${profActualizado.id_profesor}&id_curso=${asignacion.id_curso}&id_materia=${asignacion.id_materia}`, {
            method: "DELETE"
          });
          if (!res.ok) throw new Error(`Error al eliminar asignación: ${asignacion.nombre_materia}`);
        }
      }

      // 3. Agregar nuevas asignaciones
      if (asignacionesPendientes.length > 0) {
        for (const asignacion of asignacionesPendientes) {
          const res = await fetch(`${API_URL}/asignaciones`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              id_profesor: profActualizado.id_profesor,
              id_materia: asignacion.id_materia,
              id_curso: asignacion.id_curso
            })
          });
          if (!res.ok) throw new Error(`Error al crear asignación: ${asignacion.nombre_materia}`);
        }
      }

      // 4. Persistir cambios de carga horaria (bloques) preparados por el modal
      // 4.1 Eliminar bloques marcados
      if (bloquesPendientesEliminar.length > 0) {
        for (const b of bloquesPendientesEliminar) {
          if (b.id_bloque) {
            const res = await fetch(`${API_URL}/bloques/${b.id_bloque}`, { method: "DELETE" });
            if (!res.ok) throw new Error(`Error al eliminar bloque ${b.id_bloque}`);
          }
        }
      }
      
      // 4.2 Actualizar bloques existentes
      if (bloquesPendientesActualizar.length > 0) {
        for (const b of bloquesPendientesActualizar) {
          const body = {
            id_profesor: profActualizado.id_profesor,
            id_curso: b.id_curso,
            id_materia: b.id_materia,
            dia_semana: b.dia_semana,
            hora_inicio: (b.hora_inicio && b.hora_inicio.split(':').length === 2) ? `${b.hora_inicio}:00` : b.hora_inicio,
            hora_fin: (b.hora_fin && b.hora_fin.split(':').length === 2) ? `${b.hora_fin}:00` : b.hora_fin,
            gestion: b.gestion,
            observaciones: b.observaciones || null
          };
          const res = await fetch(`${API_URL}/bloques/${b.id_bloque}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
          });
          if (!res.ok) throw new Error(`Error al actualizar bloque ${b.id_bloque}`);
        }
      }
      
      // 4.3 Crear nuevos bloques
      if (bloquesPendientesCrear.length > 0) {
        for (const b of bloquesPendientesCrear) {
          const body = {
            id_profesor: profActualizado.id_profesor,
            id_curso: b.id_curso,
            id_materia: b.id_materia,
            dia_semana: b.dia_semana,
            hora_inicio: (b.hora_inicio && b.hora_inicio.split(':').length === 2) ? `${b.hora_inicio}:00` : b.hora_inicio,
            hora_fin: (b.hora_fin && b.hora_fin.split(':').length === 2) ? `${b.hora_fin}:00` : b.hora_fin,
            gestion: b.gestion,
            observaciones: b.observaciones || null
          };
          const res = await fetch(`${API_URL}/bloques`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
          });
          if (!res.ok) throw new Error(`Error al crear bloque para ${b.nombre_materia}`);
        }
      }

      // Limpiar pendientes después de persistir
      bloquesPendientesCrear = [];
      bloquesPendientesActualizar = [];
      bloquesPendientesEliminar = [];

       // 5. Éxito - recargar datos
       errorMessage = "✅ Profesor actualizado exitosamente";
       hayCambiosPendientes = false;
       
       // Recargar datos actualizados
       setTimeout(() => {
         cargarProfesor(profActualizado);
         dispatch("save", profActualizado);
       }, 1500);

     } catch (err: any) {
       errorMessage = `❌ Error: ${err.message}`;
     } finally {
       cargando = false;
     }
   }

  // === FUNCIONES PARA MODALES DE ASIGNACIÓN ===
  function abrirModalMaterias() {
    mostrarModalMaterias = true;
  }

  function abrirModalCursos() {
    if (!materiaSeleccionada) {
      errorMessage = "⚠️ Primero seleccione una materia";
      return;
    }
    mostrarModalCursos = true;
  }

  function abrirModalCarga() {
    if (!formData.id_profesor) {
      errorMessage = "⚠️ Primero debe guardar los datos del profesor";
      return;
    }
    mostrarModalCarga = true;
  }

  // Handler para cambios temporales de carga horaria (emitido por AsignarCarga)
  function onGuardarCargaTemporal(e: CustomEvent) {
    const { bloques, eliminar } = e.detail;
    // separar nuevos / existentes
    bloquesPendientesCrear = bloques.filter((b: any) => !b.id_bloque).map((b: any) => ({ ...b }));
    bloquesPendientesActualizar = bloques.filter((b: any) => b.id_bloque).map((b: any) => ({ ...b }));
    bloquesPendientesEliminar = eliminar || [];

    hayCambiosPendientes = true;
    mostrarModalCarga = false;
    errorMessage = "✅ Cambios de carga horaria preparados. Presione 'Guardar Cambios' para persistirlos.";
  }

  function onMateriaSeleccionada(e: CustomEvent) {
    materiaSeleccionada = e.detail.materia;
    mostrarModalMaterias = false;
    cursoSeleccionado = null;
  }

  function onCursoSeleccionado(e: CustomEvent) {
    cursoSeleccionado = e.detail.curso;
    mostrarModalCursos = false;
    
    // Agregar a la lista de asignaciones pendientes
    if (materiaSeleccionada && cursoSeleccionado) {
      const nuevaAsignacion = {
        id_materia: materiaSeleccionada.id_materia,
        id_curso: cursoSeleccionado.id_curso,
        nombre_materia: materiaSeleccionada.nombre_materia,
        nombre_curso: cursoSeleccionado.nombre_curso
      };

      // Verificar que no exista ya
      const existe = asignacionesPendientes.some(a => 
        a.id_materia === nuevaAsignacion.id_materia && 
        a.id_curso === nuevaAsignacion.id_curso
      ) || asignacionesGuardadas.some(a => 
        a.id_materia === nuevaAsignacion.id_materia && 
        a.id_curso === nuevaAsignacion.id_curso
      );

      if (!existe) {
        asignacionesPendientes = [...asignacionesPendientes, nuevaAsignacion];
        hayCambiosPendientes = true;
        materiaSeleccionada = null;
        cursoSeleccionado = null;
      } else {
        errorMessage = "⚠️ Esta combinación ya existe";
      }
    }
  }

  function eliminarAsignacionPendiente(index: number) {
    asignacionesPendientes = asignacionesPendientes.filter((_, i) => i !== index);
    hayCambiosPendientes = asignacionesPendientes.length > 0 || asignacionesParaEliminar.length > 0;
  }

  // === ASIGNACIONES EXISTENTES ===
  function onMarcarEliminar(e: CustomEvent) {
    const { index, asignacion } = e.detail;
    asignacionesGuardadas = asignacionesGuardadas.filter((_, i) => i !== index);
    asignacionesParaEliminar = [...asignacionesParaEliminar, asignacion];
    hayCambiosPendientes = true;
  }

  function onRestaurarAsignacion(e: CustomEvent) {
    const { index } = e.detail;
    const asig = asignacionesParaEliminar[index];
    asignacionesGuardadas = [...asignacionesGuardadas, asig];
    asignacionesParaEliminar = asignacionesParaEliminar.filter((_, i) => i !== index);
    hayCambiosPendientes = asignacionesPendientes.length > 0 || asignacionesParaEliminar.length > 0;
  }

  // === ELIMINAR PROFESOR ===
  async function eliminarProfesor() {
    if (!formData.id_persona) return;
    
    if (!confirm("¿Está seguro de eliminar este profesor? Esta acción no se puede deshacer.")) {
      return;
    }

    eliminando = true;
    try {
      const res = await fetch(`${API_URL}/${formData.id_persona}`, { 
        method: "DELETE" 
      });
      
      if (!res.ok) throw new Error("Error al eliminar el profesor");
      
      dispatch("delete", { id: formData.id_persona });
      errorMessage = "✅ Profesor eliminado exitosamente";
      
    } catch (err: any) {
      errorMessage = `❌ Error: ${err.message}`;
    } finally {
      eliminando = false;
    }
  }

  // === CANCELAR ===
  function cancelar() {
    if (hayCambiosPendientes) {
      if (!confirm("Tiene cambios pendientes. ¿Está seguro de cancelar?")) {
        return;
      }
    }
    dispatch("cancel");
  }

  // === DETECTAR CAMBIOS EN FORMULARIO ===
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

<div class="editar-profesor-container">
  <div class="editar-profesor">
    <!-- HEADER CON BOTÓN ELIMINAR -->
    <div class="header">
      <div class="header-title">
        <h2>Editar Profesor</h2>
        {#if formData.id_persona}
          <span class="profesor-id">ID: {formData.id_persona}</span>
        {/if}
      </div>
      <div class="actions">
        <button class="btn-delete" on:click={eliminarProfesor} disabled={eliminando || cargando}>
          {#if eliminando}
            <span class="spinner"></span> Eliminando...
          {:else}
            🗑️ Eliminar
          {/if}
        </button>
        <button class="btn-outline" on:click={cancelar} disabled={cargando || eliminando}>
          Cancelar
        </button>
        <button class="btn-primary" on:click={guardarCambios} disabled={cargando || eliminando || !hayCambiosPendientes}>
          {#if cargando}
            <span class="spinner"></span> Guardando...
          {:else}
            Guardar Cambios
          {/if}
        </button>
      </div>
    </div>

    <!-- ALERTAS -->
    {#if errorMessage}
      <div class="alert {errorMessage.includes('✅') ? 'alert-success' : errorMessage.includes('❌') ? 'alert-error' : errorMessage.includes('⚠️') ? 'alert-warning' : 'alert-info'}">
        {errorMessage}
      </div>
    {/if}

    {#if cargandoDatos}
      <div class="alert alert-info">
        <span class="spinner"></span> Cargando datos del profesor...
      </div>
    {/if}

    {#if hayCambiosPendientes && !cargandoDatos}
      <div class="alert alert-warning">
        ⚠️ Tiene cambios pendientes. No olvide guardar.
      </div>
    {/if}

    <!-- FORMULARIO -->
    <div class="form-content" on:change={onInputChange}>
      <!-- INFORMACIÓN PERSONAL -->
      <section>
        <h3>Información Personal</h3>
        <div class="form-row">
          <div class="form-group">
            <label class:error={formErrors.ci}>Cédula de Identidad *</label>
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
            <select bind:value={formData.estado_laboral} disabled={cargando || eliminando}>
              <option value="activo">Activo</option>
              <option value="inactivo">Inactivo</option>
              <option value="licencia">Licencia</option>
              <option value="jubilado">Jubilado</option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group full-width">
            <label class:error={formErrors.nombres}>Nombres Completos *</label>
            <input 
              type="text" 
              bind:value={formData.nombres} 
              disabled={cargando || eliminando}
              class:error={formErrors.nombres}
              placeholder="Ej: Juan Carlos"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class:error={formErrors.apellido_paterno}>Apellido Paterno *</label>
            <input 
              type="text" 
              bind:value={formData.apellido_paterno} 
              disabled={cargando || eliminando}
              class:error={formErrors.apellido_paterno}
              placeholder="Ej: Pérez"
            />
          </div>
          <div class="form-group">
            <label>Apellido Materno</label>
            <input 
              type="text" 
              bind:value={formData.apellido_materno} 
              disabled={cargando || eliminando}
              placeholder="Ej: González"
            />
          </div>
        </div>
      </section>

      <!-- INFORMACIÓN DE CONTACTO -->
      <section>
        <h3>Información de Contacto</h3>
        <div class="form-row">
          <div class="form-group">
            <label class:error={formErrors.correo}>Correo Electrónico *</label>
            <input 
              type="email" 
              bind:value={formData.correo} 
              disabled={cargando || eliminando}
              class:error={formErrors.correo}
              placeholder="Ej: profesor@colegio.edu"
            />
          </div>
          <div class="form-group">
            <label>Teléfono / Celular</label>
            <input 
              type="tel" 
              bind:value={formData.telefono} 
              disabled={cargando || eliminando}
              placeholder="Ej: 78765432"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group full-width">
            <label>Dirección</label>
            <input 
              type="text" 
              bind:value={formData.direccion} 
              disabled={cargando || eliminando}
              placeholder="Ej: Av. Principal #123"
            />
          </div>
        </div>
      </section>

      <!-- INFORMACIÓN ACADÉMICA -->
      <section>
        <h3>Información Académica</h3>
        <div class="form-row">
          <div class="form-group">
            <label class:error={formErrors.especialidad}>Especialidad *</label>
            <input 
              type="text" 
              bind:value={formData.especialidad} 
              disabled={cargando || eliminando}
              class:error={formErrors.especialidad}
              placeholder="Ej: Matemáticas"
            />
          </div>
          <div class="form-group">
            <label class:error={formErrors.titulo_academico}>Título Académico *</label>
            <input 
              type="text" 
              bind:value={formData.titulo_academico} 
              disabled={cargando || eliminando}
              class:error={formErrors.titulo_academico}
              placeholder="Ej: Lic. en Educación"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Nivel de Enseñanza</label>
            <select bind:value={formData.nivel_enseñanza} disabled={cargando || eliminando}>
              <option value="todos">Todos los niveles</option>
              <option value="inicial">Educación Inicial</option>
              <option value="primaria">Educación Primaria</option>
              <option value="secundaria">Educación Secundaria</option>
            </select>
          </div>
          <div class="form-group">
            <label>Cargo</label>
            <select bind:value={formData.id_cargo} disabled={cargando || eliminando}>
              <option value={null}>Seleccione un cargo</option>
              {#each cargos as cargo}
                <option value={cargo.id_cargo}>{cargo.nombre_cargo}</option>
              {/each}
            </select>
          </div>
        </div>

        <div class="form-row">
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
        <h3>Materias y Cursos Asignados</h3>
        <p class="section-description">
          Asignaciones actuales del profesor. Puede eliminar asignaciones marcándolas para eliminación.
        </p>
        
        {#if asignacionesGuardadas.length === 0}
          <div class="no-asignaciones">
            <p>📝 Este profesor no tiene asignaciones actualmente.</p>
          </div>
        {:else}
          <div class="asignaciones-lista">
            {#each asignacionesGuardadas as asignacion, index}
              <div class="asignacion-item">
                <div class="asignacion-info">
                  <span class="materia-nombre">{asignacion.nombre_materia}</span>
                  <span class="separator">-</span>
                  <span class="curso-nombre">{asignacion.nombre_curso}</span>
                </div>
                <button 
                  class="btn-eliminar-asignacion"
                  on:click={() => onMarcarEliminar({ detail: { index, asignacion } })}
                  disabled={cargando || eliminando}
                  title="Eliminar asignación"
                >
                  🗑️
                </button>
              </div>
            {/each}
          </div>
        {/if}
      </section>

      <!-- ASIGNACIONES MARCADAS PARA ELIMINAR -->
      {#if asignacionesParaEliminar.length > 0}
        <section class="asignaciones-eliminar">
          <h3>Asignaciones Marcadas para Eliminar</h3>
          <p class="section-description">
            Estas asignaciones se eliminarán al guardar los cambios.
          </p>
          <div class="asignaciones-lista eliminar">
            {#each asignacionesParaEliminar as asignacion, index}
              <div class="asignacion-item eliminada">
                <div class="asignacion-info">
                  <span class="materia-nombre">{asignacion.nombre_materia}</span>
                  <span class="separator">-</span>
                  <span class="curso-nombre">{asignacion.nombre_curso}</span>
                </div>
                <button 
                  class="btn-restaurar-asignacion"
                  on:click={() => onRestaurarAsignacion({ detail: { index } })}
                  disabled={cargando || eliminando}
                  title="Restaurar asignación"
                >
                  ↩️
                </button>
              </div>
            {/each}
          </div>
        </section>
      {/if}

      <!-- ASIGNAR NUEVAS MATERIAS Y CURSOS -->
      <section>
        <h3>Asignar Nuevas Materias y Cursos</h3>
        <p class="section-description">
          Seleccione materias y cursos para asignar al profesor
        </p>
        
        <!-- Selectores tipo dropdown -->
        <div class="selectores-container">
          <div class="selector-group">
            <label>Materia</label>
            <div class="selector-input" on:click={abrirModalMaterias}>
              {#if materiaSeleccionada}
                <span class="seleccionado">{materiaSeleccionada.nombre_materia}</span>
              {:else}
                <span class="placeholder">Seleccione una materia</span>
              {/if}
              <span class="dropdown-arrow">▼</span>
            </div>
          </div>

          <div class="selector-group">
            <label>Curso</label>
            <div 
              class="selector-input {!materiaSeleccionada ? 'disabled' : ''}" 
              on:click={abrirModalCursos}
            >
              {#if cursoSeleccionado}
                <span class="seleccionado">{cursoSeleccionado.nombre_curso}</span>
              {:else}
                <span class="placeholder">Seleccione un curso</span>
              {/if}
              <span class="dropdown-arrow">▼</span>
            </div>
          </div>
        </div>

        <!-- Lista de asignaciones pendientes -->
        {#if asignacionesPendientes.length > 0}
          <div class="asignaciones-pendientes-lista">
            <h4>Asignaciones Pendientes ({asignacionesPendientes.length})</h4>
            {#each asignacionesPendientes as asignacion, index}
              <div class="asignacion-item pendiente">
                <div class="asignacion-info">
                  <span class="materia-nombre">{asignacion.nombre_materia}</span>
                  <span class="separator">-</span>
                  <span class="curso-nombre">{asignacion.nombre_curso}</span>
                </div>
                <button 
                  class="btn-eliminar-pendiente"
                  on:click={() => eliminarAsignacionPendiente(index)}
                  disabled={cargando || eliminando}
                  title="Eliminar asignación pendiente"
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

      <!-- ASIGNAR CARGA HORARIA -->
      <section class="carga-horaria-section">
        <div class="carga-horaria-header">
          <div>
            <h3>Gestión de Carga Horaria</h3>
            <p class="section-description">
              Asigne horarios específicos a las materias y cursos del profesor
            </p>
          </div>
          <button 
            class="btn-carga-horaria"
            on:click={abrirModalCarga}
            disabled={!formData.id_profesor || cargando || eliminando}
          >
            📅 Asignar Carga Horaria
          </button>
        </div>

        {#if !formData.id_profesor}
          <div class="advertencia-carga">
            <p>⚠️ Debe guardar los datos del profesor primero para poder asignar la carga horaria</p>
          </div>
        {/if}
      </section>

      <!-- RESUMEN DE CAMBIOS -->
      {#if (asignacionesPendientes.length > 0 || asignacionesParaEliminar.length > 0)}
        <section class="resumen-cambios">
          <h3>Resumen de Cambios</h3>
          <div class="cambios-lista">
            {#if asignacionesPendientes.length > 0}
              <div class="cambio-grupo">
                <h4>Nuevas Asignaciones ({asignacionesPendientes.length})</h4>
                {#each asignacionesPendientes as asignacion}
                  <div class="cambio-item nueva">
                    <span class="icon">➕</span>
                    <span>{asignacion.nombre_materia} - {asignacion.nombre_curso}</span>
                  </div>
                {/each}
              </div>
            {/if}

            {#if asignacionesParaEliminar.length > 0}
              <div class="cambio-grupo">
                <h4>Asignaciones a Eliminar ({asignacionesParaEliminar.length})</h4>
                {#each asignacionesParaEliminar as asignacion}
                  <div class="cambio-item eliminar">
                    <span class="icon">➖</span>
                    <span>{asignacion.nombre_materia} - {asignacion.nombre_curso}</span>
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

<!-- Modales de selección -->
<AsignarMaterias
  mostrar={mostrarModalMaterias}
  materiaSeleccionada={materiaSeleccionada}
  on:materiaSeleccionada={onMateriaSeleccionada}
  on:cerrar={() => mostrarModalMaterias = false}
/>

<AsignarCursos
  mostrar={mostrarModalCursos}
  cursoSeleccionado={cursoSeleccionado}
  on:cursoSeleccionado={onCursoSeleccionado}
  on:cerrar={() => mostrarModalCursos = false}
/>


<AsignarCarga
  mostrar={mostrarModalCarga}
  profesor={formData}
  asignaciones={asignacionesGuardadas.concat(asignacionesPendientes)}
  autoSave={false}
  on:guardarTemporal={onGuardarCargaTemporal}
  on:cerrar={() => mostrarModalCarga = false}
/>

<style>
  .editar-profesor-container {
    width: 100%;
    height: 100vh;
    overflow-y: auto;
    background: #f8fafc;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  .editar-profesor {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    max-width: 900px;
    margin: 0 auto;
    min-height: fit-content;
  }

  .form-content {
    display: flex;
    flex-direction: column;
    gap: 24px;
    max-height: calc(100vh - 200px);
    overflow-y: auto;
    padding-right: 8px;
  }

  /* Scroll personalizado */
  .form-content::-webkit-scrollbar {
    width: 6px;
  }

  .form-content::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }

  .form-content::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;
  }

  .form-content::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 16px;
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
  }

  .header-title h2 {
    margin: 0 0 4px 0;
    font-size: 1.25rem;
    color: #1e293b;
    font-weight: 600;
  }

  .profesor-id {
    font-size: 0.85rem;
    color: #64748b;
    background: #f1f5f9;
    padding: 2px 8px;
    border-radius: 4px;
  }

  .actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .btn-outline, .btn-primary, .btn-delete {
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 0.9rem;
    cursor: pointer;
    border: none;
    font-weight: 500;
    transition: all 0.2s;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
  }

  .btn-outline {
    background: #fff;
    color: #64748b;
    border: 1.5px solid #e2e8f0;
  }

  .btn-outline:hover:not(:disabled) {
    background: #f8fafc;
    border-color: #cbd5e1;
  }

  .btn-primary {
    background: #00cfe6;
    color: #fff;
  }

  .btn-primary:hover:not(:disabled) {
    background: #00b8d4;
    transform: translateY(-1px);
  }

  .btn-primary:disabled {
    background: #cbd5e1;
    cursor: not-allowed;
    transform: none;
  }

  .btn-delete {
    background: #ef4444;
    color: #fff;
  }

  .btn-delete:hover:not(:disabled) {
    background: #dc2626;
    transform: translateY(-1px);
  }

  .btn-outline:disabled, .btn-primary:disabled, .btn-delete:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .alert {
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    font-size: 0.9rem;
    border: 1px solid;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  .alert-success {
    background: #dcfce7;
    color: #166534;
    border-color: #86efac;
  }

  .alert-error {
    background: #fee2e2;
    color: #991b1b;
    border-color: #fca5a5;
  }

  .alert-warning {
    background: #fffbeb;
    color: #92400e;
    border-color: #fcd34d;
  }

  .alert-info {
    background: #dbeafe;
    color: #1e40af;
    border-color: #93c5fd;
  }

  section {
    background: #fafbfc;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }

  .asignaciones-eliminar {
    background: #fef2f2;
    border-color: #fecaca;
  }

  .resumen-cambios {
    background: #fff7ed;
    border-color: #fdba74;
  }

  .carga-horaria-section {
    background: #f0f9ff;
    border-color: #bae6fd;
  }

  section h3 {
    margin: 0 0 12px 0;
    font-size: 1rem;
    color: #1e293b;
    font-weight: 600;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
  }

  .section-description {
    margin: -8px 0 16px 0;
    color: #64748b;
    font-size: 0.9rem;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
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
    margin-bottom: 6px;
    font-size: 0.85rem;
    color: #475569;
    font-weight: 500;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
  }

  .error {
    color: #dc2626;
  }

  input, select, textarea {
    padding: 10px 12px;
    border: 1.5px solid #e2e8f0;
    border-radius: 6px;
    font-size: 0.9rem;
    background: white;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;  color: black;
    transition: border-color 0.2s;
  }

  input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: #00cfe6;
    box-shadow: 0 0 0 3px rgba(0,207,230,0.1);
  }

  input.error, select.error, textarea.error {
    border-color: #dc2626;
  }

  /* Selectores de materias y cursos */
  .selectores-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 20px;
  }

  .selector-group {
    display: flex;
    flex-direction: column;
  }

  .selector-input {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    background: white;
    cursor: pointer;
    transition: border-color 0.2s;
    min-height: 42px;
  }

  .selector-input:hover {
    border-color: #00cfe6;
  }

  .selector-input.disabled {
    background: #f8fafc;
    cursor: not-allowed;
    color: #94a3b8;
  }

  .seleccionado {
    font-weight: 500;
    color: #1e293b;
  }

  .placeholder {
    color: #94a3b8;
  }

  .dropdown-arrow {
    color: #64748b;
    font-size: 0.8rem;
  }

  /* Asignaciones */
  .no-asignaciones {
    text-align: center;
    padding: 20px;
    color: #64748b;
  }

  .asignaciones-lista, .asignaciones-pendientes-lista {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .asignacion-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: white;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    transition: all 0.2s;
  }

  .asignacion-item:hover {
    border-color: #cbd5e1;
  }

  .asignacion-item.eliminada {
    background: #fef2f2;
    border-color: #fecaca;
    text-decoration: line-through;
    color: #dc2626;
  }

  .asignacion-item.pendiente {
    background: #f0fdf4;
    border-color: #bbf7d0;
  }

  .asignacion-info {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .materia-nombre {
    font-weight: 500;
    color: #1e293b;
  }

  .separator {
    color: #94a3b8;
  }

  .curso-nombre {
    color: #475569;
  }

  .btn-eliminar-asignacion, .btn-restaurar-asignacion, .btn-eliminar-pendiente {
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px;
    border-radius: 4px;
    transition: background-color 0.2s;
    font-size: 0.9rem;
  }

  .btn-eliminar-asignacion:hover:not(:disabled) {
    background: #fef2f2;
  }

  .btn-restaurar-asignacion:hover:not(:disabled) {
    background: #f0fdf4;
  }

  .btn-eliminar-pendiente {
    background: #ef4444;
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
  }

  .btn-eliminar-pendiente:hover:not(:disabled) {
    background: #dc2626;
  }

  .btn-eliminar-asignacion:disabled, .btn-restaurar-asignacion:disabled, .btn-eliminar-pendiente:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .sin-asignaciones-pendientes {
    text-align: center;
    color: #94a3b8;
    font-style: italic;
    padding: 20px;
    background: #f8fafc;
    border: 1px dashed #e2e8f0;
    border-radius: 6px;
  }

  /* Carga horaria */
  .carga-horaria-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
  }

  .btn-carga-horaria {
    background: #0ea5e9;
    color: white;
    border: none;
    padding: 10px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    white-space: nowrap;
    transition: background-color 0.2s;
  }

  .btn-carga-horaria:hover:not(:disabled) {
    background: #0284c7;
    
  }

  .btn-carga-horaria:disabled {
    background: #cbd5e1;
    cursor: not-allowed;
    opacity: 0.6;
  }

  .advertencia-carga {
    background: #fffbeb;
    border: 1px solid #fcd34d;
    border-radius: 6px;
    padding: 12px 16px;
    margin-top: 12px;
  }

  .advertencia-carga p {
    margin: 0;
    color: #92400e;
    font-size: 0.9rem;
  }

  /* Resumen de cambios */
  .cambios-lista {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .cambio-grupo h4 {
    margin: 0 0 8px 0;
    font-size: 0.9rem;
    color: #475569;
    font-weight: 600;
  }

  .cambio-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: white;
    border-radius: 6px;
    border-left: 4px solid;
  }

  .cambio-item.nueva {
    border-left-color: #10b981;
  }

  .cambio-item.eliminar {
    border-left-color: #ef4444;
  }

  .cambio-item .icon {
    font-size: 0.8rem;
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
    to { transform: rotate(360deg); }
  }

  @media (max-width: 768px) {
    .editar-profesor-container {
      padding: 8px;
    }

    .editar-profesor {
      padding: 16px;
      border-radius: 8px;
    }

    .header {
      flex-direction: column;
      gap: 12px;
      align-items: stretch;
    }

    .actions {
      justify-content: stretch;
      flex-wrap: wrap;
    }

    .btn-outline, .btn-primary, .btn-delete {
      flex: 1;
      min-width: 120px;
    }

    .form-content {
      max-height: calc(100vh - 240px);
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
      justify-content: center;
    }
  }

  @media (max-width: 480px) {
    .actions {
      flex-direction: column;
    }

    .btn-outline, .btn-primary, .btn-delete {
      width: 100%;
    }
  }
</style>