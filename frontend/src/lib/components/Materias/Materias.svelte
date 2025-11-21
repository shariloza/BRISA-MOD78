<script lang="ts">
  import { onMount } from "svelte";
  import CrearMaterias from "./CrearMaterias.svelte";
  import EditarMaterias from "./EditarMaterias.svelte";

  const API_URL = "http://localhost:8000/api/profesores";
  const MATERIAS_URL = `${API_URL}/materias`;

  let materias: any[] = [];
  let todasLasMaterias: any[] = [];
  let loading = true;
  let error: string | null = null;
  let searchTerm = "";

  // Modales
  let showCrear = false;
  let showEditar = false;
  let materiaAEditar: any = null;

  async function loadMaterias() {
    try {
      loading = true;
      error = null;
      const res = await fetch(MATERIAS_URL);
      if (!res.ok) throw new Error(`Error ${res.status}`);
      const data = await res.json();
      todasLasMaterias = data;
      materias = data;
    } catch (err: any) {
      error = err.message || "No se pudo conectar al servidor";
    } finally {
      loading = false;
    }
  }

  async function deleteMateria(id: number) {
    if (!confirm("¿Seguro que quieres eliminar esta materia?")) return;
    try {
      const res = await fetch(`${MATERIAS_URL}/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Error al eliminar");
      await loadMaterias();
    } catch (err: any) {
      error = err.message;
    }
  }

  function abrirEditar(materia: any) {
    materiaAEditar = { ...materia };
    showEditar = true;
  }

  function cerrarCrear() {
    showCrear = false;
    loadMaterias();
  }

  function cerrarEditar() {
    showEditar = false;
    materiaAEditar = null;
    loadMaterias();
  }

  $: materiasFiltradas = todasLasMaterias.filter(m =>
    m.nombre_materia.toLowerCase().includes(searchTerm.toLowerCase())
  );
  $: materias = searchTerm ? materiasFiltradas : todasLasMaterias;

  onMount(loadMaterias);
</script>

<div class="page-wrapper">
  <!-- Header Oscuro -->
  <header class="dark-header">
    <div class="header-content">
      <h1 class="header-title">Gestión de Materias</h1>
      <p class="header-subtitle">Administra todas las materias académicas del sistema</p>
    </div>
  </header>

  <!-- Contenido Principal -->
  <div class="main-content">
    <div class="container">
      <!-- Controles -->
      <div class="controls-section">
        <div class="search-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            type="text"
            bind:value={searchTerm}
            placeholder="Buscar materia..."
            class="search-input"
          />
          {#if searchTerm}
            <button on:click={() => (searchTerm = "")} class="clear-btn" aria-label="Limpiar búsqueda">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          {/if}
        </div>

        <button on:click={() => (showCrear = true)} class="btn-crear">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Nueva Materia
        </button>
      </div>

      <!-- Estados y Contenido -->
      {#if error}
        <div class="error-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <p>{error}</p>
        </div>
      {/if}

      {#if loading}
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Cargando materias...</p>
        </div>
      {:else if materias.length === 0}
        <div class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 6.5a9.77 9.77 0 0 1 8.82 5.5 9.77 9.77 0 0 1-17.64 0 9.77 9.77 0 0 1 8.82-5.5z"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
          <h3>{searchTerm ? "No se encontraron materias" : "No hay materias registradas"}</h3>
          <p>{searchTerm ? "Intenta con otro término de búsqueda" : "Comienza agregando una nueva materia"}</p>
        </div>
      {:else}
        <div class="table-wrapper">
          <div class="table-container">
            <table class="table-premium">
              <thead>
                <tr>
                  <th class="th-materia">
                    <div class="th-content">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                      </svg>
                      Materia
                    </div>
                  </th>
                  <th class="th-nivel">
                    <div class="th-content">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
                        <path d="M6 12v5c3 3 9 3 12 0v-5"></path>
                      </svg>
                      Nivel
                    </div>
                  </th>
                  <th class="th-actions">
                    <div class="th-content">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="1"></circle>
                        <circle cx="12" cy="5" r="1"></circle>
                        <circle cx="12" cy="19" r="1"></circle>
                      </svg>
                      Acciones
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                {#each materias as m (m.id_materia)}
                  <tr class="table-row">
                    <td class="td-materia">
                      <div class="materia-info">
                        <div class="materia-icon">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                          </svg>
                        </div>
                        <span class="materia-nombre">{m.nombre_materia}</span>
                      </div>
                    </td>
                    <td class="td-nivel">
                      <span class="badge badge-{m.nivel || 'sin-nivel'}">
                        {m.nivel ? m.nivel.charAt(0).toUpperCase() + m.nivel.slice(1) : "Sin nivel"}
                      </span>
                    </td>
                    <td class="td-actions">
                      <div class="actions-group">
                        <button on:click={() => abrirEditar(m)} class="btn-action btn-edit" title="Editar materia">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                          </svg>
                          Editar
                        </button>
                        <button on:click={() => deleteMateria(m.id_materia)} class="btn-action btn-delete" title="Eliminar materia">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                          </svg>
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
    </div>
  </div>

  <!-- Botón Flotante Mobile -->
  <button on:click={() => (showCrear = true)} class="fab" title="Crear nueva materia" aria-label="Crear nueva materia">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <line x1="12" y1="5" x2="12" y2="19"></line>
      <line x1="5" y1="12" x2="19" y2="12"></line>
    </svg>
  </button>

  <!-- Modales -->
  {#if showCrear}
    <div class="overlay" on:click={() => (showCrear = false)}>
      <div class="modal" on:click|stopPropagation>
        <CrearMaterias on:close={cerrarCrear} />
      </div>
    </div>
  {/if}

  {#if showEditar && materiaAEditar}
    <div class="overlay" on:click={cerrarEditar}>
      <div class="modal" on:click|stopPropagation>
        <EditarMaterias materia={materiaAEditar} on:close={cerrarEditar} />
      </div>
    </div>
  {/if}
</div>

<style>
  :root {
    --nav: #0d2e53;
    --nav-secondary: #07264a;
    --accent: #00cfe6;
    --muted: #e9f0f4;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  .page-wrapper {
    min-height: 100vh;
    background: var(--muted);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'Roboto', sans-serif;
  }

  /* ============================================
     HEADER OSCURO
     ============================================ */
  .dark-header {
    background: linear-gradient(135deg, var(--nav) 0%, var(--nav-secondary) 100%);
    padding: 48px 24px;
    box-shadow: 0 4px 20px rgba(13, 46, 83, 0.15);
  }

  .header-content {
    max-width: 1400px;
    margin: 0 auto;
    text-align: center;
  }

  .header-title {
    font-size: 3rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 12px 0;
    letter-spacing: -1px;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }

  .header-subtitle {
    font-size: 1.25rem;
    color: #b8d4e8;
    margin: 0;
    font-weight: 400;
  }

  @media (max-width: 768px) {
    .dark-header {
      padding: 32px 20px;
    }

    .header-title {
      font-size: 2rem;
    }

    .header-subtitle {
      font-size: 1rem;
    }
  }

  /* ============================================
     CONTENIDO PRINCIPAL
     ============================================ */
  .main-content {
    background: var(--muted);
    min-height: calc(100vh - 192px);
  }

  .container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 32px 24px 100px;
  }

  @media (max-width: 768px) {
    .container {
      padding: 24px 16px 100px;
    }
  }

  /* ============================================
     CONTROLES
     ============================================ */
  .controls-section {
    display: flex;
    gap: 16px;
    margin-bottom: 32px;
    flex-wrap: wrap;
    align-items: center;
  }

  .search-wrapper {
    position: relative;
    flex: 1;
    min-width: 280px;
  }

  .search-icon {
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    color: #6b8ba3;
    pointer-events: none;
  }

  .search-input {
    width: 100%;
    padding: 14px 48px 14px 48px;
    border: 2px solid var(--muted);
    border-radius: 12px;
    font-size: 15px;
    font-weight: 500;
    background: #ffffff;
    color: var(--nav);
    transition: all 0.2s ease;
  }

  .search-input:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(0, 207, 230, 0.1);
  }

  .search-input::placeholder {
    color: #8fa9be;
  }

  .clear-btn {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    color: #8fa9be;
    transition: all 0.2s ease;
  }

  .clear-btn svg {
    width: 16px;
    height: 16px;
  }

  .clear-btn:hover {
    background: var(--muted);
    color: var(--nav);
  }

  .btn-crear {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 14px 28px;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 15px;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(0, 207, 230, 0.3);
    white-space: nowrap;
  }

  .btn-crear svg {
    width: 20px;
    height: 20px;
  }

  .btn-crear:hover {
    background: #00b8d4;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 207, 230, 0.4);
  }

  .btn-crear:active {
    transform: translateY(0);
  }

  @media (max-width: 768px) {
    .search-wrapper {
      min-width: 100%;
    }

    .btn-crear {
      display: none;
    }
  }

  /* ============================================
     TABLA PREMIUM
     ============================================ */
  .table-wrapper {
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(13, 46, 83, 0.08);
    border: 2px solid var(--muted);
    overflow: hidden;
  }

  .table-container {
    overflow-x: auto;
  }

  .table-premium {
    width: 100%;
    border-collapse: collapse;
  }

  /* Table Header */
  thead {
    background: linear-gradient(135deg, var(--nav) 0%, var(--nav-secondary) 100%);
  }

  thead tr {
    border-bottom: 2px solid var(--nav-secondary);
  }

  th {
    padding: 0;
    text-align: left;
    font-weight: 600;
    color: #ffffff;
  }

  .th-content {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 18px 20px;
    font-size: 0.8125rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .th-content svg {
    width: 18px;
    height: 18px;
    opacity: 0.9;
  }

  .th-materia {
    width: 40%;
  }

  .th-nivel {
    width: 30%;
    text-align: center;
  }

  .th-nivel .th-content {
    justify-content: center;
  }

  .th-actions {
    width: 30%;
    text-align: center;
  }

  .th-actions .th-content {
    justify-content: center;
  }

  /* Table Body */
  tbody tr {
    border-bottom: 1px solid var(--muted);
    transition: all 0.25s ease;
  }

  tbody tr:hover {
    background: linear-gradient(90deg, #f0f9fb 0%, #ffffff 100%);
    transform: scale(1.002);
  }

  tbody tr:last-child {
    border-bottom: none;
  }

  td {
    padding: 18px 16px;
    vertical-align: middle;
  }

  /* Columna Materia */
  .td-materia {
    padding: 18px 16px;
  }

  .materia-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .materia-icon {
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--accent) 0%, #00b8d4 100%);
    border-radius: 12px;
    flex-shrink: 0;
    box-shadow: 0 3px 10px rgba(0, 207, 230, 0.25);
  }

  .materia-icon svg {
    width: 24px;
    height: 24px;
    color: white;
  }

  .materia-nombre {
    font-size: 1.0625rem;
    font-weight: 600;
    color: var(--nav);
    line-height: 1.3;
  }

  /* Columna Nivel */
  .td-nivel {
    padding: 18px 16px;
    text-align: center;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 0.875rem;
    font-weight: 700;
    letter-spacing: 0.4px;
    text-transform: uppercase;
  }

  .badge-inicial {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    color: #b91c1c;
    border: 1px solid #fecaca;
  }

  .badge-primaria {
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    color: #1e40af;
    border: 1px solid #bfdbfe;
  }

  .badge-secundaria {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    color: #15803d;
    border: 1px solid #bbf7d0;
  }

  .badge-sin-nivel {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    color: #64748b;
    border: 1px solid #e2e8f0;
  }

  /* Columna Acciones */
  .td-actions {
    padding: 18px 16px;
  }

  .actions-group {
    display: flex;
    gap: 10px;
    justify-content: center;
  }

  .btn-action {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 11px 18px;
    border: none;
    border-radius: 10px;
    font-size: 0.9375rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
  }

  .btn-action svg {
    width: 17px;
    height: 17px;
  }

  .btn-edit {
    background: var(--accent);
    color: white;
  }

  .btn-edit:hover {
    background: #00b8d4;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 207, 230, 0.3);
  }

  .btn-delete {
    background: #ef4444;
    color: white;
  }

  .btn-delete:hover {
    background: #dc2626;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  }

  .btn-action:active {
    transform: translateY(0);
  }

  /* Responsive Table */
  @media (max-width: 1024px) {
    .th-content {
      padding: 16px 14px;
      font-size: 0.75rem;
      gap: 8px;
    }

    .th-content svg {
      width: 16px;
      height: 16px;
    }

    .td-materia,
    .td-nivel,
    .td-actions {
      padding: 16px 12px;
    }

    .materia-icon {
      width: 40px;
      height: 40px;
    }

    .materia-icon svg {
      width: 20px;
      height: 20px;
    }

    .materia-nombre {
      font-size: 1rem;
    }

    .badge {
      padding: 7px 14px;
      font-size: 0.8125rem;
    }

    .btn-action {
      padding: 10px 16px;
      font-size: 0.875rem;
      gap: 6px;
    }

    .btn-action svg {
      width: 16px;
      height: 16px;
    }
  }

  @media (max-width: 768px) {
    .th-materia {
      width: 50%;
    }

    .th-nivel {
      width: 50%;
    }

    .th-actions {
      display: none;
    }

    .td-actions {
      display: none;
    }

    tbody tr {
      cursor: pointer;
      position: relative;
    }

    tbody tr::after {
      content: '›';
      position: absolute;
      right: 16px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 1.5rem;
      color: var(--accent);
      font-weight: bold;
    }
  }

  @media (max-width: 480px) {
    .materia-icon {
      width: 36px;
      height: 36px;
    }

    .materia-icon svg {
      width: 18px;
      height: 18px;
    }

    .materia-nombre {
      font-size: 0.9375rem;
    }

    .badge {
      padding: 6px 12px;
      font-size: 0.75rem;
    }

    .th-content {
      padding: 14px 10px;
      font-size: 0.7rem;
    }

    .td-materia,
    .td-nivel {
      padding: 14px 10px;
    }
  }

  /* ============================================
     ESTADOS
     ============================================ */
  .loading-state,
  .error-state,
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 24px;
    text-align: center;
    background: #ffffff;
    border-radius: 16px;
    border: 2px solid var(--muted);
    box-shadow: 0 2px 8px rgba(13, 46, 83, 0.08);
  }

  .loading-state p,
  .error-state p,
  .empty-state p {
    color: #6b8ba3;
    font-size: 1rem;
    margin: 12px 0 0 0;
    font-weight: 500;
  }

  .empty-state h3 {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--nav);
    margin: 12px 0 8px 0;
  }

  .empty-state svg,
  .error-state svg {
    width: 56px;
    height: 56px;
    color: #c8dce8;
    margin-bottom: 8px;
  }

  .error-state {
    background: #fef2f2;
    border-color: #fecaca;
  }

  .error-state svg {
    color: #ef4444;
  }

  .error-state p {
    color: #991b1b;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--muted);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-bottom: 16px;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* ============================================
     FAB
     ============================================ */
  .fab {
    position: fixed;
    bottom: 32px;
    right: 32px;
    width: 64px;
    height: 64px;
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 50%;
    box-shadow: 0 8px 24px rgba(0, 207, 230, 0.4);
    cursor: pointer;
    transition: all 0.3s ease;
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }

  .fab svg {
    width: 28px;
    height: 28px;
  }

  .fab:hover {
    background: #00b8d4;
    transform: scale(1.08) rotate(90deg);
    box-shadow: 0 12px 32px rgba(0, 207, 230, 0.5);
  }

  @media (max-width: 768px) {
    .fab {
      display: flex;
    }
  }

  /* ============================================
     MODALES
     ============================================ */
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(13, 46, 83, 0.75);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(8px);
    animation: fadeIn 0.2s ease-out;
    padding: 20px;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .modal {
    background: white;
    border-radius: 20px;
    max-width: 600px;
    width: 100%;
    max-height: 90vh;
    overflow: auto;
    box-shadow: 0 25px 50px rgba(13, 46, 83, 0.4);
    animation: slideUp 0.3s ease;
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px) scale(0.96);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  /* ============================================
     SCROLLBAR
     ============================================ */
  ::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }

  ::-webkit-scrollbar-track {
    background: var(--muted);
  }

  ::-webkit-scrollbar-thumb {
    background: #b8d4e8;
    border-radius: 5px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: #8fa9be;
  }
</style>