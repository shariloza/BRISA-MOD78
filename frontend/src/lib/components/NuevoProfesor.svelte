<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import AsignarCursos from "./AsignarCursos.svelte";
  
  export let profesorInit: any = null;

  const API_URL = 'http://localhost:8000/api/profesores';
 
  const dispatch = createEventDispatcher<{
    save: any;
    cancel: void;
  }>();

  let profesor: any = {
    ci: "",
    nombres: "",
    apellido_paterno: "",
    apellido_materno: "",
    direccion: "",
    telefono: "",
    correo: "",
    tipo_persona: "profesor",
    estado_laboral: "activo",
    id_cargo: null
  };

  let formErrors = {
    ci: false,
    nombres: false,
    apellido_paterno: false,
    correo: false
  };

  let profesorCreado: any = null;
  let asignacionesGuardadas: any[] = [];
  let isEditMode = false;
  let profesorId: number | null = null;

  // Cargar asignaciones desde el backend
  async function loadAsignaciones(id: number) {
    try {
      const res = await fetch(`${API_URL}/${id}/asignaciones`);
      if (!res.ok) {
        console.warn('No se pudieron obtener asignaciones:', res.status);
        return;
      }
      const data = await res.json();
      asignacionesGuardadas = (Array.isArray(data) ? data : []).map((a: any) => ({
        id_profesor: a.id_profesor,
        id_curso: a.id_curso,
        id_materia: a.id_materia,
        nombre_materia: a.nombre_materia || "",
        nombre_curso: a.nombre_curso || ""
      }));
    } catch (err) {
      console.error('Error al cargar asignaciones:', err);
    }
  }

  // Manejar cambios en profesorInit (modo edición)
  $: if (profesorInit) {
    const incomingId = profesorInit.id_persona || profesorInit.id || null;
    
    if (incomingId && incomingId !== profesorId) {
      isEditMode = true;
      profesorId = incomingId;
      
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
        id_cargo: profesorInit.id_cargo || null
      };

      // Cargar asignaciones del backend
      loadAsignaciones(incomingId);
    }
  } else {
    // Modo crear nuevo
    if (isEditMode || profesorId) {
      resetForm();
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
      id_cargo: null
    };
    asignacionesGuardadas = [];
    formErrors = {
      ci: false,
      nombres: false,
      apellido_paterno: false,
      correo: false
    };
    isEditMode = false;
    profesorId = null;
    profesorCreado = null;
  }

  function validarForm() {
    let isValid = true;
    formErrors = {
      ci: false,
      nombres: false,
      apellido_paterno: false,
      correo: false
    };

    if (!profesor.ci || profesor.ci.trim() === "") {
      formErrors.ci = true;
      isValid = false;
    }
    if (!profesor.nombres || profesor.nombres.trim() === "") {
      formErrors.nombres = true;
      isValid = false;
    }
    if (!profesor.apellido_paterno || profesor.apellido_paterno.trim() === "") {
      formErrors.apellido_paterno = true;
      isValid = false;
    }
    if (!profesor.correo || !profesor.correo.includes('@')) {
      formErrors.correo = true;
      isValid = false;
    }

    return isValid;
  }

  async function guardarTodo() {
    if (!validarForm()) {
      alert('Por favor complete todos los campos requeridos correctamente');
      return;
    }

    try {
      // Preparar datos del profesor (sin campos extras)
      const profesorData = {
        ci: profesor.ci.trim(),
        nombres: profesor.nombres.trim(),
        apellido_paterno: profesor.apellido_paterno.trim(),
        apellido_materno: profesor.apellido_materno?.trim() || null,
        direccion: profesor.direccion?.trim() || null,
        telefono: profesor.telefono?.trim() || null,
        correo: profesor.correo.trim(),
        tipo_persona: profesor.tipo_persona,
        estado_laboral: profesor.estado_laboral,
        id_cargo: profesor.id_cargo
      };

      // Crear o actualizar profesor
      const method = isEditMode ? 'PUT' : 'POST';
      const url = isEditMode ? `${API_URL}/${profesorId}` : API_URL;

      const resProf = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profesorData)
      });

      if (!resProf.ok) {
        const errorData = await resProf.json().catch(() => null);
        throw new Error(errorData?.detail || `Error al ${isEditMode ? 'actualizar' : 'crear'} profesor`);
      }

      profesorCreado = await resProf.json();
      const idProfesor = profesorCreado.id_persona || profesorCreado.id;

      // Guardar solo asignaciones NUEVAS (sin los tres IDs completos)
      const nuevas = asignacionesGuardadas.filter(a => 
        !a.id_profesor || !a.id_curso || !a.id_materia
      );

      if (nuevas.length > 0) {
        const promesas = nuevas.map(asig =>
          fetch(`${API_URL}/asignaciones`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              id_profesor: Number(idProfesor),
              id_curso: Number(asig.id_curso),
              id_materia: Number(asig.id_materia)
            })
          })
        );

        const resultados = await Promise.all(promesas);
        
        for (let i = 0; i < resultados.length; i++) {
          const r = resultados[i];
          if (!r.ok) {
            const err = await r.json().catch(() => null);
            console.error('Error al guardar asignación:', err);
            // Continuar con las demás aunque una falle
          }
        }
      }

      // Construir objeto para la UI
      const materiasUI = [...new Set(
        asignacionesGuardadas
          .map(a => a.nombre_materia)
          .filter(Boolean)
      )];
      
      const cursosUI = [...new Set(
        asignacionesGuardadas
          .map(a => a.nombre_curso)
          .filter(Boolean)
      )];

      const profesorParaUI = {
        ...profesorCreado,
        materias: materiasUI,
        cursos: cursosUI
      };

      alert(`Profesor ${isEditMode ? 'actualizado' : 'creado'} exitosamente`);
      dispatch('save', profesorParaUI);
      resetForm();
    } catch (error: any) {
      console.error('Error completo:', error);
      alert('Error: ' + (error.message || 'Error desconocido'));
    }
  }

  function cancelar() {
    resetForm();
    dispatch("cancel");
  }

  function onAsignado(e: CustomEvent) {
    const nuevaAsignacion = {
      id_materia: e.detail.id_materia,
      id_curso: e.detail.id_curso,
      nombre_materia: e.detail.nombre_materia || e.detail.materia || "",
      nombre_curso: e.detail.nombre_curso || e.detail.curso || ""
    };

    // Evitar duplicados
    const exists = asignacionesGuardadas.some(a => 
      a.id_materia == nuevaAsignacion.id_materia && 
      a.id_curso == nuevaAsignacion.id_curso
    );
    
    if (!exists) {
      asignacionesGuardadas = [...asignacionesGuardadas, nuevaAsignacion];
    }
  }

  async function eliminarAsignacion(arg: any) {
    let index = -1;
    
    if (typeof arg === 'number') {
      index = arg;
    } else if (arg && typeof arg === 'object') {
      index = arg.index ?? -1;
    }

    if (index === -1 || index >= asignacionesGuardadas.length) {
      return;
    }

    const asig = asignacionesGuardadas[index];
    
    // Si tiene los tres IDs, es una asignación guardada en BD
    if (asig.id_profesor && asig.id_curso && asig.id_materia) {
      try {
        const url = `${API_URL}/asignaciones?id_profesor=${asig.id_profesor}&id_curso=${asig.id_curso}&id_materia=${asig.id_materia}`;
        const res = await fetch(url, { method: 'DELETE' });
        
        if (!res.ok) {
          const err = await res.json().catch(() => null);
          throw new Error(err?.detail || 'Error al eliminar asignación');
        }
      } catch (err: any) {
        alert('No se pudo eliminar la asignación: ' + (err.message || err));
        return;
      }
    }

    // Quitar de la lista local
    asignacionesGuardadas = asignacionesGuardadas.filter((_, i) => i !== index);
  }
</script>

<div class="nuevo-profesor">
  <div class="header">
    <div class="icon-title">
      <div class="icon">👤</div>
      <div>
        <h2>{isEditMode ? 'Editar Profesor' : 'Nuevo Profesor'}</h2>
        <p>Complete los datos y asigne materias en un solo paso</p>
      </div>
    </div>
    <div class="actions">
      <button class="btn-outline" on:click={cancelar}>Cancelar</button>
      <button class="btn-primary" on:click={guardarTodo}>
        {isEditMode ? 'Actualizar' : 'Guardar'}
      </button>
    </div>
  </div>

  <div class="form">
    <!-- Información Personal -->
    <section>
      <h3>Información Personal</h3>
      <div class="form-row single">
        <div class="form-group">
          <label class:error={formErrors.ci}>CI *</label>
          <input 
            type="text" 
            bind:value={profesor.ci} 
            placeholder="Ej: 1234567" 
            class:error={formErrors.ci}
            disabled={isEditMode}
          />
          {#if formErrors.ci}
            <span class="error-message">El CI es requerido</span>
          {/if}
        </div>
        <div class="form-group">
          <label>Estado Laboral</label>
          <select bind:value={profesor.estado_laboral}>
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
            <option value="retirado">Retirado</option>
            <option value="suspendido">Suspendido</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class:error={formErrors.nombres}>Nombres *</label>
          <input 
            type="text" 
            bind:value={profesor.nombres} 
            placeholder="Ej: Juan Carlos" 
            class:error={formErrors.nombres}
          />
          {#if formErrors.nombres}
            <span class="error-message">Los nombres son requeridos</span>
          {/if}
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class:error={formErrors.apellido_paterno}>Apellido Paterno *</label>
          <input 
            type="text" 
            bind:value={profesor.apellido_paterno} 
            placeholder="Ej: Pérez" 
            class:error={formErrors.apellido_paterno}
          />
          {#if formErrors.apellido_paterno}
            <span class="error-message">El apellido paterno es requerido</span>
          {/if}
        </div>
        <div class="form-group">
          <label>Apellido Materno</label>
          <input 
            type="text" 
            bind:value={profesor.apellido_materno} 
            placeholder="Ej: García"
          />
        </div>
      </div>
    </section>

    <!-- Información de Contacto -->
    <section>
      <h3>Información de Contacto</h3>
      <div class="form-row">
        <div class="form-group">
          <label class:error={formErrors.correo}>Correo Electrónico *</label>
          <input 
            type="email" 
            bind:value={profesor.correo} 
            placeholder="profesor@escuela.edu" 
            class:error={formErrors.correo}
          />
          {#if formErrors.correo}
            <span class="error-message">Ingrese un correo válido</span>
          {/if}
        </div>
        <div class="form-group">
          <label>Teléfono</label>
          <input 
            type="tel" 
            bind:value={profesor.telefono} 
            placeholder="+591 789-0000"
          />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Dirección</label>
          <input 
            type="text" 
            bind:value={profesor.direccion} 
            placeholder="Av. Principal #123"
          />
        </div>
      </div>
    </section>

    <!-- ASIGNACIONES -->
    <section>
      <h3>Asignación de Materias y Cursos</h3>
      <p class="subtitle">Agregue todas las asignaciones antes de guardar</p>

      <div class="asignar-form">
        <AsignarCursos
          idProfesor={profesorId}
          asignaciones={asignacionesGuardadas}
          on:asignado={onAsignado}
          on:remove={(e) => eliminarAsignacion(e.detail)}
        />
      </div>
    </section>
  </div>
</div>

<style>
  .nuevo-profesor {
    background: #fff;
    border-radius: 12px;
    padding: 24px 32px;
    width: calc(100% - 64px);
    height: calc(100vh - 48px);
    margin: 24px auto;
    box-sizing: border-box;
    overflow-y: auto;
    position: relative;
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e2e8f0;
  }
  .icon-title {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .icon {
    width: 40px;
    height: 40px;
    background: #e6f7fa;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
  }
  h2 {
    margin: 0;
    font-size: 1.15rem;
    color: #1e293b;
  }
  h2 + p {
    margin: 2px 0 0;
    color: #64748b;
    font-size: 0.85rem;
  }
  .actions {
    display: flex;
    gap: 10px;
    flex-shrink: 0;
  }
  .btn-outline {
    padding: 8px 16px;
    border: 1px solid #e2e8f0;
    background: #fff;
    border-radius: 6px;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
  }
  .btn-outline:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
  }
  .btn-primary {
    padding: 8px 16px;
    background: #00cfe6;
    border: none;
    border-radius: 6px;
    color: #fff;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
  }
  .btn-primary:hover {
    background: #00b8d4;
  }
  .form {
    display: flex;
    flex-direction: column;
    gap: 20px;
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
    grid-template-columns: 1fr;
    gap: 16px;
    margin-bottom: 12px;
  }
  .form-row.single {
    grid-template-columns: 1fr 1fr;
  }
  .form-row:last-child {
    margin-bottom: 0;
  }
  .form-group {
    display: flex;
    flex-direction: column;
  }
  label {
    display: block;
    margin-bottom: 6px;
    font-size: 0.85rem;
    color: #475569;
    font-weight: 500;
  }
  input, select {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 0.9rem;
    background: #fff;
    color: #1e293b;
  }
  input:disabled {
    background: #f1f5f9;
    color: #94a3b8;
    cursor: not-allowed;
  }
  select option {
    color: #1e293b;
    background: #fff;
    padding: 8px;
  }
  input:focus, select:focus {
    outline: none;
    border-color: #00cfe6;
    box-shadow: 0 0 0 3px rgba(0, 207, 230, 0.1);
  }
  input::placeholder {
    color: #94a3b8;
  }
  select {
    cursor: pointer;
  }
  .error {
    color: #dc2626;
  }
  input.error {
    border-color: #dc2626;
  }
  .error-message {
    color: #dc2626;
    font-size: 0.8rem;
    margin-top: 4px;
  }
  .subtitle {
    color: #64748b;
    font-size: 0.9rem;
    margin: -8px 0 16px;
  }
  @media (min-width: 640px) {
    .form-row:not(.single) {
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
    }
  }
</style>