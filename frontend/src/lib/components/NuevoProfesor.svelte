<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import AsignarCursos from "./AsignarCursos.svelte";
  export let profesorInit: any = null;

  const API_URL = 'http://localhost:8000/api/profesores';
 
  const dispatch = createEventDispatcher<{
    save: any;
    cancel: void;
  }>();

  let profesor: any = {
    id: null,
    id_persona: null,
    ci: "", nombres: "", apellido_paterno: "", apellido_materno: "",
    direccion: "", telefono: "", correo: "", tipo_persona: "profesor",
    estado_laboral: "activo"
  };

  let formErrors = {
    ci: false, nombres: false, apellido_paterno: false, correo: false
  };

  let profesorCreado: any = null;
  let asignacionesGuardadas: any[] = [];

  // --- nueva función para traer asignaciones desde backend y normalizarlas ---
  async function loadAsignaciones(incomingId: number | string) {
    try {
      const res = await fetch(`${API_URL}/${incomingId}/asignaciones`);
      if (!res.ok) {
        console.warn('No se pudo obtener asignaciones: ', res.status);
        return;
      }
      const data = await res.json();
      asignacionesGuardadas = (Array.isArray(data) ? data : []).map((a: any) => ({
        id: a.id ?? a.id_asignacion ?? a.id_profesor_materia ?? null,
        id_materia: a.id_materia ?? a.idMateria ?? a.materia_id ?? "",
        id_curso: a.id_curso ?? a.idCurso ?? a.curso_id ?? "",
        nombre_materia: a.nombre_materia ?? a.materia_nombre ?? a.materia ?? a.nombre ?? "",
        nombre_curso: a.nombre_curso ?? a.curso_nombre ?? a.curso ?? a.nombre_curso ?? ""
      }));
    } catch (err) {
      console.warn('Error al recuperar asignaciones del servidor:', err);
    }
  }

  // Cuando se recibe profesorInit desde el layout, precargar formulario.
  // Esto también permite abrir en modo "editar" con datos recuperados del servidor.
  $: if (profesorInit) {
    const incomingId = profesorInit.id ?? profesorInit.id_persona ?? null;
    const currentId = profesor.id ?? profesor.id_persona ?? null;
    if (incomingId !== currentId) {
      // Inicializar campos del formulario (como ya tienes)
      profesor = { 
        ci: profesorInit.ci ?? profesorInit.documento ?? profesor.ci ?? "",
        nombres: profesorInit.nombres ?? profesorInit.name ?? "",
        apellido_paterno: profesorInit.apellido_paterno ?? "",
        apellido_materno: profesorInit.apellido_materno ?? "",
        direccion: profesorInit.direccion ?? "",
        telefono: profesorInit.telefono ?? profesorInit.phone ?? "",
        correo: profesorInit.correo ?? profesorInit.email ?? profesorInit.email_address ?? "",
        tipo_persona: profesorInit.tipo_persona ?? "profesor",
        estado_laboral: profesorInit.estado_laboral ?? "activo",
        id: incomingId
      };

      // Si el backend ya manda materias/cursos en profesorInit, crear asignaciones temporales
      asignacionesGuardadas = [];
      if (Array.isArray(profesorInit.materias) || Array.isArray(profesorInit.cursos)) {
        const ms = profesorInit.materias ?? [];
        const cs = profesorInit.cursos ?? [];
        asignacionesGuardadas = ms.map((m: string, i: number) => ({
          id_materia: "", id_curso: "", nombre_materia: m, nombre_curso: cs[i] ?? ""
        }));
      }

      // cargar asignaciones reales desde la API (si existe id)
      if (incomingId) {
        loadAsignaciones(incomingId);
      }
    }
  } else {
    // si profesorInit es null (nuevo), asegurarse formulario limpio
    // evita sobrescribir si el usuario está editando (se ejecuta solo cuando profesorInit cambia a null)
    if (!profesor.id && profesor.nombres === "") {
      profesor = {
        ci: "", nombres: "", apellido_paterno: "", apellido_materno: "",
        direccion: "", telefono: "", correo: "", tipo_persona: "profesor",
        estado_laboral: "activo"
      };
      asignacionesGuardadas = [];
    }
  }

  function validarForm() {
    let isValid = true;
    formErrors = { ci: false, nombres: false, apellido_paterno: false, correo: false };

    if (!profesor.ci) { formErrors.ci = true; isValid = false; }
    if (!profesor.nombres) { formErrors.nombres = true; isValid = false; }
    if (!profesor.apellido_paterno) { formErrors.apellido_paterno = true; isValid = false; }
    if (!profesor.correo || !profesor.correo.includes('@')) { formErrors.correo = true; isValid = false; }

    return isValid;
  }

  async function guardarTodo() {
    if (!validarForm()) {
      alert('Por favor complete todos los campos requeridos correctamente');
      return;
    }

    try {
      // Determinar si es edición (tiene id) o creación
      const isEdit = Boolean(profesor.id || profesor.id_persona);
      const method = isEdit ? 'PUT' : 'POST';
      const url = isEdit ? `${API_URL}/${profesor.id ?? profesor.id_persona}` : API_URL;

      const resProf = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profesor)
      });

      if (!resProf.ok) throw new Error('Error al guardar profesor');
      profesorCreado = await resProf.json();

      // Guardar solo las asignaciones NUEVAS (sin id)
      const nuevas = asignacionesGuardadas.filter(a => !a.id);
      if (nuevas.length > 0) {
        const promesas = nuevas.map(asig =>
          fetch(`${API_URL}/asignaciones`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              id_profesor: Number(profesorCreado.id_persona || profesorCreado.id || profesor.id),
              id_curso: Number(asig.id_curso),
              id_materia: Number(asig.id_materia)
            })
          })
        );
        const resultados = await Promise.all(promesas);
        // reemplazar las nuevas entradas locales con las respuestas que incluyen id si vienen
        for (let i = 0; i < resultados.length; i++) {
          const r = resultados[i];
          if (!r.ok) {
            const err = await r.json().catch(()=>null);
            throw new Error(err?.detail || 'Error al guardar una asignación');
          } else {
            const created = await r.json().catch(()=>null);
            // intentar asociar el id devuelto con la entrada correspondiente (por materia+curso)
            const newAsig = nuevas[i];
            const idx = asignacionesGuardadas.findIndex(a => !a.id && a.id_materia == newAsig.id_materia && a.id_curso == newAsig.id_curso);
            if (idx !== -1) {
              asignacionesGuardadas[idx] = {
                id: created?.id ?? created?.id_asignacion ?? null,
                id_materia: created?.id_materia ?? newAsig.id_materia,
                id_curso: created?.id_curso ?? newAsig.id_curso,
                nombre_materia: created?.nombre_materia ?? newAsig.nombre_materia,
                nombre_curso: created?.nombre_curso ?? newAsig.nombre_curso
              };
            }
          }
        }
      }

      // Construir objeto para UI (asegurar que incluya id)
      const materiasUI = [...new Set(asignacionesGuardadas.map(a => (a.nombre_materia || a.materia || '').toString()).filter(Boolean))];
      const cursosUI = [...new Set(asignacionesGuardadas.map(a => (a.nombre_curso || a.curso || '').toString()).filter(Boolean))];

      const profesorParaUI = {
        ...profesorCreado,
        id: profesorCreado.id ?? profesorCreado.id_persona ?? profesor.id,
        nombres: profesorCreado.nombres || profesor.nombres,
        materias: materiasUI,
        cursos: cursosUI,
        estado_laboral: profesorCreado.estado_laboral || profesor.estado_laboral
      };

      alert('Profesor y asignaciones guardados exitosamente');
      dispatch('save', profesorParaUI);
    } catch (error: any) {
      alert('Error: ' + error.message);
    }
  }

  async function cancelar() {
    try {
      // Limpiar datos del formulario
      profesor = {
        ci: "", nombres: "", apellido_paterno: "", apellido_materno: "",
        direccion: "", telefono: "", correo: "", tipo_persona: "profesor",
        estado_laboral: "activo"
      };
      asignacionesGuardadas = [];
      formErrors = { ci: false, nombres: false, apellido_paterno: false, correo: false };
      
      // Notificar al servidor (opcional)
      await fetch(`${API_URL}/cancelar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      }).catch(() => {}); // Ignorar errores de red
      
      // Despachar evento al componente padre
      dispatch("cancel");
    } catch (error) {
      console.error('Error al cancelar:', error);
      dispatch("cancel");
    }
  }

  function onAsignado(e: CustomEvent) {
    const nuevaAsignacion = {
      id_materia: e.detail.id_materia,
      id_curso: e.detail.id_curso,
      // mantener nombres estándar que usa el padre
      nombre_materia: e.detail.nombre_materia || e.detail.materia,
      nombre_curso: e.detail.nombre_curso || e.detail.curso
    };

    // Evitar duplicados (misma materia+curso)
    const exists = asignacionesGuardadas.some(a => (a.id_materia == nuevaAsignacion.id_materia && a.id_curso == nuevaAsignacion.id_curso));
    if (!exists) {
      asignacionesGuardadas = [...asignacionesGuardadas, nuevaAsignacion];
    } else {
      // opcional: feedback
      // alert('Esa asignación ya fue agregada');
    }
  }

  // ajustar eliminarAsignacion para aceptar objeto o índice
  async function eliminarAsignacion(arg: number | { index?: number; id?: any }) {
    let index = -1;
    let id = null;

    if (typeof arg === 'number') {
      index = arg;
    } else {
      index = typeof arg.index === 'number' ? arg.index : -1;
      id = arg.id ?? null;
    }

    if (index === -1 && id == null) {
      // intentar buscar por id si nos pasaron solo id
      if (arg && typeof arg === 'object' && arg.id) {
        index = asignacionesGuardadas.findIndex(a => a.id == arg.id);
        id = arg.id;
      } else {
        return;
      }
    }

    const asig = asignacionesGuardadas[index];
    if (!asig) return;

    const asignacionId = id ?? asig.id ?? asig.id_asignacion ?? null;
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

    // quitar de la lista local (reactivo)
    asignacionesGuardadas = asignacionesGuardadas.filter((_, i) => i !== index);
  }
</script>

<div class="nuevo-profesor">
  <div class="header">
    <div class="icon-title">
      <div class="icon">👤</div>
      <div>
        <h2>Nuevo Profesor</h2>
        <p>Complete los datos y asigne materias en un solo paso</p>
      </div>
    </div>
    <div class="actions">
      <button class="btn-outline" on:click={cancelar}>Cancelar</button>
      <button class="btn-primary" on:click={guardarTodo}>
        Terminar
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
          <input type="text" bind:value={profesor.ci} placeholder="Ej: 1234567" class:error={formErrors.ci} />
          {#if formErrors.ci}<span class="error-message">El CI es requerido</span>{/if}
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
          <input type="text" bind:value={profesor.nombres} placeholder="Ej: Juan Carlos" class:error={formErrors.nombres} />
          {#if formErrors.nombres}<span class="error-message">Los nombres son requeridos</span>{/if}
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class:error={formErrors.apellido_paterno}>Apellido Paterno *</label>
          <input type="text" bind:value={profesor.apellido_paterno} placeholder="Ej: Pérez" class:error={formErrors.apellido_paterno} />
          {#if formErrors.apellido_paterno}<span class="error-message">El apellido paterno es requerido</span>{/if}
        </div>
        <div class="form-group">
          <label>Apellido Materno</label>
          <input type="text" bind:value={profesor.apellido_materno} placeholder="Ej: García" />
        </div>
      </div>
    </section>

    <!-- Información de Contacto -->
    <section>
      <h3>Información de Contacto</h3>
      <div class="form-row">
        <div class="form-group">
          <label class:error={formErrors.correo}>Correo Electrónico *</label>
          <input type="email" bind:value={profesor.correo} placeholder="profesor@escuela.edu" class:error={formErrors.correo} />
          {#if formErrors.correo}<span class="error-message">Ingrese un correo válido</span>{/if}
        </div>
        <div class="form-group">
          <label>Teléfono</label>
          <input type="tel" bind:value={profesor.telefono} placeholder="+591 789-0000" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label>Dirección</label>
          <input type="text" bind:value={profesor.direccion} placeholder="Av. Principal #123" />
        </div>
      </div>
    </section>

    <!-- ASIGNACIONES -->
    <section>
      <h3>Asignación de Materias y Cursos</h3>
      <p class="subtitle">Agregue todas las asignaciones antes de guardar</p>

      <div class="asignar-form">
        <AsignarCursos
          idProfesor={profesor.id ?? null}
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
    color: #1e293b; /* Color oscuro para el texto */
  }

  select option {
    color: #1e293b; /* Color oscuro para las opciones */
    background: #fff;
    padding: 8px;
  }

  /* Asegurarse que los textos en los selectores sean visibles */
  .form-group select {
    color: #1e293b;
    background: #fff;
  }

  /* Color para el placeholder de los select */
  select option[value=""] {
    color: #94a3b8;
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
  .form-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
  .subtitle {
    color: #64748b;
    font-size: 0.9rem;
    margin: -8px 0 16px;
  }
  .asignaciones-list {
    margin-top: 24px;
  }
  .asignaciones-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
    margin-top: 12px;
  }
  .asignacion-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 12px;
  }
  .asignacion-card .materia {
    font-weight: 500;
    color: #1e293b;
  }
  .asignacion-card .curso {
    color: #64748b;
    font-size: 0.875rem;
    margin-top: 4px;
  }
  h4 {
    font-size: 0.9rem;
    color: #1e293b;
    margin: 0 0 12px;
  }
  .btn-remove {
    width: 100%;
    margin-top: 8px;
    padding: 6px 8px;
    border: 1px solid #fecaca;
    background: #fee2e2;
    color: #dc2626;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.2s;
    font-weight: 500;
  }
  .btn-remove:hover {
    background: #fca5a5;
    border-color: #f87171;
  }
  .btn-remove:active {
    transform: scale(0.98);
  }
  @media (min-width: 640px) {
    .form-row:not(.single) {
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
    }
  }
  @media (max-width: 768px) {
    .nuevo-profesor {
      padding: 16px;
      max-height: 100vh;
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
    .icon-title {
      width: 100%;
    }
    h2 {
      font-size: 1.05rem;
    }
    section {
      padding: 14px;
    }
  }
  @media (max-width: 480px) {
    .actions {
      flex-direction: column-reverse;
      width: 100%;
    }
    .btn-outline, .btn-primary {
      width: 100%;
      padding: 10px 14px;
    }
    input, select {
      font-size: 16px;
    }
    .icon {
      width: 36px;
      height: 36px;
      font-size: 18px;
    }
  }
</style>