<script>
  import { onMount } from 'svelte';
  import { page } from '@app/stores';
  //import { page } from '$app/stores';
  
  let curso = { nombre_curso: '', nivel: '', gestion: '' };
  let loading = false;
  let error = null;
  let isEditing = false;

  $: cursoId = $page.params.id;

  onMount(() => {
    if (cursoId) {
      isEditing = true;
      loadCurso();
    }
  });

  async function loadCurso() {
    try {
      loading = true;
      const response = await fetch(`/api/profesores/cursos/${cursoId}`);
      if (!response.ok) throw new Error('Error al cargar curso');
      curso = await response.json();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function saveCurso() {
    try {
      loading = true;
      const url = isEditing ? `/api/profesores/cursos/${cursoId}` : '/api/profesores/cursos';
      const method = isEditing ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(curso)
      });

      if (!response.ok) throw new Error('Error al guardar curso');
      
      // Redirigir a la lista
      window.location.href = '/cursos';
    } catch (err) {
      error = err.message;
      loading = false;
    }
  }

  function cancel() {
    window.location.href = '/cursos';
  }
</script>

<div class="container">
  <h1>{isEditing ? 'Editar Curso' : 'Nuevo Curso'}</h1>
  
  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if loading && isEditing}
    <div class="loading">Cargando...</div>
  {:else}
    <form on:submit|preventDefault={saveCurso}>
      <div class="form-group">
        <label for="nombre">Nombre del Curso:</label>
        <input 
          type="text" 
          id="nombre" 
          bind:value={curso.nombre_curso} 
          required
        >
      </div>
      
      <div class="form-group">
        <label for="nivel">Nivel:</label>
        <select id="nivel" bind:value={curso.nivel} required>
          <option value="">Seleccionar nivel</option>
          <option value="inicial">Inicial</option>
          <option value="primaria">Primaria</option>
          <option value="secundaria">Secundaria</option>
        </select>
      </div>
      
      <div class="form-group">
        <label for="gestion">Gestión:</label>
        <input 
          type="number" 
          id="gestion" 
          bind:value={curso.gestion} 
          min="2020" 
          max="2030"
          required
        >
      </div>
      
      <div class="form-actions">
        <button type="submit" disabled={loading} class="btn btn-primary">
          {loading ? 'Guardando...' : 'Guardar'}
        </button>
        <button type="button" on:click={cancel} class="btn btn-secondary">Cancelar</button>
      </div>
    </form>
  {/if}
</div>

<style>
  .container { padding: 20px; max-width: 500px; }
  .form-group { margin-bottom: 15px; }
  label { display: block; margin-bottom: 5px; font-weight: bold; }
  input, select { 
    width: 100%; 
    padding: 8px; 
    border: 1px solid #ddd; 
    border-radius: 4px; 
    box-sizing: border-box;
  }
  .form-actions { margin-top: 20px; }
  .btn { 
    padding: 10px 20px; 
    margin-right: 10px; 
    border: none; 
    border-radius: 4px; 
    cursor: pointer; 
  }
  .btn-primary { background: #007bff; color: white; }
  .btn-secondary { background: #6c757d; color: white; }
  .btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>