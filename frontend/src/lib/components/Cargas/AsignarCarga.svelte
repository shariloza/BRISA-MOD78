<script lang="ts">
  import { onMount, createEventDispatcher } from "svelte";

  const API_URL = "http://localhost:8000/api/profesores";

  interface BloqueHorario {
    id_bloque?: number;
    id_profesor: number;
    id_curso: number;
    id_materia: number;
    dia_semana: string;
    hora_inicio: string;
    hora_fin: string;
    gestion: string;
    observaciones?: string;
    nombre_materia?: string;
    nombre_curso?: string;
  }

  interface Asignacion {
    id_materia: number;
    id_curso: number;
    nombre_materia: string;
    nombre_curso: string;
  }

  export let profesor: any = null;
  export let mostrar: boolean = false;
  export let asignaciones: Asignacion[] = [];
  export let autoSave: boolean = false; // si en algún momento se desea auto-save (por defecto false)

  const dispatch = createEventDispatcher<{
    guardar: void;
    guardarTemporal: { bloques: BloqueHorario[]; eliminar: BloqueHorario[] };
    cerrar: void;
  }>();

  // Estados
  let bloquesHorarios: BloqueHorario[] = [];
  let bloquesEditando: BloqueHorario[] = [];
  let cargando = false;
  let guardando = false;
  let errorMessage = "";
  let gestionActual = "2025";

  // Bloques calculados / cambios locales
  // bloquesAEliminar: bloques que estaban en BD (bloquesHorarios) y ya no están en bloquesEditando
  let bloquesAEliminar: BloqueHorario[] = [];
  // indicador si hay modificaciones locales que deben guardarse (crear/actualizar/eliminar)
  let hayCambiosLocal = false;

  // Nuevo bloque temporal
  let nuevoBloque: Partial<BloqueHorario> & { asignacionId?: string } = {
    asignacionId: "",
    dia_semana: "lunes",
    hora_inicio: "08:00",
    hora_fin: "09:00",
    gestion: gestionActual,
    observaciones: ""
  };

  // Opciones disponibles
  const diasSemana = [
    { value: "lunes", label: "Lunes" },
    { value: "martes", label: "Martes" },
    { value: "miercoles", label: "Miércoles" },
    { value: "jueves", label: "Jueves" },
    { value: "viernes", label: "Viernes" },
  ];

  const horasDisponibles = [
    "07:00", "07:30", "08:00", "08:30", "09:00", "09:30", 
    "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", 
    "17:00", "17:30", "18:00", "18:30", "19:00", "19:30"
  ];

  // Cargar bloques horarios existentes
  async function cargarBloquesHorarios() {
    if (!profesor?.id_persona) return;

    cargando = true;
    errorMessage = "";

    try {
      const resBloques = await fetch(`${API_URL}/${profesor.id_persona}/bloques?gestion=${gestionActual}`);
      if (resBloques.ok) {
        const data = await resBloques.json();
        bloquesHorarios = Array.isArray(data) ? data.map((b: any) => ({
          ...b,
          hora_inicio: b.hora_inicio?.substring(0, 5) || "08:00",
          hora_fin: b.hora_fin?.substring(0, 5) || "09:00"
        })) : [];
      }

      // Inicializar bloques en edición
      bloquesEditando = [...bloquesHorarios];

    } catch (err: any) {
      errorMessage = `Error al cargar bloques horarios: ${err.message}`;
    } finally {
      cargando = false;
    }
  }

  // Manejar selección de materia y curso
  function manejarSeleccionAsignacion(event: Event) {
    const target = event.target as HTMLSelectElement;
    const selectedOption = target.options[target.selectedIndex];
    
    if (selectedOption.value) {
      const [idMateria, idCurso] = selectedOption.value.split('-');
      nuevoBloque.id_materia = parseInt(idMateria);
      nuevoBloque.id_curso = parseInt(idCurso);
      nuevoBloque.asignacionId = selectedOption.value;
    } else {
      nuevoBloque.id_materia = undefined;
      nuevoBloque.id_curso = undefined;
      nuevoBloque.asignacionId = "";
    }
  }

  // Agregar nuevo bloque horario
  function agregarBloque() {
    if (!nuevoBloque.id_materia || !nuevoBloque.id_curso) {
      errorMessage = "⚠️ Seleccione una materia y curso";
      return;
    }

    if (!nuevoBloque.hora_inicio || !nuevoBloque.hora_fin) {
      errorMessage = "⚠️ Seleccione horario de inicio y fin";
      return;
    }

    // Validar que la hora de fin sea mayor que la de inicio
    if (nuevoBloque.hora_fin <= nuevoBloque.hora_inicio) {
      errorMessage = "⚠️ La hora de fin debe ser mayor que la hora de inicio";
      return;
    }

    // Validar que no se solape con otros bloques del mismo día
    const bloquesMismoDia = bloquesEditando.filter(b => 
      b.dia_semana === nuevoBloque.dia_semana
    );

    const solapado = bloquesMismoDia.some(bloque => {
      return (
        (nuevoBloque.hora_inicio! >= bloque.hora_inicio && nuevoBloque.hora_inicio! < bloque.hora_fin) ||
        (nuevoBloque.hora_fin! > bloque.hora_inicio && nuevoBloque.hora_fin! <= bloque.hora_fin) ||
        (nuevoBloque.hora_inicio! <= bloque.hora_inicio && nuevoBloque.hora_fin! >= bloque.hora_fin)
      );
    });

    if (solapado) {
      errorMessage = "⚠️ El horario se solapa con otro bloque del mismo día";
      return;
    }

    const asignacion = asignaciones.find(a => 
      a.id_materia === nuevoBloque.id_materia && a.id_curso === nuevoBloque.id_curso
    );

    if (!asignacion) {
      errorMessage = "⚠️ Asignación no válida";
      return;
    }

    const bloque: BloqueHorario = {
      id_profesor: profesor.id_profesor,
      id_curso: nuevoBloque.id_curso!,
      id_materia: nuevoBloque.id_materia!,
      dia_semana: nuevoBloque.dia_semana!,
      hora_inicio: nuevoBloque.hora_inicio!,
      hora_fin: nuevoBloque.hora_fin!,
      gestion: nuevoBloque.gestion!,
      observaciones: nuevoBloque.observaciones,
      nombre_materia: asignacion.nombre_materia,
      nombre_curso: asignacion.nombre_curso
    };

    bloquesEditando = [...bloquesEditando, bloque];
    
    // Resetear formulario
    nuevoBloque = {
      asignacionId: "",
      dia_semana: "lunes",
      hora_inicio: "08:00",
      hora_fin: "09:00",
      gestion: gestionActual,
      observaciones: ""
    };
    
    errorMessage = "";
  }

  // Eliminar bloque horario
  function eliminarBloque(index: number) {
    bloquesEditando = bloquesEditando.filter((_, i) => i !== index);
  }

  // Actualizar bloque existente
  function actualizarBloque(index: number, campo: string, valor: any) {
    bloquesEditando = bloquesEditando.map((bloque, i) => 
      i === index ? { ...bloque, [campo]: valor } : bloque
    );
  }

  // Guardado: si autoSave===false -> emitimos los cambios y NO hacemos requests (temporal).
  async function guardarCambios(confirm: boolean = false) {
    // reutilizar el cálculo reactivo de bloquesAEliminar
    // (si por alguna razón no está calculado, calcularlo aquí)
    if (!Array.isArray(bloquesAEliminar) || bloquesAEliminar.length === 0) {
      bloquesAEliminar = bloquesHorarios.filter(bloqueDb =>
        !bloquesEditando.some(bloqueEdit => bloqueEdit.id_bloque === bloqueDb.id_bloque)
      );
    }

    // Si no está activado autoSave, emitimos los cambios al padre para persistencia posterior
    if (!autoSave) {
      dispatch("guardarTemporal", { bloques: bloquesEditando, eliminar: bloquesAEliminar });
      errorMessage = "✅ Cambios de carga horaria preparados (pendientes). Presione 'Guardar Cambios' en el editor para persistirlos.";
      return;
    }

    // Si autoSave === true, ejecutar persistencia inmediata (comportamiento original)
    guardando = true;
    errorMessage = "";
    try {
      // Eliminar bloques
      for (const bloque of bloquesAEliminar) {
        if (bloque.id_bloque) {
          const res = await fetch(`${API_URL}/bloques/${bloque.id_bloque}`, {
            method: "DELETE"
          });
          if (!res.ok) throw new Error(`Error al eliminar bloque ${bloque.id_bloque}`);
        }
      }

      // Crear/actualizar bloques
      for (const bloque of bloquesEditando) {
        const bloqueData = {
          id_profesor: bloque.id_profesor,
          id_curso: bloque.id_curso,
          id_materia: bloque.id_materia,
          dia_semana: bloque.dia_semana,
          hora_inicio: `${bloque.hora_inicio}:00`,
          hora_fin: `${bloque.hora_fin}:00`,
          gestion: bloque.gestion,
          observaciones: bloque.observaciones || null
        };

        if (bloque.id_bloque) {
          const res = await fetch(`${API_URL}/bloques/${bloque.id_bloque}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(bloqueData)
          });
          if (!res.ok) throw new Error(`Error al actualizar bloque ${bloque.id_bloque}`);
        } else {
          const res = await fetch(`${API_URL}/bloques`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(bloqueData)
          });
          if (!res.ok) throw new Error(`Error al crear bloque`);
        }
      }

      errorMessage = "✅ Carga horaria guardada exitosamente";
      setTimeout(() => {
        cargarBloquesHorarios();
        dispatch("guardar");
      }, 1500);
    } catch (err: any) {
      errorMessage = `❌ Error al guardar: ${err.message}`;
    } finally {
      guardando = false;
    }
  }

  // REACTIVIDAD: calcular bloquesAEliminar y si hay cambios locales
  $: {
    // determinar bloques eliminados (los que estaban en BD y ya no están en edición)
    bloquesAEliminar = bloquesHorarios.filter(bloqueDb =>
      !bloquesEditando.some(bloqueEdit => bloqueEdit.id_bloque === bloqueDb.id_bloque)
    );

    // detectar nuevos bloques (sin id_bloque)
    const nuevos = bloquesEditando.some(b => !b.id_bloque);

    // detectar cambios en bloques existentes (comparando campos relevantes)
    const modificados = bloquesEditando.some(b => {
      if (!b.id_bloque) return false;
      const orig = bloquesHorarios.find(o => o.id_bloque === b.id_bloque);
      if (!orig) return false;
      return (
        orig.hora_inicio !== b.hora_inicio ||
        orig.hora_fin !== b.hora_fin ||
        orig.dia_semana !== b.dia_semana ||
        orig.id_curso !== b.id_curso ||
        orig.id_materia !== b.id_materia ||
        (orig.observaciones || "") !== (b.observaciones || "")
      );
    });

    hayCambiosLocal = nuevos || modificados || (bloquesAEliminar.length > 0);
  }

  // Cerrar modal
  function cerrar() {
    // Resetear estado al cerrar
    nuevoBloque = {
      asignacionId: "",
      dia_semana: "lunes",
      hora_inicio: "08:00",
      hora_fin: "09:00",
      gestion: gestionActual,
      observaciones: ""
    };
    errorMessage = "";
    dispatch("cerrar");
  }

  // REACTIVIDAD: cuando cambian las asignaciones disponibles, actualizar la UI y bloques en edición
  $: if (asignaciones) {
    // construir conjunto de combinaciones válidas "id_materia-id_curso"
    const asignKeys = new Set(asignaciones.map(a => `${a.id_materia}-${a.id_curso}`));

    // Si la selección actual del nuevo bloque ya no existe, limpiar la selección
    if (nuevoBloque.asignacionId && !asignKeys.has(nuevoBloque.asignacionId)) {
      nuevoBloque.asignacionId = "";
      nuevoBloque.id_materia = undefined;
      nuevoBloque.id_curso = undefined;
    }

    // Filtrar bloques en edición: eliminar aquellos que ya no poseen asignación válida.
    // Esto garantiza que, si en el padre se eliminó una asignación (por ejemplo usuario marcó
    // para eliminar una materia/curso), los bloques dependientes se retiren del editor y
    // queden marcados para eliminación al persistir (la detección de eliminados se hace
    // comparando con bloquesHorarios cargados desde BD).
    const removed = bloquesEditando.filter(b => !asignKeys.has(`${b.id_materia}-${b.id_curso}`));
    if (removed.length > 0) {
      bloquesEditando = bloquesEditando.filter(b => asignKeys.has(`${b.id_materia}-${b.id_curso}`));
      // informar al usuario (mensaje informativo no bloqueante)
      errorMessage = "⚠️ Algunas cargas han sido removidas porque cambió la lista de asignaciones.";
    }
  }

  // Calcular duración en horas
  function calcularDuracion(horaInicio: string, horaFin: string): number {
    const [h1, m1] = horaInicio.split(':').map(Number);
    const [h2, m2] = horaFin.split(':').map(Number);
    const minutosTotales = (h2 * 60 + m2) - (h1 * 60 + m1);
    return minutosTotales / 60;
  }

  // Calcular total de horas por día
  function calcularHorasPorDia(dia: string): number {
    return bloquesEditando
      .filter(bloque => bloque.dia_semana === dia)
      .reduce((total, bloque) => total + calcularDuracion(bloque.hora_inicio, bloque.hora_fin), 0);
  }

  // Calcular total de horas semanales
  $: totalHorasSemanales = bloquesEditando.reduce((total, bloque) => 
    total + calcularDuracion(bloque.hora_inicio, bloque.hora_fin), 0
  );

  // Cargar datos cuando se abre el modal
  $: if (mostrar && profesor) {
    cargarBloquesHorarios();
  }
</script>

{#if mostrar}
<div class="modal-overlay" on:click={cerrar}>
  <div class="modal-content" on:click|stopPropagation>
    
    <!-- HEADER -->
    <div class="modal-header">
      <div class="header-title">
        <h2>Asignar Carga Horaria</h2>
        <p class="profesor-info">
          {profesor?.nombres} {profesor?.apellido_paterno} 
          {#if profesor?.especialidad} - {profesor.especialidad}{/if}
        </p>
      </div>
      <button class="btn-cerrar" on:click={cerrar}>×</button>
    </div>

    <!-- ALERTAS -->
    {#if errorMessage}
      <div class="alert {errorMessage.includes('✅') ? 'alert-success' : errorMessage.includes('❌') ? 'alert-error' : 'alert-warning'}">
        {errorMessage}
      </div>
    {/if}

    {#if cargando}
      <div class="alert alert-info">
        <span class="spinner"></span> Cargando carga horaria...
      </div>
    {/if}

    <div class="carga-horaria-content">
      
      <!-- RESUMEN DE HORAS -->
      <div class="resumen-horas">
        <div class="resumen-header">
          <span class="resumen-label">Total Horas Semanales:</span>
          <span class="resumen-value {totalHorasSemanales > 40 ? 'sobrecarga' : ''}">
            {totalHorasSemanales.toFixed(1)}h
          </span>
        </div>
        <div class="resumen-dias">
          {#each diasSemana as dia}
            <div class="dia-horas">
              <span>{dia.label}:</span>
              <span>{calcularHorasPorDia(dia.value).toFixed(1)}h</span>
            </div>
          {/each}
        </div>
      </div>

      <!-- FORMULARIO PARA NUEVO BLOQUE -->
      <div class="nuevo-bloque-section">
        <h3>Agregar Nuevo Bloque Horario</h3>
        
        <div class="form-nuevo-bloque">
          <div class="form-row">
            <div class="form-group">
              <label>Materia y Curso *</label>
              <select 
                bind:value={nuevoBloque.asignacionId}
                on:change={manejarSeleccionAsignacion}
              >
                <option value="">Seleccione materia y curso</option>
                {#each asignaciones as asignacion}
                  <option value={`${asignacion.id_materia}-${asignacion.id_curso}`}>
                    {asignacion.nombre_materia} - {asignacion.nombre_curso}
                  </option>
                {/each}
              </select>
            </div>
            
            <div class="form-group">
              <label>Día de la Semana *</label>
              <select bind:value={nuevoBloque.dia_semana}>
                {#each diasSemana as dia}
                  <option value={dia.value}>{dia.label}</option>
                {/each}
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Hora Inicio *</label>
              <select bind:value={nuevoBloque.hora_inicio}>
                {#each horasDisponibles as hora}
                  <option value={hora}>{hora}</option>
                {/each}
              </select>
            </div>
            
            <div class="form-group">
              <label>Hora Fin *</label>
              <select bind:value={nuevoBloque.hora_fin}>
                {#each horasDisponibles as hora}
                  {#if hora > nuevoBloque.hora_inicio}
                    <option value={hora}>{hora}</option>
                  {/if}
                {/each}
              </select>
            </div>
            
            <div class="form-group">
              <label>Gestión</label>
              <input type="text" bind:value={nuevoBloque.gestion} />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group full-width">
              <label>Observaciones</label>
              <input 
                type="text" 
                bind:value={nuevoBloque.observaciones} 
                placeholder="Observaciones opcionales..."
              />
            </div>
          </div>

          <button class="btn-agregar" on:click={agregarBloque}>
            + Agregar Bloque Horario
          </button>
        </div>
      </div>

      <!-- LISTA DE BLOQUES HORARIOS -->
      <div class="bloques-lista-section">
        <h3>Bloques Horarios Asignados ({bloquesEditando.length})</h3>
        
        {#if bloquesEditando.length === 0}
          <div class="sin-bloques">
            <p>📝 No hay bloques horarios asignados</p>
            <p class="sin-bloques-desc">Agregue bloques horarios usando el formulario superior</p>
          </div>
        {:else}
          <div class="bloques-lista">
            {#each bloquesEditando as bloque, index}
              <div class="bloque-item">
                <div class="bloque-info">
                  <div class="bloque-principal">
                    <span class="materia-curso">
                      {bloque.nombre_materia} - {bloque.nombre_curso}
                    </span>
                    <span class="bloque-horario">
                      {bloque.dia_semana} | {bloque.hora_inicio} - {bloque.hora_fin} 
                      | <strong>{calcularDuracion(bloque.hora_inicio, bloque.hora_fin).toFixed(1)}h</strong>
                    </span>
                  </div>
                  {#if bloque.observaciones}
                    <div class="bloque-observaciones">
                      📝 {bloque.observaciones}
                    </div>
                  {/if}
                  {#if !bloque.id_bloque}
                    <div class="bloque-nuevo-indicator">
                      ✨ Nuevo (pendiente de guardar)
                    </div>
                  {/if}
                </div>
                
                <div class="bloque-actions">
                  <button 
                    class="btn-eliminar-bloque"
                    on:click={() => eliminarBloque(index)}
                    title="Eliminar bloque"
                    disabled={guardando}
                  >
                    🗑️
                  </button>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- BOTONES DE ACCIÓN -->
      <div class="modal-actions">
        <button class="btn-cancelar" on:click={cerrar} disabled={guardando}>
          Cancelar
        </button>
        <!-- habilitar si hay cambios locales (crear/actualizar/eliminar) o si autoSave está activado -->
        <button 
          class="btn-guardar" 
          on:click={() => guardarCambios(true)}
          disabled={guardando || (!autoSave && !hayCambiosLocal)}
        >
          {#if guardando}
            <span class="spinner"></span> Guardando...
          {:else}
            💾 Guardar Carga Horaria
          {/if}
        </button>
      </div>
    </div>
  </div>
</div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
  }

  .modal-content {
    background: white;
    border-radius: 12px;
    width: 90%;
    max-width: 900px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 24px;
    border-bottom: 1px solid #e2e8f0;
    background: #f8fafc;
    border-radius: 12px 12px 0 0;
  }

  .header-title h2 {
    margin: 0 0 4px 0;
    font-size: 1.25rem;
    color: #1e293b;
    font-weight: 600;
  }

  .profesor-info {
    margin: 0;
    color: #64748b;
    font-size: 0.9rem;
  }

  .btn-cerrar {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #64748b;
    padding: 4px;
    border-radius: 4px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .btn-cerrar:hover {
    background: #e2e8f0;
  }

  .carga-horaria-content {
    padding: 24px;
  }

  /* ALERTAS */
  .alert {
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    font-size: 0.9rem;
    border: 1px solid;
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
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* RESUMEN DE HORAS */
  .resumen-horas {
    background: #f8fafc;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    margin-bottom: 24px;
  }

  .resumen-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e2e8f0;
  }

  .resumen-label {
    font-weight: 600;
    color: #475569;
    font-size: 1rem;
  }

  .resumen-value {
    font-weight: 700;
    font-size: 1.2rem;
    color: #1e293b;
  }

  .resumen-value.sobrecarga {
    color: #dc2626;
  }

  .resumen-dias {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
  }

  .dia-horas {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    color: #475569;
    padding: 8px 12px;
    background: white;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
  }

  /* FORMULARIO NUEVO BLOQUE */
  .nuevo-bloque-section {
    margin-bottom: 32px;
  }

  .nuevo-bloque-section h3 {
    margin: 0 0 16px 0;
    font-size: 1.1rem;
    color: #1e293b;
    font-weight: 600;
  }

  .form-nuevo-bloque {
    background: #fafbfc;
    padding: 24px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
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
  }

  select, input {
    padding: 10px 12px;
    border: 1.5px solid #e2e8f0;
    border-radius: 6px;
    font-size: 0.9rem;
    background: white;
    color: #1e293b;
    transition: border-color 0.2s;
  }

  select:focus, input:focus {
    outline: none;
    border-color: #00cfe6;
    box-shadow: 0 0 0 3px rgba(0, 207, 230, 0.1);
  }

  .btn-agregar {
    background: #00cfe6;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    margin-top: 16px;
    transition: background-color 0.2s;
  }

  .btn-agregar:hover {
    background: #00b8d4;
  }

  /* LISTA DE BLOQUES */
  .bloques-lista-section h3 {
    margin: 0 0 16px 0;
    font-size: 1.1rem;
    color: #1e293b;
    font-weight: 600;
  }

  .sin-bloques {
    text-align: center;
    padding: 40px;
    color: #64748b;
    background: #f8fafc;
    border: 1px dashed #e2e8f0;
    border-radius: 8px;
  }

  .sin-bloques-desc {
    font-size: 0.9rem;
    margin-top: 8px;
    color: #94a3b8;
  }

  .bloques-lista {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .bloque-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    transition: all 0.2s;
  }

  .bloque-item:hover {
    border-color: #cbd5e1;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .bloque-info {
    flex: 1;
  }

  .bloque-principal {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 8px;
  }

  .materia-curso {
    font-weight: 600;
    color: #1e293b;
    font-size: 0.95rem;
  }

  .bloque-horario {
    color: #475569;
    font-size: 0.9rem;
  }

  .bloque-observaciones {
    font-size: 0.85rem;
    color: #64748b;
    background: #f8fafc;
    padding: 6px 10px;
    border-radius: 4px;
    border-left: 3px solid #00cfe6;
  }

  .bloque-nuevo-indicator {
    font-size: 0.8rem;
    color: #059669;
    background: #d1fae5;
    padding: 4px 8px;
    border-radius: 4px;
    display: inline-block;
    margin-top: 6px;
  }

  .bloque-actions {
    display: flex;
    gap: 8px;
  }

  .btn-eliminar-bloque {
    background: none;
    border: none;
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
    color: #ef4444;
    transition: background-color 0.2s;
  }

  .btn-eliminar-bloque:hover:not(:disabled) {
    background: #fef2f2;
  }

  .btn-eliminar-bloque:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* BOTONES DE ACCIÓN */
  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 32px;
    padding-top: 20px;
    border-top: 1px solid #e2e8f0;
  }

  .btn-cancelar, .btn-guardar {
    padding: 12px 24px;
    border-radius: 6px;
    font-size: 0.9rem;
    cursor: pointer;
    border: none;
    font-weight: 500;
    transition: all 0.2s;
  }

  .btn-cancelar {
    background: #f8fafc;
    color: #64748b;
    border: 1.5px solid #e2e8f0;
  }

  .btn-cancelar:hover:not(:disabled) {
    background: #f1f5f9;
    border-color: #cbd5e1;
  }

  .btn-guardar {
    background: #00cfe6;
    color: white;
  }

  .btn-guardar:hover:not(:disabled) {
    background: #00b8d4;
    transform: translateY(-1px);
  }

  .btn-guardar:disabled {
    background: #cbd5e1;
    cursor: not-allowed;
    transform: none;
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

  /* RESPONSIVE */
  @media (max-width: 768px) {
    .modal-content {
      width: 95%;
      margin: 10px;
    }

    .modal-header {
      padding: 16px;
      flex-direction: column;
      gap: 12px;
    }

    .carga-horaria-content {
      padding: 16px;
    }

    .form-row {
      grid-template-columns: 1fr;
    }

    .bloque-item {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
    }

    .bloque-actions {
      justify-content: flex-end;
    }

    .resumen-dias {
      grid-template-columns: repeat(2, 1fr);
    }

    .modal-actions {
      flex-direction: column;
    }

    .btn-cancelar, .btn-guardar {
      width: 100%;
    }
  }

  @media (max-width: 480px) {
    .resumen-dias {
      grid-template-columns: 1fr;
    }

    .form-nuevo-bloque {
      padding: 16px;
    }
  }
</style>