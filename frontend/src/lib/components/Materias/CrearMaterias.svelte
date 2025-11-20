<script>
  let materia = {
    nombre_materia: '',
    nivel: ''
  };
  let loading = false;
  let error = null;
  let success = false;

  async function crearMateria() {
    if (!materia.nombre_materia || !materia.nivel) {
      error = 'Todos los campos son obligatorios';
      return;
    }

    try {
      loading = true;
      error = null;
      
      const response = await fetch('/api/profesores/materias', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(materia)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Error al crear materia');
      }

      const nuevaMateria = await response.json();
      success = true;
      
      // Limpiar formulario después de éxito
      materia = {
        nombre_materia: '',
        nivel: ''
      };

      // Redirigir después de 2 segundos
      setTimeout(() => {
        window.location.href = '/materias';
      }, 2000);

    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  function cancelar() {
    window.location.href = '/materias';
  }
</script>

<div class="container">
  <h1>📚 Crear Nueva Materia</h1>

  {#if error}
    <div class="alert error">
      <strong>Error:</strong> {error}
    </div>
  {/if}

  {#if success}
    <div class="alert success">
      ✅ Materia creada exitosamente. Redirigiendo...
    </div>
  {/if}

  <form on:submit|preventDefault={crearMateria}>
    <div class="form-group">
      <label for="nombre_materia">Nombre de la Materia:</label>
      <input
        type="text"
        id="nombre_materia"
        bind:value={materia.nombre_materia}
        placeholder="Ej: Matemáticas, Lengua, Ciencias, etc."
        required
        maxlength="100"
      >
    </div>

    <div class="form-group">
      <label for="nivel">Nivel:</label>
      <select id="nivel" bind:value={materia.nivel} required>
        <option value="">Selecciona un nivel</option>
        <option value="inicial">Inicial</option>
        <option value="primaria">Primaria</option>
        <option value="secundaria">Secundaria</option>
      </select>
    </div>

    <div class="examples">
      <h3>📝 Ejemplos de materias:</h3>
      <div class="examples-grid">
        <span class="example-tag">Matemáticas</span>
        <span class="example-tag">Lengua</span>
        <span class="example-tag">Ciencias</span>
        <span class="example-tag">Inglés</span>
        <span class="example-tag">Historia</span>
        <span class="example-tag">Geografía</span>
        <span class="example-tag">Arte</span>
        <span class="example-tag">Educación Física</span>
      </div>
    </div>

    <div class="form-actions">
      <button type="submit" disabled={loading} class="btn btn-primary">
        {#if loading}
          ⏳ Creando...
        {:else}
          ✅ Crear Materia
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

  .examples {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 6px;
    margin: 25px 0;
  }

  .examples h3 {
    margin: 0 0 10px 0;
    color: #495057;
    font-size: 14px;
  }

  .examples-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 8px;
  }

  .example-tag {
    background: white;
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 12px;
    text-align: center;
    border: 1px solid #dee2e6;
    color: #6c757d;
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
    background: #e74c3c;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: #c0392b;
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