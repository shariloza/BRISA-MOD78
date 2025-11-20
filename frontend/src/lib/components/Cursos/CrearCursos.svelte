<script>
  let curso = {
    nombre_curso: '',
    nivel: '',
    gestion: new Date().getFullYear()
  };
  let loading = false;
  let error = null;
  let success = false;

  async function crearCurso() {
    if (!curso.nombre_curso || !curso.nivel || !curso.gestion) {
      error = 'Todos los campos son obligatorios';
      return;
    }

    try {
      loading = true;
      error = null;
      
      const response = await fetch('/api/profesores/cursos', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(curso)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Error al crear curso');
      }

      const nuevoCurso = await response.json();
      success = true;
      
      // Limpiar formulario después de éxito
      curso = {
        nombre_curso: '',
        nivel: '',
        gestion: new Date().getFullYear()
      };

      // Redirigir después de 2 segundos
      setTimeout(() => {
        window.location.href = '/cursos';
      }, 2000);

    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  function cancelar() {
    window.location.href = '/cursos';
  }
</script>

<div class="container">
  <h1>➕ Crear Nuevo Curso</h1>

  {#if error}
    <div class="alert error">
      <strong>Error:</strong> {error}
    </div>
  {/if}

  {#if success}
    <div class="alert success">
      ✅ Curso creado exitosamente. Redirigiendo...
    </div>
  {/if}

  <form on:submit|preventDefault={crearCurso}>
    <div class="form-group">
      <label for="nombre_curso">Nombre del Curso:</label>
      <input
        type="text"
        id="nombre_curso"
        bind:value={curso.nombre_curso}
        placeholder="Ej: Primaria 1A, Inicial B, etc."
        required
        maxlength="100"
      >
    </div>

    <div class="form-group">
      <label for="nivel">Nivel:</label>
      <select id="nivel" bind:value={curso.nivel} required>
        <option value="">Selecciona un nivel</option>
        <option value="inicial">Inicial</option>
        <option value="primaria">Primaria</option>
        <option value="secundaria">Secundaria</option>
      </select>
    </div>

    <div class="form-group">
      <label for="gestion">Gestión (Año):</label>
      <input
        type="number"
        id="gestion"
        bind:value={curso.gestion}
        min="2020"
        max="2030"
        required
      >
      <small>Ej: 2024, 2025, etc.</small>
    </div>

    <div class="form-actions">
      <button type="submit" disabled={loading} class="btn btn-primary">
        {#if loading}
          ⏳ Creando...
        {:else}
          ✅ Crear Curso
        {/if}
      </button>
      
      <button type="button" on:click={cancelar} class="btn btn-secondary">
        ❌ Cancelar
      </button>
    </div>
  </form>
</div>

<style>
  .container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }

  h1 {
    color: #2c3e50;
    text-align: center;
    margin-bottom: 30px;
  }

  .form-group {
    margin-bottom: 20px;
  }

  label {
    display: block;
    margin-bottom: 8px;
    font-weight: bold;
    color: #34495e;
  }

  input, select {
    width: 100%;
    padding: 12px;
    border: 2px solid #bdc3c7;
    border-radius: 6px;
    font-size: 16px;
    box-sizing: border-box;
    transition: border-color 0.3s ease;
  }

  input:focus, select:focus {
    outline: none;
    border-color: #3498db;
  }

  small {
    display: block;
    margin-top: 5px;
    color: #7f8c8d;
    font-size: 12px;
  }

  .form-actions {
    display: flex;
    gap: 15px;
    margin-top: 30px;
  }

  .btn {
    flex: 1;
    padding: 15px;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .btn-primary {
    background: #27ae60;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #219a52;
    transform: translateY(-2px);
  }

  .btn-secondary {
    background: #95a5a6;
    color: white;
  }

  .btn-secondary:hover {
    background: #7f8c8d;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .alert {
    padding: 15px;
    border-radius: 6px;
    margin-bottom: 20px;
    text-align: center;
  }

  .error {
    background: #ffeaa7;
    color: #d63031;
    border: 1px solid #fab1a0;
  }

  .success {
    background: #55efc4;
    color: #00b894;
    border: 1px solid #00b894;
  }
</style>