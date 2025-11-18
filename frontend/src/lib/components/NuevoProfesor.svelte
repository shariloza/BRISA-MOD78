<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import AsignarMaterias from "./AsignarMaterias.svelte";
  import AsignarCursos from "./AsignarCursos.svelte";
  import AsignarCarga from "./AsignarCarga.svelte";
  export let profesorInit: any = null;

  const API_URL = 'http://localhost:8000/api/profesores';
  const dispatch = createEventDispatcher();

  let profesor = {
    ci: "", nombres: "", apellido_paterno: "", apellido_materno: "", direccion: "", telefono: "", correo: "",
    tipo_persona: "profesor", estado_laboral: "activo", id_cargo: null, años_experiencia: 0,
    fecha_ingreso: new Date().toISOString().split('T')[0], especialidad: "", titulo_academico: "",
    nivel_enseñanza: "todos", observaciones_profesor: ""
  };

  let formData = {
    ci: "", nombres: "", apellido_paterno: "", apellido_materno: "", 
    direccion: "", telefono: "", correo: "",
    tipo_persona: "profesor", estado_laboral: "activo",
    id_persona: null as number | null, id_profesor: null as number | null,
    especialidad: "", titulo_academico: "", nivel_enseñanza: "todos", 
    observaciones_profesor: "",
    id_cargo: null as number | null
  };

  

  let formErrors = {};
  let profesorCreado: any = null;
  let asignacionesPendientes: any[] = [];
  let isEditMode = false;
  let profesorId: number | null = null;
  let cargos: any[] = [];

  // --- Bloques pendientes (para integración con AsignarCarga) ---
  let bloquesPendientesCrear: any[] = [];
  let bloquesPendientesActualizar: any[] = [];
  let bloquesPendientesEliminar: any[] = [];
  let hayCambiosPendientes = false;
  let errorMessage = "";

  // Estados para los modales de selección
  let mostrarModalMaterias = false;
  let mostrarModalCursos = false;
  let mostrarModalCarga = false;
  let materiaSeleccionada: any = null;
  let cursoSeleccionado: any = null;



    // === ASIGNACIONES ===
  
  let asignacionesGuardadas: any[] = [];
  let asignacionesParaEliminar: any[] = [];

  async function cargarAuxiliares() {
    try {
      const res = await fetch(`${API_URL}/cargos`);
      if (res.ok) cargos = await res.json();
    } catch (err) { console.error(err); }
  }

  $: if (profesorInit) {
    const id = profesorInit.id_persona || profesorInit.id_profesor;
    if (id && id !== profesorId) {
      isEditMode = true;
      profesorId = id;
      Object.assign(profesor, profesorInit);
    }
  }

  function resetForm() {
    profesor = { 
      ci: "", nombres: "", apellido_paterno: "", apellido_materno: "", direccion: "", telefono: "", correo: "", 
      tipo_persona: "profesor", estado_laboral: "activo", id_cargo: null, años_experiencia: 0, 
      fecha_ingreso: new Date().toISOString().split('T')[0], especialidad: "", titulo_academico: "", 
      nivel_enseñanza: "todos", observaciones_profesor: "" 
    };
    asignacionesPendientes = [];
    formErrors = {};
    isEditMode = false;
    profesorId = null;
    profesorCreado = null;
    materiaSeleccionada = null;
    cursoSeleccionado = null;
  }

  function validar() {
    const e = {};
    let ok = true;
    if (!profesor.ci?.trim()) { e['ci'] = true; ok = false; }
    if (!profesor.nombres?.trim()) { e['nombres'] = true; ok = false; }
    if (!profesor.apellido_paterno?.trim()) { e['apellido_paterno'] = true; ok = false; }
    if (!profesor.correo?.includes('@')) { e['correo'] = true; ok = false; }
    if (!profesor.especialidad?.trim()) { e['especialidad'] = true; ok = false; }
    if (!profesor.titulo_academico?.trim()) { e['titulo_academico'] = true; ok = false; }
    formErrors = e;
    return ok;
  }

  async function guardarTodo() {
    if (!validar()) return alert('Complete los campos requeridos');

    const data = { ...profesor, id_cargo: profesor.id_cargo ? Number(profesor.id_cargo) : null };
    const method = isEditMode ? 'PUT' : 'POST';
    const url = isEditMode ? `${API_URL}/${profesorId}` : API_URL;

    try {
      const res = await fetch(url, { 
        method, 
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify(data) 
      });
      
      if (!res.ok) throw new Error('Error al guardar profesor');
      
      profesorCreado = await res.json();
      const idProf = profesorCreado.id_profesor;

      // Guardar asignaciones pendientes
      if (asignacionesPendientes.length > 0) {
        await Promise.all(asignacionesPendientes.map(a => 
          fetch(`${API_URL}/asignaciones`, {
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              id_profesor: idProf, 
              id_materia: a.id_materia, 
              id_curso: a.id_curso 
            })
          })
        ));
      }

      // --- Persistir bloques pendientes (si los hay) ---
      // 1) Eliminar
      if (bloquesPendientesEliminar.length > 0) {
        for (const b of bloquesPendientesEliminar) {
          if (b.id_bloque) {
            await fetch(`${API_URL}/bloques/${b.id_bloque}`, { method: 'DELETE' });
          }
        }
      }
      
      // 2) Actualizar lOS BLOQUES
      if (bloquesPendientesActualizar.length > 0) {
        for (const b of bloquesPendientesActualizar) {
          const body = {
            id_profesor: idProf,
            id_curso: b.id_curso,
            id_materia: b.id_materia,
            dia_semana: b.dia_semana,
            hora_inicio: (b.hora_inicio && b.hora_inicio.split(':').length === 2) ? `${b.hora_inicio}:00` : b.hora_inicio,
            hora_fin: (b.hora_fin && b.hora_fin.split(':').length === 2) ? `${b.hora_fin}:00` : b.hora_fin,
            gestion: b.gestion || "2025",
            observaciones: b.observaciones || null
          };
          if (b.id_bloque) {
            await fetch(`${API_URL}/bloques/${b.id_bloque}`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(body)
            });
          }
        }
      }
      
      // 3) Crear
      if (bloquesPendientesCrear.length > 0) {
        for (const b of bloquesPendientesCrear) {
          const body = {
            id_profesor: idProf,
            id_curso: b.id_curso,
            id_materia: b.id_materia,
            dia_semana: b.dia_semana,
            hora_inicio: (b.hora_inicio && b.hora_inicio.split(':').length === 2) ? `${b.hora_inicio}:00` : b.hora_inicio,
            hora_fin: (b.hora_fin && b.hora_fin.split(':').length === 2) ? `${b.hora_fin}:00` : b.hora_fin,
            gestion: b.gestion || "2025",
            observaciones: b.observaciones || null
          };
          await fetch(`${API_URL}/bloques`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
          });
        }
      }

      // Limpiar colas de bloques
      bloquesPendientesCrear = [];
      bloquesPendientesActualizar = [];
      bloquesPendientesEliminar = [];
      hayCambiosPendientes = false;

      alert(`Profesor ${isEditMode ? 'actualizado' : 'creado'} exitosamente`);
      dispatch('save', { 
        ...profesorCreado, 
        asignaciones: asignacionesPendientes 
      });
      resetForm();
      
    } catch (err) {
      alert('Error: ' + err.message);
    }
  }

  // Función para abrir modal de materias
  function abrirModalMaterias() {
    mostrarModalMaterias = true;
  }

  // Función para abrir modal de cursos
  function abrirModalCursos() {
    if (!materiaSeleccionada) {
      alert("Primero seleccione una materia");
      return;
    }
    mostrarModalCursos = true;
  }

  // Abrir modal de carga — ahora también si hay asignaciones locales o guardadas aunque profesor no exista
  function abrirModalCarga() {
    const totalAsignaciones = (asignacionesGuardadas.length + asignacionesPendientes.length);
    // permitir abrir si ya existe el profesor o si hay asignaciones (locales o guardadas)
    if (!profesorCreado && totalAsignaciones === 0) {
      alert("Primero asigne al menos una materia/curso (local o desde BD) antes de gestionar la carga horaria.");
      return;
    }
    mostrarModalCarga = true;
  }

  // Cuando se selecciona una materia
  function onMateriaSeleccionada(event: CustomEvent) {
    materiaSeleccionada = event.detail.materia;
    mostrarModalMaterias = false;
    cursoSeleccionado = null; // Resetear curso cuando cambia la materia
  }

  // Cuando se selecciona un curso
  function onCursoSeleccionado(event: CustomEvent) {
    cursoSeleccionado = event.detail.curso;
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
      );

      if (!existe) {
        asignacionesPendientes = [...asignacionesPendientes, nuevaAsignacion];
        // Resetear selecciones
        materiaSeleccionada = null;
        cursoSeleccionado = null;
      } else {
        alert("Esta combinación ya está en la lista");
      }
    }
  }

  // Handler para cambios temporales del modal AsignarCarga
  function onGuardarCargaTemporal(e: CustomEvent) {
    const { bloques, eliminar } = e.detail;
    bloquesPendientesCrear = bloques.filter((b: any) => !b.id_bloque).map((b: any) => ({ ...b }));
    bloquesPendientesActualizar = bloques.filter((b: any) => b.id_bloque).map((b: any) => ({ ...b }));
    bloquesPendientesEliminar = eliminar || [];
    hayCambiosPendientes = true;
    mostrarModalCarga = false;
    errorMessage = "✅ Cambios de carga horaria preparados. Se guardarán al crear el profesor.";
  }

  // Eliminar asignación pendiente
  function eliminarAsignacion(index: number) {
    asignacionesPendientes = asignacionesPendientes.filter((_, i) => i !== index);
  }

  onMount(cargarAuxiliares);
</script>

<div class="nuevo-profesor-container">
  <div class="nuevo-profesor">
    <div class="header">
      <h2>{isEditMode ? 'Editar Profesor' : 'Nuevo Profesor'}</h2>
      <div class="actions">
        <button class="btn-outline" on:click={() => dispatch('cancel')}>Cancelar</button>
        <button class="btn-primary" on:click={guardarTodo}>
          {isEditMode ? 'Actualizar' : 'Guardar'}
        </button>
      </div>
    </div>

    <div class="form-content">
      <!-- Información Personal -->
      <section>
        <h3>Información Personal</h3>
        <div class="form-row single">
          <div class="form-group">
            <label class:error={formErrors.ci}>CI *</label>
            <input type="text" bind:value={profesor.ci} disabled={isEditMode} />
          </div>
          <div class="form-group">
            <label>Estado Laboral</label>
            <select bind:value={profesor.estado_laboral}>
              <option value="activo">Activo</option>
              <option value="inactivo">Inactivo</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class:error={formErrors.nombres}>Nombres *</label>
            <input type="text" bind:value={profesor.nombres} />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class:error={formErrors.apellido_paterno}>Apellido Paterno *</label>
            <input type="text" bind:value={profesor.apellido_paterno} />
          </div>
          <div class="form-group">
            <label>Apellido Materno</label>
            <input type="text" bind:value={profesor.apellido_materno} />
          </div>
        </div>
      </section>

      <!-- Contacto -->
      <section>
        <h3>Información de Contacto</h3>
        <div class="form-row">
          <div class="form-group">
            <label class:error={formErrors.correo}>Correo *</label>
            <input type="email" bind:value={profesor.correo} />
          </div>
          <div class="form-group">
            <label>Teléfono</label>
            <input type="tel" bind:value={profesor.telefono} />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Dirección</label>
            <input type="text" bind:value={profesor.direccion} />
          </div>
        </div>
      </section>

      <!-- Académicos -->
      <section>
        <h3>Datos Académicos</h3>
        <div class="form-row">
          <div class="form-group">
            <label class:error={formErrors.especialidad}>Especialidad *</label>
            <input type="text" bind:value={profesor.especialidad} />
          </div>
          <div class="form-group">
            <label class:error={formErrors.titulo_academico}>Título *</label>
            <input type="text" bind:value={profesor.titulo_academico} />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Nivel</label>
            <select bind:value={profesor.nivel_enseñanza}>
              <option value="todos">Todos</option>
              <option value="primary">Primaria</option>
              <option value="secondary">Secundaria</option>
            </select>
          </div>
          <div class="form-group">
            <label>Años Experiencia</label>
            <input type="number" bind:value={profesor.años_experiencia} min="0" />
          </div>
        </div>
      </section>

      <!-- Laborales -->
      <section>
        <h3>Datos Laborales</h3>
        <div class="form-row">
          <div class="form-group">
            <label>Cargo</label>
            <select bind:value={profesor.id_cargo}>
              <option value={null}>Ninguno</option>
              {#each cargos as c}
                <option value={c.id_cargo}>{c.nombre_cargo}</option>
              {/each}
            </select>
          </div>
          <div class="form-group">
            <label>Fecha Ingreso</label>
            <input type="date" bind:value={profesor.fecha_ingreso} />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Observaciones</label>
            <textarea bind:value={profesor.observaciones_profesor} rows="3"></textarea>
          </div>
        </div>
      </section>

      <!-- ASIGNACIÓN DE MATERIAS Y CURSOS -->
      <section>
        <h3>Asignación de Materias y Cursos</h3>
        
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

        <div style="display:flex; gap:12px; align-items:center; margin-bottom:12px;">
          <button 
            class="btn-carga-horaria" 
            on:click={abrirModalCarga} 
            disabled={!profesorCreado && (asignacionesGuardadas.concat(asignacionesPendientes).length === 0)}
          >
            📅 Asignar Carga Horaria
          </button>
          {#if !profesorCreado}
            <small style="color:#64748b;">
              (Disponible después de crear el profesor o si ya agregó al menos una materia/curso)
            </small>
          {/if}
        </div>

        <!-- Lista de asignaciones pendientes -->
        {#if asignacionesPendientes.length > 0}
          <div class="asignaciones-lista">
            <h4>Asignaciones Pendientes ({asignacionesPendientes.length})</h4>
            {#each asignacionesPendientes as asignacion, index}
              <div class="asignacion-item">
                <span class="materia">{asignacion.nombre_materia}</span>
                <span class="separador">-</span>
                <span class="curso">{asignacion.nombre_curso}</span>
                <button 
                  class="btn-eliminar" 
                  on:click={() => eliminarAsignacion(index)}
                >
                  ×
                </button>
              </div>
            {/each}
          </div>
        {:else}
          <div class="sin-asignaciones">
            No hay asignaciones pendientes
          </div>
        {/if}
      </section>
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
  profesor={profesorCreado || profesor}
  asignaciones={asignacionesGuardadas.concat(asignacionesPendientes)}
  autoSave={false}
  on:guardarTemporal={onGuardarCargaTemporal}
  on:cerrar={() => mostrarModalCarga = false}
/>


<style>
  /* CONTENEDOR PRINCIPAL CON SCROLL */
  .nuevo-profesor-container {
    width: 100%;
    height: 100vh;
    overflow-y: auto;
    background: #f8fafc;
  }

  .nuevo-profesor {
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    max-width: 900px;
    margin: 0 auto;
    min-height: fit-content;
  }

  /* CONTENEDOR DEL FORMULARIO CON SCROLL INTERNO */
  .form-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
    max-height: calc(100vh - 120px);
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
    padding-bottom: 12px;
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
  }

  h2 {
    margin: 0;
    font-size: 1.15rem;
    color: #1e293b;
  }

  .actions {
    display: flex;
    gap: 10px;
  }

  .btn-outline, .btn-primary {
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 0.9rem;
    cursor: pointer;
    border: 1px solid #e2e8f0;
  }

  .btn-outline {
    background: #fff;
    color: #64748b;
  }

  .btn-primary {
    background: #00cfe6;
    color: #fff;
    border-color: #00cfe6;
  }

  section {
    background: #fafbfc;
    padding: 18px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }

  section h3 {
    margin: 0 0 16px;
    font-size: 0.95rem;
    color: #1e293b;
    font-weight: 600;
  }

  .form-row {
    display: grid;
    gap: 16px;
    margin-bottom: 12px;
  }

  .form-row.single {
    grid-template-columns: 1fr 1fr;
  }

  .form-group {
    display: flex;
    flex-direction: column;
  }

  label {
    margin-bottom: 6px;
    font-size: 0.85rem;
    color: #475569;
    font-weight: 500;
  }

  input, select, textarea {
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 0.9rem;
    background: #aebcca;
    color: black;
  }

  input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: #00cfe6;
    box-shadow: 0 0 0 3px rgba(0,207,230,0.1);
  }

  .error {
    color: #dc2626;
  }

  input.error {
    border-color: #dc2626;
  }

  /* Estilos para los selectores */
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

  /* Estilos para la lista de asignaciones */
  .asignaciones-lista h4 {
    margin: 0 0 12px;
    font-size: 0.9rem;
    color: #475569;
  }

  .asignacion-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 12px;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    margin-bottom: 8px;
  }

  .materia {
    font-weight: 600;
    color: #1e293b;
  }

  .separador {
    color: #94a3b8;
  }

  .curso {
    color: #475569;
  }

  .btn-eliminar {
    background: #ef4444;
    color: white;
    border: none;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    cursor: pointer;
    margin-left: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
  }

  .sin-asignaciones {
    text-align: center;
    color: #94a3b8;
    font-style: italic;
    padding: 20px;
    background: #f8fafc;
    border: 1px dashed #e2e8f0;
    border-radius: 6px;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .nuevo-profesor-container {
      padding: 8px;
    }
    
    .nuevo-profesor {
      padding: 16px;
      border-radius: 8px;
    }

    .selectores-container {
      grid-template-columns: 1fr;
    }
    
    .form-row.single {
      grid-template-columns: 1fr;
    }
    
    .header {
      flex-direction: column;
      gap: 12px;
      align-items: stretch;
    }
    
    .actions {
      justify-content: stretch;
    }
    
    .btn-outline, .btn-primary {
      flex: 1;
    }

    .form-content {
      max-height: calc(100vh - 140px);
    }
  }

  @media (max-width: 480px) {
    .asignacion-item {
      flex-wrap: wrap;
    }
    
    .btn-eliminar {
      margin-left: 0;
      margin-top: 4px;
    }
  }

  .btn-carga-horaria {
    background: #0ea5e9;
    color: white;
    border: none;
    padding: 8px 12px;
    border-radius: 6px;
    cursor: pointer;
   }
   .btn-carga-horaria:disabled { background:#cbd5e1; cursor: not-allowed; }
</style>