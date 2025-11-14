<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import AsignarCursos from "./AsignarCursos.svelte";

  interface Profesor {
    id?: number;
    id_persona?: number;
    ci: string;
    nombres: string;
    apellido_paterno: string;
    apellido_materno?: string;
    direccion?: string;
    telefono?: string;
    correo: string;
    tipo_persona?: string;
    estado_laboral?: string;
    materias?: string[];
    cursos?: string[];
  }

  export let profesor: any = null;

  const API_URL = "http://localhost:8000/api/profesores";
  const API_MATERIAS_URL = "http://localhost:8000/api/profesores/materias";

  const dispatch = createEventDispatcher<{
    save: any;
    cancel: void;
  }>();

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
    id: null as number | null
  };

  let formErrors = {
    ci: false,
    nombres: false,
    apellido_paterno: false,
    correo: false
  };

  let asignacionesGuardadas: any[] = [];
  let cargando = false;
  let errorMessage = "";
  let cargandoDatos = false;
  let materias: any[] = [];

  // Recuperar datos completos desde la API
  async function cargarProfesor(p: any) {
    cargandoDatos = true;
    errorMessage = "";

    try {
      if (!p) {
        formData = {
          ci: "", nombres: "", apellido_paterno: "", apellido_materno: "",
          direccion: "", telefono: "", correo: "", tipo_persona: "profesor",
          estado_laboral: "activo", id: null
        };
        asignacionesGuardadas = [];
        return;
      }

      const id = p.id ?? p.id_persona ?? null;
      console.log("Cargando profesor con ID:", id);

      if (id) {
        // Recuperar datos completos desde la API
        const res = await fetch(`${API_URL}/${id}`);
        console.log("Response status:", res.status);
        
        if (res.ok) {
          const data = await res.json();
          console.log("Datos obtenidos:", data);
          
          formData = {
            ci: data.ci ?? data.identificacion ?? data.documento ?? "",
            nombres: data.nombres ?? data.name ?? data.nombre ?? "",
            apellido_paterno: data.apellido_paterno ?? data.apellido1 ?? "",
            apellido_materno: data.apellido_materno ?? data.apellido2 ?? "",
            direccion: data.direccion ?? data.address ?? "",
            telefono: data.telefono ?? data.phone ?? "",
            correo: data.correo ?? data.email ?? data.email_address ?? "",
            tipo_persona: data.tipo_persona ?? "profesor",
            estado_laboral: data.estado_laboral ?? "activo",
            id: data.id ?? data.id_persona ?? id
          };

          // Cargar asignaciones
          if (Array.isArray(data.asignaciones) && data.asignaciones.length > 0) {
            asignacionesGuardadas = data.asignaciones.map((a: any) => ({
              id: a.id ?? null,
              id_materia: a.id_materia ?? "",
              id_curso: a.id_curso ?? "",
              nombre_materia: a.nombre_materia ?? a.materia ?? "",
              nombre_curso: a.nombre_curso ?? a.curso ?? ""
            }));
          } else {
            const materiasData = Array.isArray(data.materias) ? data.materias : [];
            const cursosData = Array.isArray(data.cursos) ? data.cursos : [];
            asignacionesGuardadas = materiasData.map((materia: string, index: number) => ({
              id: null,
              id_materia: "",
              id_curso: "",
              nombre_materia: materia,
              nombre_curso: cursosData[index] || ""
            }));
          }
          
          console.log("Profesor cargado exitosamente");
          cargandoDatos = false;
          return;
        } else {
          console.error("Error en API:", res.status, res.statusText);
          throw new Error(`Error: ${res.status} ${res.statusText}`);
        }
      }

      // Fallback: usar los datos que vienen en la prop
      console.log("Sin ID, usando datos locales");
      formData = {
        ci: p.ci ?? "",
        nombres: p.nombres ?? "",
        apellido_paterno: p.apellido_paterno ?? "",
        apellido_materno: p.apellido_materno ?? "",
        direccion: p.direccion ?? "",
        telefono: p.telefono ?? "",
        correo: p.correo ?? "",
        tipo_persona: p.tipo_persona ?? "profesor",
        estado_laboral: p.estado_laboral ?? "activo",
        id: p.id ?? p.id_persona ?? null
      };
      asignacionesGuardadas = [];
      if (Array.isArray(p.materias) && p.materias.length > 0) {
        const materiasData = p.materias;
        const cursosData = Array.isArray(p.cursos) ? p.cursos : [];
        asignacionesGuardadas = materiasData.map((materia: string, index: number) => ({
          id: null,
          id_materia: "",
          id_curso: "",
          nombre_materia: materia,
          nombre_curso: cursosData[index] || ""
        }));
      }
      
    } catch (err: any) {
      console.error("Error cargando profesor:", err);
      errorMessage = `Error: ${err.message}`;
      
      // Fallback a datos locales
      formData = {
        ci: p?.ci ?? "",
        nombres: p?.nombres ?? "",
        apellido_paterno: p?.apellido_paterno ?? "",
        apellido_materno: p?.apellido_materno ?? "",
        direccion: p?.direccion ?? "",
        telefono: p?.telefono ?? "",
        correo: p?.correo ?? "",
        tipo_persona: p?.tipo_persona ?? "profesor",
        estado_laboral: p?.estado_laboral ?? "activo",
        id: p?.id ?? p?.id_persona ?? null
      };
    } finally {
      cargandoDatos = false;
    }
  }

  // Llamada reactiva cuando cambie la prop `profesor`
  $: if (profesor !== undefined && profesor !== null) {
    cargarProfesor(profesor);
  }

  function validarForm() {
    let isValid = true;
    formErrors = { ci: false, nombres: false, apellido_paterno: false, correo: false };

    if (!formData.ci) { formErrors.ci = true; isValid = false; }
    if (!formData.nombres) { formErrors.nombres = true; isValid = false; }
    if (!formData.apellido_paterno) { formErrors.apellido_paterno = true; isValid = false; }
    if (!formData.correo || !formData.correo.includes('@')) { formErrors.correo = true; isValid = false; }

    return isValid;
  }

  async function guardarCambios() {
    if (!validarForm()) {
      errorMessage = 'Por favor complete todos los campos requeridos correctamente';
      return;
    }

    cargando = true;
    errorMessage = "";

    try {
      const method = 'PUT';
      const url = `${API_URL}/${formData.id}`;

      const resProf = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!resProf.ok) throw new Error('Error al guardar profesor');
      const profesorActualizado = await resProf.json();

      // Guardar solo las asignaciones NUEVAS (sin id)
      const nuevas = asignacionesGuardadas.filter(a => !a.id);
      if (nuevas.length > 0) {
        const promesas = nuevas.map(asig =>
          fetch(`${API_URL}/asignaciones`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              id_profesor: formData.id,
              id_curso: Number(asig.id_curso),
              id_materia: Number(asig.id_materia)
            })
          })
        );
        const resultados = await Promise.all(promesas);
        for (const r of resultados) {
          if (!r.ok) {
            const err = await r.json().catch(()=>null);
            throw new Error(err?.detail || 'Error al guardar una asignación');
          }
        }
      }

      // Construir objeto para UI
      const materiasUI = [...new Set(asignacionesGuardadas.map(a => (a.nombre_materia || a.materia || '').toString()).filter(Boolean))];
      const cursosUI = [...new Set(asignacionesGuardadas.map(a => (a.nombre_curso || a.curso || '').toString()).filter(Boolean))];

      const profesorParaUI = {
        ...profesorActualizado,
        id: profesorActualizado.id ?? profesorActualizado.id_persona ?? formData.id,
        nombres: profesorActualizado.nombres || formData.nombres,
        materias: materiasUI,
        cursos: cursosUI,
        estado_laboral: profesorActualizado.estado_laboral || formData.estado_laboral
      };

      errorMessage = 'Profesor actualizado exitosamente';
      dispatch('save', profesorParaUI);
    } catch (error: any) {
      errorMessage = 'Error: ' + error.message;
    } finally {
      cargando = false;
    }
  }

  function cancelar() {
    formData = {
      ci: "", nombres: "", apellido_paterno: "", apellido_materno: "",
      direccion: "", telefono: "", correo: "", tipo_persona: "profesor",
      estado_laboral: "activo", id: null
    };
    asignacionesGuardadas = [];
    formErrors = { ci: false, nombres: false, apellido_paterno: false, correo: false };
    errorMessage = "";
    dispatch("cancel");
  }

  function onAsignado(e: CustomEvent) {
    const nuevaAsignacion = {
      id_materia: e.detail.id_materia,
      id_curso: e.detail.id_curso,
      nombre_materia: e.detail.nombre_materia || e.detail.materia,
      nombre_curso: e.detail.nombre_curso || e.detail.curso
    };
    const exists = asignacionesGuardadas.some(a => (a.id_materia == nuevaAsignacion.id_materia && a.id_curso == nuevaAsignacion.id_curso));
    if (!exists) {
      asignacionesGuardadas = [...asignacionesGuardadas, nuevaAsignacion];
    }
  }

  async function eliminarAsignacion(index: number) {
    const asig = asignacionesGuardadas[index];
    if (!asig) return;

    const asignacionId = asig.id ?? asig.id_asignacion ?? null;
    if (asignacionId) {
      try {
        const res = await fetch(`${API_URL}/asignaciones/${asignacionId}`, {
          method: 'DELETE'
        });
        if (!res.ok) {
          const err = await res.json().catch(()=>null);
          throw new Error(err?.detail || 'Error al eliminar asignación en servidor');
        }
      } catch (err: any) {
        alert('No se pudo eliminar la asignación en el servidor: ' + (err?.message || err));
        return;
      }
    }
    asignacionesGuardadas = asignacionesGuardadas.filter((_, i) => i !== index);
  }

  onMount(async () => {
    try {
      const res = await fetch(API_MATERIAS_URL);
      if (res.ok) {
        materias = await res.json();
      } else {
        console.warn("No se pudieron cargar materias:", res.status);
      }
    } catch (err) {
      console.warn("Error cargando materias:", err);
    }
  });
</script>

<div class="editar-profesor">
  <div class="header">
    <div class="icon-title">
      <div class="icon">✏️</div>
      <div>
        <h2>Editar Profesor</h2>
        <p>Actualice los datos y asignaciones</p>
      </div>
    </div>
    <div class="actions">
      <button class="btn-outline" on:click={cancelar} disabled={cargando || cargandoDatos}>
        Cancelar
      </button>
      <button class="btn-primary" on:click={guardarCambios} disabled={cargando || cargandoDatos}>
        {cargando ? '⏳ Guardando...' : cargandoDatos ? '⏳ Cargando...' : 'Guardar Cambios'}
      </button>
    </div>
  </div>

  {#if cargandoDatos}
    <div class="alert">
      ⏳ Cargando datos del profesor...
    </div>
  {/if}

  {#if errorMessage}
    <div class="alert" class:success={errorMessage.includes('exitosamente')} class:error={!errorMessage.includes('exitosamente')}>
      {errorMessage}
    </div>
  {/if}

  <div class="form">
    <!-- Información Personal -->
    <section>
      <h3>Información Personal</h3>
      <div class="form-row single">
        <div class="form-group">
          <label class:error={formErrors.ci}>CI *</label>
          <input 
            type="text" 
            bind:value={formData.ci} 
            placeholder="Ej: 1234567" 
            class:error={formErrors.ci}
            disabled={cargando || cargandoDatos}
          />
          {#if formErrors.ci}<span class="error-message">El CI es requerido</span>{/if}
        </div>
        <div class="form-group">
          <label>Estado Laboral</label>
          <select bind:value={formData.estado_laboral} disabled={cargando || cargandoDatos}>
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class:error={formErrors.nombres}>Nombres *</label>
          <input 
            type="text" 
            bind:value={formData.nombres} 
            placeholder="Ej: Juan Carlos" 
            class:error={formErrors.nombres}
            disabled={cargando || cargandoDatos}
          />
          {#if formErrors.nombres}<span class="error-message">Los nombres son requeridos</span>{/if}
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class:error={formErrors.apellido_paterno}>Apellido Paterno *</label>
          <input 
            type="text" 
            bind:value={formData.apellido_paterno} 
            placeholder="Ej: Pérez" 
            class:error={formErrors.apellido_paterno}
            disabled={cargando || cargandoDatos}
          />
          {#if formErrors.apellido_paterno}<span class="error-message">El apellido paterno es requerido</span>{/if}
        </div>
        <div class="form-group">
          <label>Apellido Materno</label>
          <input 
            type="text" 
            bind:value={formData.apellido_materno} 
            placeholder="Ej: García"
            disabled={cargando || cargandoDatos}
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
            bind:value={formData.correo} 
            placeholder="profesor@escuela.edu" 
            class:error={formErrors.correo}
            disabled={cargando || cargandoDatos}
          />
          {#if formErrors.correo}<span class="error-message">Ingrese un correo válido</span>{/if}
        </div>
        <div class="form-group">
          <label>Teléfono</label>
          <input 
            type="tel" 
            bind:value={formData.telefono} 
            placeholder="+591 789-0000"
            disabled={cargando || cargandoDatos}
          />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Dirección</label>
          <input 
            type="text" 
            bind:value={formData.direccion} 
            placeholder="Av. Principal #123"
            disabled={cargando || cargandoDatos}
          />
        </div>
      </div>
    </section>

    <!-- Asignaciones -->
    <section>
      <h3>Asignación de Materias y Cursos</h3>
      <p class="subtitle">Agregue o modifique las asignaciones</p>

      <div class="asignar-form">
        <AsignarCursos
          idProfesor={formData.id}
          asignaciones={asignacionesGuardadas}
          materias={materias}
          on:asignado={onAsignado}
          on:remove={(e) => eliminarAsignacion(e.detail.index)}
        />
      </div>
    </section>
  </div>
</div>

<style>
  .editar-profesor {
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
    background: #fef3c7;
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

  .alert {
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 16px;
    font-size: 0.9rem;
  }

  .alert.success {
    background: #dcfce7;
    color: #166534;
    border: 1px solid #86efac;
  }

  .alert.error {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fca5a5;
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

  .btn-outline:hover:not(:disabled) {
    background: #f8fafc;
    border-color: #cbd5e1;
  }

  .btn-outline:disabled {
    opacity: 0.6;
    cursor: not-allowed;
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

  .btn-primary:hover:not(:disabled) {
    background: #00b8d4;
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
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
    transition: border-color 0.2s;
  }

  input:disabled, select:disabled {
    background: #f1f5f9;
    color: #94a3b8;
    cursor: not-allowed;
  }

  input:focus, select:focus {
    outline: none;
    border-color: #00cfe6;
    box-shadow: 0 0 0 3px rgba(0, 207, 230, 0.1);
  }

  input::placeholder {
    color: #94a3b8;
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

  .asignar-form {
    margin-bottom: 20px;
  }

  @media (min-width: 640px) {
    .form-row:not(.single) {
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
    }
  }

  @media (max-width: 768px) {
    .editar-profesor {
      padding: 16px;
    }
    .form-row,
    .form-row.single {
      grid-template-columns: 1fr;
      gap: 12px;
    }
    .header {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
    .actions {
      width: 100%;
      justify-content: flex-end;
    }
  }
</style>