<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let curso: any;

  let formData = { ...curso };
  let loading = false;
  let error: string | null = null;
  let success = false;

  async function guardarCambios() {
    if (!formData.nombre_curso.trim() || !formData.nivel) {
      error = 'Todos los campos son obligatorios';
      return;
    }

    try {
      loading = true;
      error = null;

      // convertir 'gestion' a string para cumplir validación backend
      const payload = { ...formData, gestion: String(formData.gestion) };
      const response = await fetch(`http://localhost:8000/api/profesores/cursos/${curso.id_curso}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.message || 'Error al actualizar el curso');
      }

      success = true;
      setTimeout(() => {
        dispatch('close');
      }, 1500);

    } catch (err: any) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="modal-container">
  <!-- Header del Modal -->
  <div class="modal-header">
    <div class="header-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
      </svg>
    </div>
    <h2 class="modal-title">Editar Curso</h2>
    <p class="modal-subtitle">Actualiza los datos del curso académico</p>
    <button class="btn-close" on:click={() => dispatch('close')} aria-label="Cerrar modal">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg> X
    </button>
  </div>

  <!-- Alertas -->
  {#if error}
    <div class="alert alert-error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <span>{error}</span>
    </div>
  {/if}

  {#if success}
    <div class="alert alert-success">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
      </svg>
      <span>¡Curso actualizado exitosamente!</span>
    </div>
  {/if}

  <!-- Formulario -->
  <form on:submit|preventDefault={guardarCambios} class="modal-form">
    <div class="form-group">
      <label for="nombre" class="form-label">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
        </svg>
        Nombre del Curso
      </label>
      <input
        id="nombre"
        type="text"
        bind:value={formData.nombre_curso}
        placeholder="Ej: 1ro de Primaria A, 2do de Secundaria B..."
        class="form-input"
        disabled={loading || success}
        required
      />
    </div>

    <div class="form-group">
      <label for="nivel" class="form-label">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
          <path d="M6 12v5c3 3 9 3 12 0v-5"></path>
        </svg>
        Nivel Académico
      </label>
      <select
        id="nivel"
        bind:value={formData.nivel}
        class="form-select"
        disabled={loading || success}
        required
      >
        <option value="">Selecciona un nivel</option>
        <option value="inicial">🎨 Inicial</option>
        <option value="primaria">📖 Primaria</option>
        <option value="secundaria">🎓 Secundaria</option>
      </select>
    </div>

    <div class="form-group">
      <label for="gestion" class="form-label">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
        Gestión (Año)
      </label>
      <input
        id="gestion"
        type="number"
        bind:value={formData.gestion}
        min="2020"
        max="2035"
        class="form-input"
        disabled={loading || success}
        required
      />
      <div class="input-hint">Año académico del curso</div>
    </div>

    

    <!-- Botones de Acción -->
    <div class="form-actions">
      <button
        type="button"
        on:click={() => dispatch('close')}
        class="btn btn-secondary"
        disabled={loading}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
        Cancelar
      </button>
      <button
        type="submit"
        class="btn btn-primary"
        disabled={loading || success}
      >
        {#if loading}
          <div class="spinner"></div>
          Guardando...
        {:else if success}
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          Guardado
        {:else}
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
            <polyline points="17 21 17 13 7 13 7 21"></polyline>
            <polyline points="7 3 7 8 15 8"></polyline>
          </svg>
          Guardar Cambios
        {/if}
      </button>
    </div>
  </form>
</div>

<style>
  :root {
    --nav: #0d2e53;
    --nav-secondary: #07264a;
    --accent: #00cfe6;
    --muted: #e9f0f4;
  }

  .modal-container {
    background: white;
    border-radius: 20px;
    width: 100%;
    height: 100%;
    max-width: none;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* ============================================
     HEADER DEL MODAL
     ============================================ */
  .modal-header {
    position: relative;
    background: linear-gradient(135deg, var(--nav) 0%, var(--nav-secondary) 100%);
    padding: 32px 24px;
    text-align: center;
    border-bottom: 3px solid var(--accent);
    flex-shrink: 0;
  }

  .header-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 16px;
    background: var(--accent);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px rgba(0, 207, 230, 0.3);
  }

  .header-icon svg {
    width: 32px;
    height: 32px;
    color: white;
  }

  .modal-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: white;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
  }

  .modal-subtitle {
    font-size: 0.9375rem;
    color: #b8d4e8;
    margin: 0;
    font-weight: 400;
  }

  .btn-close {
    position: absolute;
    top: 16px;
    right: 16px;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: white;
  }

  .btn-close svg {
    width: 20px;
    height: 20px;
  }

  .btn-close:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: scale(1.05);
  }

  /* ============================================
     ALERTAS
     ============================================ */
  .alert {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 20px;
    margin: 20px 24px 0;
    border-radius: 12px;
    font-weight: 500;
    font-size: 0.9375rem;
    animation: slideDown 0.3s ease;
    flex-shrink: 0;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .alert svg {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
  }

  .alert-error {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    color: #991b1b;
    border: 2px solid #fecaca;
  }

  .alert-error svg {
    color: #dc2626;
  }

  .alert-success {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    color: #166534;
    border: 2px solid #bbf7d0;
  }

  .alert-success svg {
    color: #16a34a;
  }

  /* ============================================
     FORMULARIO
     ============================================ */
  .modal-form {
    padding: 28px 24px 24px;
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .form-group {
    margin-bottom: 24px;
  }

  .form-label {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    font-weight: 600;
    font-size: 0.9375rem;
    color: var(--nav);
  }

  .form-label svg {
    width: 18px;
    height: 18px;
    color: var(--accent);
  }

  .form-input,
  .form-select {
    width: 100%;
    padding: 14px 16px;
    border: 2px solid var(--muted);
    border-radius: 12px;
    font-size: 15px;
    font-weight: 500;
    color: var(--nav);
    background: white;
    transition: all 0.2s ease;
    font-family: inherit;
  }

  .form-input:focus,
  .form-select:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(0, 207, 230, 0.1);
  }

  .form-input::placeholder {
    color: #8fa9be;
  }

  .form-input:disabled,
  .form-select:disabled {
    background: var(--muted);
    cursor: not-allowed;
    opacity: 0.6;
  }

  .form-select {
    cursor: pointer;
  }

  .form-select option {
    padding: 12px;
  }

  .input-hint {
    font-size: 0.8125rem;
    color: #6b8ba3;
    margin-top: 6px;
    font-weight: 400;
  }

  /* ============================================
     INFORMACIÓN EXISTENTE
     ============================================ */
  .existing-info {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px;
    margin: 16px 0;
  }

  .info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
  }

  .info-item:not(:last-child) {
    border-bottom: 1px solid #e2e8f0;
  }

  .info-label {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 500;
  }

  .info-value {
    font-size: 0.875rem;
    color: var(--nav);
    font-weight: 600;
    font-family: 'Monaco', 'Consolas', monospace;
  }

  .info-status {
    font-size: 0.875rem;
    color: #16a34a;
    font-weight: 600;
    background: #dcfce7;
    padding: 4px 8px;
    border-radius: 6px;
  }

  /* ============================================
     BOTONES
     ============================================ */
  .form-actions {
    display: flex;
    gap: 12px;
    margin-top: auto;
    padding-top: 20px;
  }

  .btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px 24px;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 15px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: inherit;
  }

  .btn svg {
    width: 18px;
    height: 18px;
  }

  .btn-primary {
    background: var(--accent);
    color: white;
    box-shadow: 0 4px 12px rgba(0, 207, 230, 0.3);
  }

  .btn-primary:hover:not(:disabled) {
    background: #00b8d4;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 207, 230, 0.4);
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .btn-secondary {
    background: #f1f5f9;
    color: #475569;
    border: 2px solid #e2e8f0;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #e2e8f0;
    border-color: #cbd5e1;
  }

  .btn-secondary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* Spinner */
  .spinner {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* ============================================
     RESPONSIVE
     ============================================ */
  @media (max-width: 640px) {
    .modal-container {
      max-width: 100%;
      border-radius: 20px 20px 0 0;
    }

    .modal-header {
      padding: 28px 20px;
    }

    .header-icon {
      width: 56px;
      height: 56px;
    }

    .header-icon svg {
      width: 28px;
      height: 28px;
    }

    .modal-title {
      font-size: 1.5rem;
    }

    .modal-subtitle {
      font-size: 0.875rem;
    }

    .modal-form {
      padding: 24px 20px 20px;
    }

    .form-group {
      margin-bottom: 20px;
    }

    .existing-info {
      margin: 12px 0;
      padding: 12px;
    }

    .form-actions {
      flex-direction: column-reverse;
      gap: 10px;
    }

    .btn {
      width: 100%;
    }
  }

  @media (max-width: 480px) {
    .modal-header {
      padding: 24px 16px;
    }

    .modal-title {
      font-size: 1.375rem;
    }

    .form-input,
    .form-select {
      padding: 12px 14px;
      font-size: 14px;
    }

    .alert {
      margin: 16px 16px 0;
      padding: 12px 16px;
      font-size: 0.875rem;
    }

    .info-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
    }
  }
</style>