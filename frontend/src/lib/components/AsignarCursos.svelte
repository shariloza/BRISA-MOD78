<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let idProfesor: number | null = null;
  export let asignaciones: any[] = []; // la lista viene del padre
  export let materias: any[] | null = null; // si el padre pasa materias, usar esas
  const API_URL = "http://localhost:8000/api/profesores";
  const dispatch = createEventDispatcher();

  let cursos = [];
  let asignacion = { id_curso: "", id_materia: "" };

  async function cargarDatos() {
    try {
      // cargar cursos siempre (no lo pasa el padre)
      const resCursos = await fetch(`${API_URL}/cursos`);
      cursos = resCursos.ok ? await resCursos.json() : [];

      // materias: si el padre ya las pasó, no hacer fetch adicional
      if (Array.isArray(materias) && materias.length > 0) {
        // usar la prop `materias` pasada
      } else {
        const resMaterias = await fetch(`${API_URL}/materias`);
        materias = resMaterias.ok ? await resMaterias.json() : [];
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }

  function agregarAsignacion() {
    if (!asignacion.id_materia || !asignacion.id_curso) return;
    const materia = materias.find((m) => m.id_materia == asignacion.id_materia);
    const curso = cursos.find((c) => c.id_curso == asignacion.id_curso);
    const nuevaAsignacion = {
      id_materia: asignacion.id_materia,
      id_curso: asignacion.id_curso,
      nombre_materia: materia?.nombre_materia,
      nombre_curso: curso?.nombre_curso,
    };
    dispatch("asignado", nuevaAsignacion);
    asignacion.id_curso = "";
    asignacion.id_materia = "";
  }

  function quitarLocal(index: number, id?: any) {
    dispatch("remove", { index, id });
  }

  $: cargarDatos();
</script>

<div class="asignar-cursos">
  <div class="form-grid">
    <div class="form-group">
      <label>Materia *</label>
      <select bind:value={asignacion.id_materia} class="select-field">
        <option value="">Seleccione una materia</option>
        {#each materias as materia}
          <option value={materia.id_materia}>{materia.nombre_materia}</option>
        {/each}
      </select>
    </div>

    <div class="form-group">
      <label>Curso *</label>
      <select bind:value={asignacion.id_curso} class="select-field">
        <option value="">Seleccione un curso</option>
        {#each cursos as curso}
          <option value={curso.id_curso}
            >{curso.nombre_curso} - {curso.gestion}</option
          >
        {/each}
      </select>
    </div>
  </div>

  <div class="form-actions">
    <button
      class="btn-primary"
      disabled={!asignacion.id_materia || !asignacion.id_curso}
      on:click={agregarAsignacion}
    >
      Agregar Asignación
    </button>
  </div>

  <!-- Lista de asignaciones PENDIENTES (se muestra aquí) -->
  {#if asignaciones && asignaciones.length > 0}
    <div class="asignaciones-list">
      <h4>Asignaciones Pendientes</h4>
      <div class="asignaciones-grid">
        {#each asignaciones as asig, index (index)}
          <div class="asignacion-card">
            <div class="materia">
              {asig.nombre_materia || asig.materia || "Sin nombre"}
            </div>
            <div class="curso">
              {asig.nombre_curso || asig.curso || "Sin curso"}
            </div>
            <button
              class="btn-remove"
              on:click={() => quitarLocal(index, asig.id)}>✕ Quitar</button
            >
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .asignar-cursos {
    background: #fafbfc;
    border-radius: 8px;
    padding: 20px;
    border: 1px solid #e2e8f0;
    margin-top: 20px;
  }

  h3 {
    margin: 0 0 20px;
    font-size: 1rem;
    color: #1e293b;
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  label {
    font-size: 0.875rem;
    color: #475569;
    font-weight: 500;
  }

  .select-field {
    padding: 0.5rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.375rem;
    background-color: white;
    color: #1e293b;
    width: 100%;
  }

  .select-field option {
    color: #1e293b;
    background: white;
    padding: 0.5rem;
  }

  .form-actions {
    grid-column: span 2;
    display: flex;
    justify-content: flex-end;
    margin-top: 10px;
  }

  .btn-primary {
    padding: 8px 16px;
    background: #00cfe6;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .asignaciones-list {
    margin-top: 20px;
    padding: 10px;
    background: #fff;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }

  .asignaciones-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 10px;
  }

  .asignacion-card {
    background: #f9fafb;
    padding: 10px;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .materia {
    font-weight: 500;
    color: #1e293b;
  }

  .curso {
    font-size: 0.875rem;
    color: #475569;
  }

  .btn-remove {
    background: transparent;
    border: none;
    color: #ef4444;
    cursor: pointer;
    font-size: 1.25rem;
  }

  @media (max-width: 640px) {
    .form-grid {
      grid-template-columns: 1fr;
    }
    .form-actions {
      grid-column: 1;
    }
  }
</style>
