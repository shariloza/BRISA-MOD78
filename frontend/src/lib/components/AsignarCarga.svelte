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

  const dispatch = createEventDispatcher<{
    guardar: void;
    cerrar: void;
  }>();

  // Estados
  let asignaciones: Asignacion[] = [];
  let bloquesHorarios: BloqueHorario[] = [];
  let bloquesEditando: BloqueHorario[] = [];
  let cargando = false;
  let guardando = false;
  let errorMessage = "";
  let gestionActual = "2025";

  // Nuevo bloque temporal
  let nuevoBloque: Partial<BloqueHorario> = {
    dia_semana: "lunes",
    hora_inicio: "08:00",
    hora_fin: "10:00",
    gestion: gestionActual,
    observaciones: ""
  };

  // Opciones disponibles
  const diasSemana = [
    { value: "lunes", label: "Lunes" },
    { value: "martes", label: "Martes" },
    { value: "miercoles", label: "Martes" },
    { value: "jueves", label: "Jueves" },
    { value: "viernes", label: "Viernes" },
  ];

  const horasDisponibles = [
    "07:00", "08:00", "09:00", "10:00", "11:00", "12:00",
    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"
  ];

  // Cargar datos del profesor
  async function cargarDatos() {
    if (!profesor?.id_persona) return;

    cargando = true;
    errorMessage = "";

    try {
      // Cargar asignaciones del profesor
      const resAsignaciones = await fetch(`${API_URL}/${profesor.id_persona}/asignaciones`);
      if (resAsignaciones.ok) {
        const data = await resAsignaciones.json();
        asignaciones = Array.isArray(data) ? data : [];
      }

      // Cargar bloques horarios existentes
      const resBloques = await fetch(`${API_URL}/${profesor.id_persona}/bloques?gestion=${gestionActual}`);
      if (resBloques.ok) {
        const data = await resBloques.json();
        bloquesHorarios = Array.isArray(data) ? data.map((b: any) => ({
          ...b,
          hora_inicio: b.hora_inicio?.substring(0, 5) || "08:00",
          hora_fin: b.hora_fin?.substring(0, 5) || "10:00"
        })) : [];
      }

      // Inicializar bloques en edición
      bloquesEditando = [...bloquesHorarios];

    } catch (err: any) {
      errorMessage = `Error al cargar datos: ${err.message}`;
    } finally {
      cargando = false;
    }
  }

  // Agregar nuevo bloque horario
  function agregarBloque() {
    if (!nuevoBloque.id_materia || !nuevoBloque.id_curso) {
      errorMessage = "Seleccione una materia y curso";
      return;
    }

    if (!nuevoBloque.hora_inicio || !nuevoBloque.hora_fin) {
      errorMessage = "Seleccione horario de inicio y fin";
      return;
    }

    // Validar que la hora de fin sea mayor que la de inicio
    const inicio = nuevoBloque.hora_inicio;
    const fin = nuevoBloque.hora_fin;
    if (fin <= inicio) {
      errorMessage = "La hora de fin debe ser mayor que la hora de inicio";
      return;
    }

    const asignacion = asignaciones.find(a => 
      a.id_materia === nuevoBloque.id_materia && a.id_curso === nuevoBloque.id_curso
    );

    if (!asignacion) {
      errorMessage = "Asignación no válida";
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
      dia_semana: "lunes",
      hora_inicio: "08:00",
      hora_fin: "10:00",
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

  // Guardar todos los cambios
  async function guardarCambios() {
    guardando = true;
    errorMessage = "";

    try {
      // Identificar bloques a eliminar (existen en DB pero no en edición)
      const bloquesAEliminar = bloquesHorarios.filter(bloqueDb => 
        !bloquesEditando.some(bloqueEdit => bloqueEdit.id_bloque === bloqueDb.id_bloque)
      );

      // Eliminar bloques
      for (const bloque of bloquesAEliminar) {
        if (bloque.id_bloque) {
          await fetch(`${API_URL}/bloques/${bloque.id_bloque}`, {
            method: "DELETE"
          });
        }
      }

      // Crear/actualizar bloques
      for (const bloque of bloquesEditando) {
        const bloqueData = {
          id_profesor: bloque.id_profesor,
          id_curso: bloque.id_curso,
          id_materia: bloque.id_materia,
          dia_semana: bloque.dia_semana,
          hora_inicio: bloque.hora_inicio + ":00",
          hora_fin: bloque.hora_fin + ":00",
          gestion: bloque.gestion,
          observaciones: bloque.observaciones || null
        };

        if (bloque.id_bloque) {
          // Actualizar bloque existente
          await fetch(`${API_URL}/bloques/${bloque.id_bloque}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(bloqueData)
          });
        } else {
          // Crear nuevo bloque
          await fetch(`${API_URL}/bloques`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(bloqueData)
          });
        }
      }

      errorMessage = "✅ Carga horaria guardada exitosamente";
      
      // Recargar datos
      setTimeout(() => {
        cargarDatos();
        dispatch("guardar");
      }, 1500);

    } catch (err: any) {
      errorMessage = `❌ Error al guardar: ${err.message}`;
    } finally {
      guardando = false;
    }
  }

  // Cerrar modal
  function cerrar() {
    dispatch("cerrar");
  }

  // Calcular duración en horas
  function calcularDuracion(horaInicio: string, horaFin: string): number {
    const [h1, m1] = horaInicio.split(':').map(Number);
    const [h2, m2] = horaFin.split(':').map(Number);
    return (h2 - h1) + (m2 - m1) / 60;
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
    cargarDatos();
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
      <div class="alert {errorMessage.includes('✅') ? 'alert-success' : 'alert-error'}">
        {errorMessage}
      </div>
    {/if}

    {#if cargando}
      <div class="alert alert-info">
        <span class="spinner"></span> Cargando datos...
      </div>
    {/if}

    <div class="carga-horaria-content">
      
      <!-- RESUMEN DE HORAS -->
      <div class="resumen-horas">
        <div class="resumen-item">
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
              <label>Materia y Curso</label>
              <select bind:value={nuevoBloque.id_materia}>
                <option value="">Seleccione materia y curso</option>
                {#each asignaciones as asignacion}
                  <option value={asignacion.id_materia} data-curso={asignacion.id_curso}>
                    {asignacion.nombre_materia} - {asignacion.nombre_curso}
                  </option>
                {/each}
              </select>
            </div>
            
            <div class="form-group">
              <label>Día de la Semana</label>
              <select bind:value={nuevoBloque.dia_semana}>
                {#each diasSemana as dia}
                  <option value={dia.value}>{dia.label}</option>
                {/each}
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Hora Inicio</label>
              <select bind:value={nuevoBloque.hora_inicio}>
                {#each horasDisponibles as hora}
                  <option value={hora}>{hora}</option>
                {/each}
              </select>
            </div>
            
            <div class="form-group">
              <label>Hora Fin</label>
              <select bind:value={nuevoBloque.hora_fin}>
                {#each horasDisponibles as hora}
                  <option value={hora}>{hora}</option>
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
            + Agregar Bloque
          </button>
        </div>
      </div>

      <!-- LISTA DE BLOQUES HORARIOS -->
      <div class="bloques-lista-section">
        <h3>Bloques Horarios Asignados ({bloquesEditando.length})</h3>
        
        {#if bloquesEditando.length === 0}
          <div class="sin-bloques">
            <p>No hay bloques horarios asignados</p>
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
                      {bloque.dia_semana} {bloque.hora_inicio} - {bloque.hora_fin} 
                      ({calcularDuracion(bloque.hora_inicio, bloque.hora_fin).toFixed(1)}h)
                    </span>
                  </div>
                  {#if bloque.observaciones}
                    <div class="bloque-observaciones">
                      {bloque.observaciones}
                    </div>
                  {/if}
                </div>
                
                <div class="bloque-controles">
                  <select 
                    value={bloque.dia_semana}
                    on:change={(e) => actualizarBloque(index, 'dia_semana', e.target.value)}
                  >
                    {#each diasSemana as dia}
                      <option value={dia.value}>{dia.label}</option>
                    {/each}
                  </select>
                  
                  <select 
                    value={bloque.hora_inicio}
                    on:change={(e) => actualizarBloque(index, 'hora_inicio', e.target.value)}
                  >
                    {#each horasDisponibles as hora}
                      <option value={hora}>{hora}</option>
                    {/each}
                  </select>
                  
                  <select 
                    value={bloque.hora_fin}
                    on:change={(e) => actualizarBloque(index, 'hora_fin', e.target.value)}
                  >
                    {#each horasDisponibles as hora}
                      <option value={hora}>{hora}</option>
                    {/each}
                  </select>
                  
                  <button 
                    class="btn-eliminar-bloque"
                    on:click={() => eliminarBloque(index)}
                    title="Eliminar bloque"
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
        <button 
          class="btn-guardar" 
          on:click={guardarCambios}
          disabled={guardando}
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
    max-width: 1000px;
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
    padding: 16px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    margin-bottom: 24px;
  }

  .resumen-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .resumen-label {
    font-weight: 600;
    color: #475569;
  }

  .resumen-value {
    font-weight: 700;
    font-size: 1.1rem;
    color: #1e293b;
  }

  .resumen-value.sobrecarga {
    color: #dc2626;
  }

  .resumen-dias {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 8px;
  }

  .dia-horas {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: #64748b;
  }

  /* FORMULARIO NUEVO BLOQUE */
  .nuevo-bloque-section {
    margin-bottom: 24px;
  }

  .nuevo-bloque-section h3 {
    margin: 0 0 16px 0;
    font-size: 1rem;
    color: #1e293b;
  }

  .form-nuevo-bloque {
    background: #fafbfc;
    padding: 20px;
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
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 0.9rem;
    background: white;
  }

  .btn-agregar {
    background: #00cfe6;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    margin-top: 8px;
  }

  .btn-agregar:hover {
    background: #00b8d4;
  }

  /* LISTA DE BLOQUES */
  .bloques-lista-section h3 {
    margin: 0 0 16px 0;
    font-size: 1rem;
    color: #1e293b;
  }

  .sin-bloques {
    text-align: center;
    padding: 40px;
    color: #64748b;
    background: #f8fafc;
    border: 1px dashed #e2e8f0;
    border-radius: 8px;
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
    transition: border-color 0.2s;
  }

  .bloque-item:hover {
    border-color: #cbd5e1;
  }

  .bloque-info {
    flex: 1;
  }

  .bloque-principal {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 8px;
  }

  .materia-curso {
    font-weight: 600;
    color: #1e293b;
  }

  .bloque-horario {
    color: #475569;
    font-size: 0.9rem;
  }

  .bloque-observaciones {
    font-size: 0.85rem;
    color: #64748b;
    font-style: italic;
  }

  .bloque-controles {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .bloque-controllers select {
    min-width: 100px;
  }

  .btn-eliminar-bloque {
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px;
    border-radius: 4px;
    color: #ef4444;
  }

  .btn-eliminar-bloque:hover {
    background: #fef2f2;
  }

  /* BOTONES DE ACCIÓN */
  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid #e2e8f0;
  }

  .btn-cancelar, .btn-guardar {
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 0.9rem;
    cursor: pointer;
    border: none;
    font-weight: 500;
  }

  .btn-cancelar {
    background: #f8fafc;
    color: #64748b;
    border: 1px solid #e2e8f0;
  }

  .btn-cancelar:hover:not(:disabled) {
    background: #f1f5f9;
  }

  .btn-guardar {
    background: #00cfe6;
    color: white;
  }

  .btn-guardar:hover:not(:disabled) {
    background: #00b8d4;
  }

  .btn-cancelar:disabled, .btn-guardar:disabled {
    opacity: 0.6;
    cursor: not-allowed;
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

    .bloque-controles {
      justify-content: space-between;
    }

    .resumen-dias {
      grid-template-columns: repeat(2, 1fr);
    }

    .modal-actions {
      flex-direction: column;
    }
  }

  @media (max-width: 480px) {
    .bloque-controles {
      flex-direction: column;
    }

    .resumen-dias {
      grid-template-columns: 1fr;
    }
  }
</style>