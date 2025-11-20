<script>
  import { onMount } from 'svelte';
  
  let materias = [];
  let loading = true;
  let error = null;

  async function loadMaterias() {
    try {
      loading = true;
      const response = await fetch('/api/profesores/materias');
      if (!response.ok) throw new Error('Error al cargar materias');
      materias = await response.json();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function deleteMateria(id) {
    if (!confirm('¿Estás seguro de eliminar esta materia?')) return;
    
    try {
      const response = await fetch(`/api/profesores/materias/${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Error al eliminar materia');
      
      await loadMaterias();
    } catch (err) {
      error = err.message;
    }
  }

  async function copyMateria(materia) {
    try {
      const materiaCopy = { ...materia };
      delete materiaCopy.id_materia;
      materiaCopy.nombre_materia += ' (Copia)';
      
      const response = await fetch('/api/profesores/materias', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(materiaCopy)
      });
      
      if (!response.ok) throw new Error('Error al copiar materia');
      
      await loadMaterias();
    } catch (err) {
      error = err.message;
    }
  }

  onMount(() => {
    loadMaterias();
  });
</script>

<div class="container">
  <h1>Gestión de Materias</h1>
  
  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if loading}
    <div class="loading">Cargando materias...</div>
  {:else}
    <div class="actions">
      <a href="/materias/editar" class="btn btn-primary">Nueva Materia</a>
      <a href="/materias/clear" class="btn btn-secondary">Limpiar</a>
    </div>

    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Nombre</th>
          <th>Nivel</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {#each materias as materia}
          <tr>
            <td>{materia.id_materia}</td>
            <td>{materia.nombre_materia}</td>
            <td>{materia.nivel}</td>
            <td class="actions">
              <a href="/materias/crear" class="btn btn-primary">📚 Nueva Materia</a>
              <a href="/materias/editar/{materia.id_materia}" class="btn btn-edit">Editar</a>
              <button on:click={() => copyMateria(materia)} class="btn btn-copy">Copiar</button>
              <button on:click={() => deleteMateria(materia.id_materia)} class="btn btn-delete">Borrar</button>
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