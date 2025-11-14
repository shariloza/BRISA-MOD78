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
  const API_CURSOS_URL = "http://localhost:8000/api/profesores/cursos";

  const dispatch = createEventDispatcher<{
    save: any;
    cancel: void;
    delete: { id: number };
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
    id: null as number | null,
  };

  let formErrors = {
    ci: false,
    nombres: false,
    apellido_paterno: false,
    correo: false,
  };

  let asignacionesGuardadas: any[] = [];
  let asignacionesParaEliminar: any[] = [];
  let cargando = false;
  let eliminando = false;
  let errorMessage = "";
  let cargandoDatos = false;
  let materias: any[] = [];
  let cursos: any[] = [];
  let todasAsignaciones: any[] = [];
  let hayCambiosPendientes = false;

  async function cargarDatosAuxiliares() {
    try {
      const [resMat, resCur, resAsig] = await Promise.all([
        fetch(API_MATERIAS_URL),
        fetch(API_CURSOS_URL),
        fetch(`${API_URL}/asignaciones`),
      ]);

      if (resMat.ok) materias = await resMat.json();
      if (resCur.ok) cursos = await resCur.json();
      if (resAsig.ok) todasAsignaciones = await resAsig.json();
    } catch (err) {
      console.warn("Error cargando datos auxiliares", err);
    }
  }

  async function cargarProfesor(p: any) {
    cargandoDatos = true;
    errorMessage = "";

    try {
      if (!p) {
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
          id: null,
        };
        asignacionesGuardadas = [];
        asignacionesParaEliminar = [];
        hayCambiosPendientes = false;
        return;
      }

      const id = p.id ?? p.id_persona ?? null;
      if (!id) {
        formData = { ...formData, ...p, id: null };
        asignacionesGuardadas = [];
        asignacionesParaEliminar = [];
        hayCambiosPendientes = false;
        return;
      }

      const resProf = await fetch(`${API_URL}/${id}?completo=false`);
      if (!resProf.ok) throw new Error("No se pudo cargar el profesor");

      const dataProf = await resProf.json();

      formData = {
        ci: dataProf.ci ?? "",
        nombres: dataProf.nombres ?? "",
        apellido_paterno: dataProf.apellido_paterno ?? "",
        apellido_materno: dataProf.apellido_materno ?? "",
        direccion: dataProf.direccion ?? "",
        telefono: dataProf.telefono ?? "",
        correo: dataProf.correo ?? "",
        tipo_persona: dataProf.tipo_persona ?? "profesor",
        estado_laboral: dataProf.estado_laboral ?? "activo",
        id: dataProf.id ?? dataProf.id_persona ?? id,
      };

      const asignacionesDelProfesor = todasAsignaciones.filter(
        (a) => a.id_profesor === id,
      );

      asignacionesGuardadas = asignacionesDelProfesor.map((asig) => {
        const materia = materias.find((m) => m.id_materia === asig.id_materia);
        const curso = cursos.find((c) => c.id_curso === asig.id_curso);

        return {
          existeEnBD: true,
          id_materia: asig.id_materia,
          id_curso: asig.id_curso,
          nombre_materia:
            materia?.nombre_materia ?? `Materia ${asig.id_materia}`,
          nombre_curso: curso?.nombre_curso ?? `Curso ${asig.id_curso}`,
        };
      });

      asignacionesParaEliminar = [];
      hayCambiosPendientes = false;
    } catch (err: any) {
      errorMessage = `Error: ${err.message}`;
      console.error(err);
    } finally {
      cargandoDatos = false;
    }
  }

  $: if (profesor !== undefined && profesor !== null) {
    cargarProfesor(profesor);
  }

  function validarForm() {
    let isValid = true;
    formErrors = {
      ci: false,
      nombres: false,
      apellido_paterno: false,
      correo: false,
    };

    if (!formData.ci) {
      formErrors.ci = true;
      isValid = false;
    }
    if (!formData.nombres) {
      formErrors.nombres = true;
      isValid = false;
    }
    if (!formData.apellido_paterno) {
      formErrors.apellido_paterno = true;
      isValid = false;
    }
    if (!formData.correo || !formData.correo.includes("@")) {
      formErrors.correo = true;
      isValid = false;
    }

    return isValid;
  }

  async function guardarCambios() {
    if (!validarForm()) {
      errorMessage =
        "Por favor complete todos los campos requeridos correctamente";
      return;
    }

    cargando = true;
    errorMessage = "";

    try {
      const method = "PUT";
      const url = `${API_URL}/${formData.id}`;

      const resProf = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!resProf.ok) throw new Error("Error al guardar profesor");
      const profesorActualizado = await resProf.json();

      // Eliminar asignaciones marcadas
      if (asignacionesParaEliminar.length > 0) {
        const promesasEliminar = asignacionesParaEliminar.map((asig) => {
          const url = new URL(`${API_URL}/asignaciones`);
          url.searchParams.append("id_profesor", String(formData.id));
          url.searchParams.append("id_curso", String(asig.id_curso));
          url.searchParams.append("id_materia", String(asig.id_materia));
          return fetch(url, { method: "DELETE" });
        });

        const resultadosEliminar = await Promise.all(promesasEliminar);
        for (const r of resultadosEliminar) {
          if (!r.ok) {
            const err = await r.json().catch(() => null);
            throw new Error(err?.detail || "Error al eliminar una asignación");
          }
        }
      }

      // Guardar solo las asignaciones NUEVAS
      const nuevas = asignacionesGuardadas.filter((a) => !a.existeEnBD);
      if (nuevas.length > 0) {
        const promesas = nuevas.map((asig) =>
          fetch(`${API_URL}/asignaciones`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              id_profesor: formData.id,
              id_curso: Number(asig.id_curso),
              id_materia: Number(asig.id_materia),
            }),
          }),
        );
        const resultados = await Promise.all(promesas);
        for (const r of resultados) {
          if (!r.ok) {
            const err = await r.json().catch(() => null);
            throw new Error(err?.detail || "Error al guardar una asignación");
          }
        }
      }

      const materiasUI = [
        ...new Set(
          asignacionesGuardadas
            .map((a) => (a.nombre_materia || "").toString())
            .filter(Boolean),
        ),
      ];
      const cursosUI = [
        ...new Set(
          asignacionesGuardadas
            .map((a) => (a.nombre_curso || "").toString())
            .filter(Boolean),
        ),
      ];

      const profesorParaUI = {
        ...profesorActualizado,
        id:
          profesorActualizado.id ??
          profesorActualizado.id_persona ??
          formData.id,
        nombres: profesorActualizado.nombres || formData.nombres,
        materias: materiasUI,
        cursos: cursosUI,
        estado_laboral:
          profesorActualizado.estado_laboral || formData.estado_laboral,
      };

      asignacionesParaEliminar = [];
      hayCambiosPendientes = false;
      errorMessage = "✓ Profesor actualizado exitosamente";
      
      setTimeout(() => {
        dispatch("save", profesorParaUI);
      }, 1500);
    } catch (error: any) {
      errorMessage = "✗ Error: " + error.message;
    } finally {
      cargando = false;
    }
  }

  async function eliminarProfesor() {
    if (!formData?.id) return;
    const confirmar = confirm("¿Confirma que desea eliminar este profesor de la base de datos? Esta acción no se puede deshacer.");
    if (!confirmar) return;
    eliminando = true;
    errorMessage = "";
    try {
      const res = await fetch(`${API_URL}/${formData.id}`, { method: "DELETE" });
      if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(err?.detail || `Error al eliminar (status ${res.status})`);
      }
      errorMessage = "✓ Profesor eliminado correctamente";
      // Notificar a quien usa el componente
      dispatch("delete", { id: formData.id });
      // Opcional: cerrar el formulario después de un momento
      setTimeout(() => dispatch("cancel"), 700);
    } catch (err: any) {
      errorMessage = "✗ Error al eliminar: " + (err?.message || err);
      console.error(err);
    } finally {
      eliminando = false;
    }
  }

  function cancelar() {
    if (hayCambiosPendientes) {
      const confirmar = confirm(
        "Hay cambios sin guardar. ¿Está seguro que desea cancelar?",
      );
      if (!confirmar) return;
    }

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
      id: null,
    };
    asignacionesGuardadas = [];
    asignacionesParaEliminar = [];
    formErrors = {
      ci: false,
      nombres: false,
      apellido_paterno: false,
      correo: false,
    };
    errorMessage = "";
    hayCambiosPendientes = false;
    dispatch("cancel");
  }

  function onAsignado(e: CustomEvent) {
    const nuevaAsignacion = {
      existeEnBD: false,
      id_materia: e.detail.id_materia,
      id_curso: e.detail.id_curso,
      nombre_materia: e.detail.nombre_materia || e.detail.materia,
      nombre_curso: e.detail.nombre_curso || e.detail.curso,
    };
    const exists = asignacionesGuardadas.some(
      (a) =>
        a.id_materia == nuevaAsignacion.id_materia &&
        a.id_curso == nuevaAsignacion.id_curso,
    );
    if (!exists) {
      asignacionesGuardadas = [...asignacionesGuardadas, nuevaAsignacion];
      hayCambiosPendientes = true;
    }
  }

  function marcarParaEliminar(index: number) {
    const asig = asignacionesGuardadas[index];
    if (!asig) return;

    // Si existe en BD, agregar a lista de eliminación
    if (asig.existeEnBD) {
      asignacionesParaEliminar = [...asignacionesParaEliminar, asig];
    }

    // Eliminar de la lista local
    asignacionesGuardadas = asignacionesGuardadas.filter((_, i) => i !== index);
    hayCambiosPendientes = true;
  }

  function restaurarAsignacion(index: number) {
    const asig = asignacionesParaEliminar[index];
    if (!asig) return;

    // Restaurar a la lista de asignaciones
    asignacionesGuardadas = [...asignacionesGuardadas, asig];
    
    // Quitar de la lista de eliminación
    asignacionesParaEliminar = asignacionesParaEliminar.filter(
      (_, i) => i !== index,
    );
    
    hayCambiosPendientes = asignacionesParaEliminar.length > 0 || 
      asignacionesGuardadas.some(a => !a.existeEnBD);
  }

  onMount(async () => {
    await cargarDatosAuxiliares();
    if (profesor) {
      cargarProfesor(profesor);
    }
  });
</script>

<div class="editar-profesor">
  <div class="header">
    <div class="icon-title">
      <div class="icon">✏️</div>
      <div>
        <h2>Editar Profesor</h2>
        <p>Actualice los datos y asignaciones del profesor</p>
      </div>
    </div>
    <div class="actions">
      <button
        class="btn-outline"
        on:click={cancelar}
        disabled={cargando || cargandoDatos}
      >
        Cancelar
      </button>
      <button
        class="btn-primary"
        on:click={guardarCambios}
        disabled={cargando || cargandoDatos}
      >
        {#if cargando}
          <span class="spinner"></span>
          Guardando...
        {:else if cargandoDatos}
          <span class="spinner"></span>
          Cargando...
        {:else}
          💾 Guardar Cambios
        {/if}
      </button>
    </div>
  </div>

  {#if hayCambiosPendientes}
    <div class="alert alert-warning">
      ⚠️ Hay cambios pendientes sin guardar. Haga clic en "Guardar Cambios" para
      aplicar los cambios.
    </div>
  {/if}

  {#if cargandoDatos}
    <div class="alert alert-info">
      <span class="spinner"></span>
      Cargando datos del profesor...
    </div>
  {/if}

  {#if errorMessage}
    <div
      class="alert"
      class:alert-success={errorMessage.includes("exitosamente")}
      class:alert-error={!errorMessage.includes("exitosamente")}
    >
      {errorMessage}
    </div>
  {/if}

  <div class="form">
    <section>
      <h3>📋 Información Personal</h3>
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
          {#if formErrors.ci}
            <span class="error-message">El CI es requerido</span>
          {/if}
        </div>
        <div class="form-group">
          <label>Estado Laboral</label>
          <select
            bind:value={formData.estado_laboral}
            disabled={cargando || cargandoDatos}
          >
            <option value="activo">✓ Activo</option>
            <option value="inactivo">✗ Inactivo</option>
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
          {#if formErrors.nombres}
            <span class="error-message">Los nombres son requeridos</span>
          {/if}
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class:error={formErrors.apellido_paterno}
            >Apellido Paterno *</label
          >
          <input
            type="text"
            bind:value={formData.apellido_paterno}
            placeholder="Ej: Pérez"
            class:error={formErrors.apellido_paterno}
            disabled={cargando || cargandoDatos}
          />
          {#if formErrors.apellido_paterno}
            <span class="error-message">El apellido paterno es requerido</span>
          {/if}
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

    <section>
      <h3>📞 Información de Contacto</h3>
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
          {#if formErrors.correo}
            <span class="error-message">Ingrese un correo válido</span>
          {/if}
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

    <section>
      <h3>📚 Asignación de Materias y Cursos</h3>
      <p class="subtitle">Gestione las materias y cursos del profesor</p>

      <div class="asignar-form">
        <AsignarCursos
          idProfesor={formData.id}
          asignaciones={asignacionesGuardadas}
          {materias}
          on:asignado={onAsignado}
          on:remove={(e) => marcarParaEliminar(e.detail.index)}
        />
      </div>

      {#if asignacionesParaEliminar.length > 0}
        <div class="eliminadas-section">
          <h4>
            🗑️ Asignaciones marcadas para eliminar ({asignacionesParaEliminar.length})
          </h4>
          <p class="subtitle-small">
            Estas asignaciones se eliminarán al guardar los cambios
          </p>
          <div class="eliminadas-list">
            {#each asignacionesParaEliminar as asig, index}
              <div class="asignacion-eliminada">
                <div class="asignacion-info">
                  <span class="materia-badge">{asig.nombre_materia}</span>
                  <span class="curso-badge">{asig.nombre_curso}</span>
                </div>
                <button
                  class="btn-restaurar"
                  on:click={() => restaurarAsignacion(index)}
                  title="Restaurar asignación"
                >
                  ↺ Restaurar
                </button>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </section>
  </div>

  <!-- Botón para eliminar profesor al final de la pantalla -->
  {#if formData?.id}
    <div class="footer-delete" style="margin-top:18px;">
      <button
        class="btn-delete"
        on:click={eliminarProfesor}
        disabled={cargando || cargandoDatos || eliminando}
        title="Eliminar profesor"
      >
        {#if eliminando}
          <span class="spinner"></span> Eliminando...
        {:else}
          🗑️ Eliminar Profesor
        {/if}
      </button>
    </div>
  {/if}
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

  input,
  select {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 0.9rem;
    background: #fff;
    color: #1e293b;
    transition: border-color 0.2s;
  }

  input:disabled,
  select:disabled {
    background: #f1f5f9;
    color: #94a3b8;
    cursor: not-allowed;
  }

  input:focus,
  select:focus {
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

  .footer-delete {
    display: flex;
    justify-content: center;
    margin-bottom: 24px;
  }

  .btn-delete {
    background: #ef4444;
    color: #fff;
    border: none;
    padding: 10px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    box-shadow: 0 1px 2px rgba(0,0,0,0.06);
    transition: transform 0.12s, background 0.12s;
  }

  .btn-delete:hover:not(:disabled) {
    background: #dc2626;
    transform: translateY(-2px);
  }

  .btn-delete:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
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

/* === SECCIÓN: ASIGNACIONES MARCADAS PARA ELIMINAR (ESTILO BRISA) === */
.eliminadas-section {
  background: #ecfdf5; /* Verde muy claro (coherente con éxito) */
  border: 1px solid #6ee7b4; /* Borde verde cian */
  border-radius: 8px;
  padding: 16px;
  margin-top: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.eliminadas-section h4 {
  margin: 0 0 8px;
  font-size: 0.95rem;
  color: #0f766e; /* Verde oscuro (como éxito) */
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.subtitle-small {
  color: #0f766e;
  font-size: 0.85rem;
  margin: -4px 0 12px;
  font-style: italic;
}

.eliminadas-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.asignacion-eliminada {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f0fdf4; /* Verde más claro */
  padding: 10px 12px;
  border-radius: 6px;
  border-left: 4px solid #10b981; /* Línea lateral verde */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.asignacion-info {
  display: flex;
  gap: 12px;
  align-items: center;
  flex: 1;
}

.materia-badge,
.curso-badge {
  background: #10b981; /* Verde esmeralda */
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

.curso-badge {
  background: #059669; /* Verde más oscuro */
}

.btn-restaurar {
  background: #00cfe6; /* TU COLOR PRINCIPAL */
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
  font-weight: 500;
}

.btn-restaurar:hover {
  background: #00b8d4;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 207, 230, 0.2);
}

.btn-restaurar:active {
  transform: translateY(0);
}

/* Alertas coherentes con BRISA */
.alert-warning {
  background: #ecfdf5;
  color: #0f766e;
  border: 1px solid #6ee7b4;
}

.alert-info {
  background: #dbeafe;
  color: #1e40af;
  border: 1px solid #93c5fd;
}

.alert-success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #86efac;
}

.alert-error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

/* Spinner para botones */
.spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid #ffffff40;
  border-top: 2px solid #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 6px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
