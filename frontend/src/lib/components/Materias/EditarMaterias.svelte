<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  
  
  let materia = { nombre_materia: '', nivel: '' };
  let loading = false;
  let error = null;
  let isEditing = false;

  $: materiaId = $page.params.id;

  onMount(() => {
    if (materiaId) {
      isEditing = true;
      loadMateria();
    }
  });

  async function loadMateria() {
    try {
      loading = true;
      const response = await fetch(`/api/profesores/materias/${materiaId}`);
      if (!response.ok) throw new Error('Error al cargar materia');
      materia = await response.json();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function saveMateria() {
    try {
      loading = true;
      const url = isEditing ? `/api/profesores/materias/${materiaId}` : '/api/profesores/materias';
      const method = isEditing ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(materia)
      });

      if (!response.ok) throw new Error('Error al guardar materia');
      
      window.location.href = '/materias';
    } catch (err) {
      error = err.message;
      loading = false;
    }
  }

  function cancel() {
    window.location.href = '/materias';
  }
</script>

<div class="container">
  <h1>{isEditing ? 'Editar Materia' : 'Nueva Materia'}</h1>
  
  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if loading && isEditing}
    <div class="loading">Cargando...</div>
  {:else}
    <form on:submit|preventDefault={saveMateria}>
      <div class="form-group">
        <label for="nombre">Nombre de la Materia:</label>
        <input 
          type="text" 
          id="nombre" 
          bind:value={materia.nombre_materia} 
          required
        >
      </div>
      
      <div class="form-group">
        <label for="nivel">Nivel:</label>
        <select id="nivel" bind:value={materia.nivel} required>
          <option value="">Seleccionar nivel</option>
          <option value="inicial">Inicial</option>
          <option value="primaria">Primaria</option>
          <option value="secundaria">Secundaria</option>
        </select>
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