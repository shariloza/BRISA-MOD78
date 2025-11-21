<script lang="ts">
  import { onMount } from "svelte";
  import CrearCursos from "./CrearCursos.svelte";
  import EditarCursos from "./EditarCursos.svelte";

  const API_URL = "http://localhost:8000/api/profesores";
  const CURSOS_URL = `${API_URL}/cursos`;

  let cursos: any[] = [];
  let loading = true;
  let error: string | null = null;

  // Filtros
  let searchTerm = "";
  let nivelFiltro = "todos";

  // Modales
  let showCrear = false;
  let showEditar = false;
  let cursoAEditar: any = null;

  async function loadCursosConInfoReal() {
    try {
      loading = true;
      error = null;

      // 1. Cargar cursos + profesores EN PARALELO (lo más rápido posible)
      const [resCursos, resProfes] = await Promise.all([
        fetch(CURSOS_URL),
        fetch(API_URL),
      ]);

      if (!resCursos.ok || !resProfes.ok) {
        throw new Error("Error al cargar datos básicos");
      }

      const cursosBase = await resCursos.json();
      const profesores = await resProfes.json();

      // 2. Cargar TODAS las asignaciones de una sola vez (nuevo endpoint recomendado)
      // Si tu backend tiene un endpoint tipo /asignaciones o /cursos-con-profesores → úsalo
      // Si NO lo tiene, esta es la forma más rápida con tu API actual:
      const asignacionesPromises = profesores.map((prof: any) =>
        fetch(`${API_URL}/${prof.id_persona}/asignaciones`)
          .then((r) => (r.ok ? r.json() : []))
          .catch(() => []),
      );

      const todasAsignacionesArrays = await Promise.all(asignacionesPromises);
      const todasAsignaciones = todasAsignacionesArrays.flat();

      // 3. Mapear el primer profesor titular por curso (el que se asignó primero)
      const profesorPorCurso = new Map<number, string>();
      for (const a of todasAsignaciones) {
        if (!profesorPorCurso.has(a.id_curso)) {
          profesorPorCurso.set(a.id_curso, a.nombre_profesor || "Sin nombre");
        }
      }

      // 4. Enriquecer cursos
      cursos = cursosBase.map((c: any) => ({
        ...c,
        profesor_titular:
          profesorPorCurso.get(c.id_curso) || "Sin profesor asignado",
        total_estudiantes: c.total_estudiantes || 0,
      }));
    } catch (err: any) {
      error = "No se pudieron cargar los cursos";
      console.error(err);
    } finally {
      loading = false;
    }
  }

  async function deleteCurso(id: number) {
    if (!confirm("¿Eliminar este curso permanentemente?")) return;
    try {
      await fetch(`${CURSOS_URL}/${id}`, { method: "DELETE" });
      await loadCursosConInfoReal();
    } catch {
      alert("Error al eliminar");
    }
  }

  function abrirEditar(curso: any) {
    cursoAEditar = { ...curso };
    showEditar = true;
  }

  function cerrarCrear() {
    showCrear = false;
    loadCursosConInfoReal();
  }

  function cerrarEditar() {
    showEditar = false;
    loadCursosConInfoReal();
  }

  $: cursosFiltrados = cursos.filter((c) => {
    const busca = searchTerm.toLowerCase();
    return (
      (c.nombre_curso.toLowerCase().includes(busca) ||
        c.profesor_titular.toLowerCase().includes(busca)) &&
      (nivelFiltro === "todos" || c.nivel === nivelFiltro)
    );
  });

  onMount(loadCursosConInfoReal);
</script>

<div class="page-wrapper">
  <!-- Header Oscuro -->
  <header class="dark-header">
    <div class="header-content">
      <h1 class="header-title">Gestión de Cursos</h1>
      <p class="header-subtitle">
        Administra y supervisa todos los cursos académicos
      </p>
    </div>
  </header>

  <!-- Contenido Principal -->
  <div class="main-content">
    <div class="container">
      <!-- Controles -->
      <div class="controls-section">
        <div class="search-wrapper">
          <svg
            class="search-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            type="text"
            bind:value={searchTerm}
            placeholder="Buscar curso o profesor..."
            class="search-input"
          />
        </div>

        <div class="filter-wrapper">
          <select bind:value={nivelFiltro} class="nivel-select">
            <option value="todos">📚 Todos los niveles</option>
            <option value="inicial">🎨 Inicial</option>
            <option value="primaria">📖 Primaria</option>
            <option value="secundaria">🎓 Secundaria</option>
          </select>
        </div>

        <button on:click={() => (showCrear = true)} class="btn-crear">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Nuevo Curso
        </button>
      </div>

      <!-- Contenido Principal -->
      {#if loading}
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Cargando cursos...</p>
        </div>
      {:else if error}
        <div class="error-state">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <p>{error}</p>
        </div>
      {:else if cursosFiltrados.length === 0}
        <div class="empty-state">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path
              d="M12 6.5a9.77 9.77 0 0 1 8.82 5.5 9.77 9.77 0 0 1-17.64 0 9.77 9.77 0 0 1 8.82-5.5z"
            ></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
          <h3>No se encontraron cursos</h3>
          <p>Intenta ajustar los filtros o crea un nuevo curso</p>
        </div>
      {:else}
        <div class="grid">
          {#each cursosFiltrados as curso}
            <article class="card">
              <!-- Card Header -->
              <div class="card-header">
                <h3 class="curso-nombre">{curso.nombre_curso}</h3>
                <span class="badge badge-{curso.nivel}">
                  {curso.nivel === "inicial"
                    ? "INICIAL"
                    : curso.nivel === "primaria"
                      ? "PRIMARIA"
                      : "SECUNDARIA"}
                </span>
              </div>

              <!-- Card Body -->
              <div class="card-body">
                <div class="info-group">
                  <div class="info-item">
                    <svg
                      class="info-icon"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"
                      ></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                    <div class="info-content">
                      <span class="info-label">PROFESOR</span>
                      <span class="info-value">{curso.profesor_titular}</span>
                    </div>
                  </div>

                  <div class="info-item">
                    <svg
                      class="info-icon"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"
                      ></path>
                      <circle cx="9" cy="7" r="4"></circle>
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                      <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                    </svg>
                    <div class="info-content">
                      <span class="info-label">ESTUDIANTES</span>
                      <span class="info-value"
                        >{curso.total_estudiantes} estudiantes</span
                      >
                    </div>
                  </div>
                </div>
              </div>

              <!-- Card Actions -->
              <div class="card-actions">
                <button
                  on:click={() => abrirEditar(curso)}
                  class="btn-action btn-edit"
                >
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path
                      d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"
                    ></path>
                    <path
                      d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                    ></path>
                  </svg>
                  Editar
                </button>
                <button
                  on:click={() => deleteCurso(curso.id_curso)}
                  class="btn-action btn-delete"
                >
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path
                      d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
                    ></path>
                  </svg>
                  Eliminar
                </button>
              </div>
            </article>
          {/each}
        </div>
      {/if}
    </div>
  </div>

  <!-- Botón Flotante Mobile -->
  <button
    on:click={() => (showCrear = true)}
    class="fab"
    title="Crear nuevo curso"
    aria-label="Crear nuevo curso"
  >
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2.5"
    >
      <line x1="12" y1="5" x2="12" y2="19"></line>
      <line x1="5" y1="12" x2="19" y2="12"></line>
    </svg>
  </button>

  <!-- Modales -->
  {#if showCrear}
    <div class="overlay" on:click={() => (showCrear = false)}>
      <div class="modal" on:click|stopPropagation>
        <CrearCursos on:close={cerrarCrear} />
      </div>
    </div>
  {/if}

  {#if showEditar && cursoAEditar}
    <div class="overlay" on:click={cerrarEditar}>
      <div class="modal" on:click|stopPropagation>
        <EditarCursos curso={cursoAEditar} on:close={cerrarEditar} />
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
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter",
      "Roboto", sans-serif;
  }

  /* ============================================
     HEADER OSCURO
     ============================================ */
  .dark-header {
    background: linear-gradient(
      135deg,
      var(--nav) 0%,
      var(--nav-secondary) 100%
    );
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
     CONTROLES Y FILTROS
     ============================================ */
  .controls-section {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
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
    padding: 14px 16px 14px 48px;
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

  .filter-wrapper {
    flex-shrink: 0;
  }

  .nivel-select {
    padding: 14px 20px;
    border: 2px solid var(--muted);
    border-radius: 12px;
    background: #ffffff;
    font-size: 15px;
    font-weight: 500;
    color: var(--nav);
    min-width: 200px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .nivel-select:hover {
    border-color: #c8dce8;
  }

  .nivel-select:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(0, 207, 230, 0.1);
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
      order: 1;
    }

    .filter-wrapper {
      flex: 1;
      order: 2;
    }

    .nivel-select {
      width: 100%;
      min-width: auto;
    }

    .btn-crear {
      display: none;
    }
  }

  /* ============================================
     GRID DE CURSOS
     ============================================ */
  .grid {
    display: grid;
    gap: 20px;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }

  @media (max-width: 768px) {
    .grid {
      grid-template-columns: 1fr;
    }
  }

  /* ============================================
     CARDS DE CURSOS
     ============================================ */
  .card {
    background: #ffffff;
    border-radius: 16px;
    overflow: hidden;
    border: 2px solid var(--muted);
    box-shadow: 0 2px 8px rgba(13, 46, 83, 0.08);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .card:hover {
    transform: translateY(-4px);
    border-color: var(--accent);
    box-shadow:
      0 8px 24px rgba(0, 207, 230, 0.2),
      0 4px 12px rgba(13, 46, 83, 0.1);
  }

  /* Card Header */
  .card-header {
    padding: 20px 20px 16px;
    background: linear-gradient(
      135deg,
      var(--nav) 0%,
      var(--nav-secondary) 100%
    );
    border-bottom: 2px solid var(--nav-secondary);
  }

  .curso-nombre {
    font-size: 1.25rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 12px 0;
    line-height: 1.3;
  }

  /* Badges */
  .badge {
    display: inline-flex;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.5px;
  }

  .badge-inicial {
    background: #fbbf24;
    color: #78350f;
  }

  .badge-primaria {
    background: #60a5fa;
    color: #1e3a8a;
  }

  .badge-secundaria {
    background: #34d399;
    color: #064e3b;
  }

  /* Card Body */
  .card-body {
    padding: 20px;
    background: #ffffff;
  }

  .info-group {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .info-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
  }

  .info-icon {
    width: 18px;
    height: 18px;
    color: #6b8ba3;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .info-content {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
  }

  .info-label {
    font-size: 0.7rem;
    color: #8fa9be;
    font-weight: 600;
    letter-spacing: 0.5px;
  }

  .info-value {
    font-size: 0.9rem;
    color: var(--nav);
    font-weight: 600;
  }

  /* Card Actions */
  .card-actions {
    display: flex;
    border-top: 2px solid var(--muted);
  }

  .btn-action {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px;
    border: none;
    background: #ffffff;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-action svg {
    width: 16px;
    height: 16px;
  }

  .btn-edit {
    color: var(--accent);
    border-right: 2px solid var(--muted);
  }

  .btn-edit:hover {
    background: linear-gradient(180deg, #e6fbff 0%, #ccf7ff 100%);
    color: #00b8d4;
  }

  .btn-delete {
    color: #ef4444;
  }

  .btn-delete:hover {
    background: linear-gradient(180deg, #fef2f2 0%, #fee2e2 100%);
    color: #dc2626;
  }

  .btn-action:active {
    transform: scale(0.98);
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

  .error-state svg {
    color: #ef4444;
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
    to {
      transform: rotate(360deg);
    }
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
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
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

  /* ============================================
     RESPONSIVE ADICIONALES
     ============================================ */
  @media (max-width: 480px) {
    .card-header {
      padding: 16px;
    }

    .curso-nombre {
      font-size: 1.125rem;
    }

    .card-body {
      padding: 16px;
    }

    .btn-action {
      padding: 12px;
      font-size: 0.8125rem;
    }

    .stat-card {
      padding: 16px 24px;
    }

    .stat-value {
      font-size: 2rem;
    }
  }
</style>
