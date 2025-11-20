<script lang="ts">
  import { onMount } from "svelte";

  let cursos = [];
  let loading = true;
  let error = null;

  // Cargar cursos al inicializar
  async function loadCursos() {
    try {
      loading = true;
      const response = await fetch('/api/profesores/cursos');
      if (!response.ok) throw new Error('Error al cargar cursos');
      cursos = await response.json();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  // Eliminar curso
  async function deleteCurso(id) {
    if (!confirm('¿Estás seguro de eliminar este curso?')) return;
    
    try {
      const response = await fetch(`/api/profesores/cursos/${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Error al eliminar curso');
      
      // Recargar la lista
      await loadCursos();
    } catch (err) {
      error = err.message;
    }
  }

  // Copiar curso
  async function copyCurso(curso) {
    try {
      const cursoCopy = { ...curso };
      delete cursoCopy.id_curso;
      cursoCopy.nombre_curso += ' (Copia)';
      
      const response = await fetch('/api/profesores/cursos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cursoCopy)
      });
      
      if (!response.ok) throw new Error('Error al copiar curso');
      
      await loadCursos();
    } catch (err) {
      error = err.message;
    }
  }

  onMount(() => {
    loadCursos();
  });
</script>

<div class="container">
  <h1>Gestión de Cursos</h1>
  
  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if loading}
    <div class="loading">Cargando cursos...</div>
  {:else}
    <div class="actions">
      <a href="/cursos/editar" class="btn btn-primary">Nuevo Curso</a>
      <a href="/cursos/clear" class="btn btn-secondary">Limpiar</a>
    </div>

    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Nombre</th>
          <th>Nivel</th>
          <th>Gestión</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {#each cursos as curso}
          <tr>
            <td>{curso.id_curso}</td>
            <td>{curso.nombre_curso}</td>
            <td>{curso.nivel}</td>
            <td>{curso.gestion}</td>
            <td class="actions">
              <a href="/cursos/crear" class="btn btn-primary">➕ Nuevo Curso</a>
              <a href="/cursos/editar/{curso.id_curso}" class="btn btn-edit">Editar</a>
              <button on:click={() => copyCurso(curso)} class="btn btn-copy">Copiar</button>
              <button on:click={() => deleteCurso(curso.id_curso)} class="btn btn-delete">Borrar</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<style>
  .container { padding: 20px; }
  .loading, .error { padding: 10px; margin: 10px 0; }
  .error { background: #fee; color: #c00; }
  .loading { background: #eef; }
  
  .actions { margin: 20px 0; }
  
  table { 
    width: 100%; 
    border-collapse: collapse;
    margin-top: 20px;
  }
  
  th, td { 
    padding: 12px; 
    text-align: left; 
    border-bottom: 1px solid #ddd;
  }
  
  th { background: #f5f5f5; }
  
  .btn { 
    padding: 6px 12px; 
    margin: 0 2px; 
    border: none; 
    border-radius: 4px; 
    cursor: pointer; 
    text-decoration: none;
    display: inline-block;
    font-size: 14px;
  }
  
  .btn-primary { background: #007bff; color: white; }
  .btn-secondary { background: #6c757d; color: white; }
  .btn-edit { background: #28a745; color: white; }
  .btn-copy { background: #17a2b8; color: white; }
  .btn-delete { background: #dc3545; color: white; }
</style>