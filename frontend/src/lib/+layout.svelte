<script lang="ts">
  import ProfesorDetalle from "./components/ProfesorDetalle.svelte";
  import NuevoProfesor from "./components/NuevoProfesor.svelte";
  import EditarProfesores from "./components/EditarProfesores.svelte";
  import {
    Home,
    Users,
    BookOpen,
    Layers,  
    Bell,
    Search,
    LogOut,
    Clock,
    RefreshCw,
  } from "lucide-svelte";
  import { writable } from "svelte/store";
  import { onMount, onDestroy } from "svelte";

  const API_URL = "http://localhost:8000/api/profesores";
  const API_MATERIAS_URL = "http://localhost:8000/api/profesores/materias";
  const API_BLOQUES_URL = "http://localhost:8000/api/profesores";
  
  // Configuración de polling (actualización automática cada X segundos)
  const POLLING_INTERVAL = 5000; // 5 segundos
  const FAST_POLLING_INTERVAL = 2000; // 2 segundos (después de cambios)

  // Sidebar
  let abierto = writable(true);
  function toggleSidebar() {
    abierto.update((v) => !v);
  }

  const menuItems = [
    { icon: Home, label: "Dashboard" },
    { icon: Users, label: "Usuarios y Roles" },
    { icon: BookOpen, label: "Estudiantes" },
    { icon: BookOpen, label: "Profesores" },
    { icon: Layers, label: "Cursos" },
    { icon: Layers, label: "Administrativos" },
    { icon: Layers, label: "Retiros Tempranos" },
    { icon: Layers, label: "Incidentes" },
    { icon: Layers, label: "Esquelas" },
    { icon: LogOut, label: "Cerrar Sesión" },
  ];

  // Profesores
  type Materia = {
    id_materia: number;
    nombre_materia: string;
    nivel: string;
  };

  type Profesor = {
    id?: number;
    id_persona?: number;
    nombres: string;
    apellido_paterno?: string;
    apellido_materno?: string;
    ci?: string;
    fecha_nacimiento?: string;
    sexo?: string;
    direccion?: string;
    telefono?: string;
    email?: string;
    especialidad?: string;
    titulo_academico?: string;
    años_experiencia?: number;
    fecha_contratacion?: string;
    estado_laboral: string;
    cargaHoraria?: number;
    materias?: string[];
    cursos?: string[];
  };

  let profesores: Profesor[] = [];
  let materias: Materia[] = [];
  let materiaSeleccionada: string = "todas";

  let profesorSeleccionado: Profesor | null = null;
  let searchQuery = "";
  let mostrarNuevoProfesor = false;
  let mostrarEditarProfesor = false;
  let profesorEditando: Profesor | null = null;

  // Variables para reactividad
  let pollingInterval: number | null = null;
  let isLoading = false;
  let lastUpdate = new Date();
  let isRefreshing = false;
  let hasChanges = false;

  // Hash simple para detectar cambios
  function generateHash(data: any): string {
    return JSON.stringify(data).split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0).toString();
  }

  let profesoresHash = "";
  let materiasHash = "";
  let cargasHorarias: { [key: number]: number } = {}; // Almacenar carga horaria por id_profesor

  // Función para calcular horas entre dos tiempos
  function calcularHoras(hora_inicio: string, hora_fin: string): number {
    try {
      const inicio = new Date(`1970-01-01T${hora_inicio}`);
      const fin = new Date(`1970-01-01T${hora_fin}`);
      const diff = fin.getTime() - inicio.getTime();
      return diff / (1000 * 60 * 60); // Convertir a horas
    } catch {
      return 0;
    }
  }

  // Función para cargar bloques y calcular carga horaria de un profesor
  async function cargarCargaHoraria(idProfesor: number): Promise<number> {
    try {
      const response = await fetch(`${API_BLOQUES_URL}/${idProfesor}/bloques`);
      if (!response.ok) return 0;
      
      const bloques = await response.json();
      if (!Array.isArray(bloques)) return 0;
      
      // Sumar todas las horas de los bloques
      const totalHoras = bloques.reduce((total, bloque) => {
        const horas = calcularHoras(bloque.hora_inicio, bloque.hora_fin);
        return total + horas;
      }, 0);
      
      return Math.round(totalHoras * 10) / 10; // Redondear a 1 decimal
    } catch (error) {
      console.error(`Error cargando bloques para profesor ${idProfesor}:`, error);
      return 0;
    }
  }

  // Función para cargar profesores
  async function cargarProfesores(silent = false) {
    try {
      if (!silent) isLoading = true;
      
      const response = await fetch(API_URL);
      if (!response.ok) throw new Error("Error cargando profesores");
      
      const data = await response.json();
      const newHash = generateHash(data);
      
      // Solo actualizar si hay cambios
      if (newHash !== profesoresHash) {
        profesores = data;
        profesoresHash = newHash;
        hasChanges = true;
        lastUpdate = new Date();
        
        // Cargar carga horaria para cada profesor en paralelo
        const cargaPromises = profesores.map(async (profesor) => {
          const idProfesor = profesor.id ?? profesor.id_persona;
          if (idProfesor) {
            const carga = await cargarCargaHoraria(idProfesor);
            cargasHorarias[idProfesor] = carga;
          }
        });
        
        await Promise.all(cargaPromises);
        
        // Actualizar profesores con la carga horaria
        profesores = profesores.map(p => ({
          ...p,
          cargaHoraria: cargasHorarias[p.id ?? p.id_persona] || 0
        }));
        
        // Si había un profesor seleccionado, actualizarlo
        if (profesorEditando) {
          const updated = profesores.find((p: Profesor) => 
            (p.id ?? p.id_persona) === (profesorEditando.id ?? profesorEditando.id_persona)
          );
          if (updated) profesorEditando = updated;
        }
      }
      
      return data;
    } catch (error) {
      console.error("Error cargando profesores:", error);
    } finally {
      if (!silent) isLoading = false;
      setTimeout(() => { hasChanges = false; }, 1000);
    }
  }

  // Función para cargar materias
  async function cargarMaterias(silent = false) {
    try {
      const response = await fetch(API_MATERIAS_URL);
      if (!response.ok) throw new Error("Error cargando materias");
      
      const data = await response.json();
      const newHash = generateHash(data);
      
      if (newHash !== materiasHash) {
        materias = data;
        materiasHash = newHash;
      }
      
      return data;
    } catch (error) {
      console.error("Error cargando materias:", error);
    }
  }

  // Función para refrescar todo
  async function refrescarDatos(silent = false) {
    if (isRefreshing && !silent) return;
    
    isRefreshing = true;
    await Promise.all([
      cargarProfesores(silent),
      cargarMaterias(silent)
    ]);
    isRefreshing = false;
  }

  // Iniciar polling automático
  function iniciarPolling(intervalo = POLLING_INTERVAL) {
    detenerPolling();
    pollingInterval = setInterval(() => {
      refrescarDatos(true);
    }, intervalo) as unknown as number;
  }

  // Detener polling
  function detenerPolling() {
    if (pollingInterval !== null) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  }

  // Polling rápido temporal después de cambios
  function activarPollingRapido(duracion = 10000) {
    detenerPolling();
    iniciarPolling(FAST_POLLING_INTERVAL);
    
    setTimeout(() => {
      detenerPolling();
      iniciarPolling(POLLING_INTERVAL);
    }, duracion);
  }

  onMount(async () => {
    await refrescarDatos();
    iniciarPolling();
    
    // Refrescar al volver al tab
    document.addEventListener('visibilitychange', handleVisibilityChange);
  });

  onDestroy(() => {
    detenerPolling();
    document.removeEventListener('visibilitychange', handleVisibilityChange);
  });

  function handleVisibilityChange() {
    if (!document.hidden) {
      refrescarDatos(true);
    }
  }

  // Refrescar manualmente
  async function refrescarManual() {
    await refrescarDatos(false);
  }

  async function abrirEdicionProfesor(p?: Profesor) {
    if (!p) {
      profesorEditando = null;
      mostrarNuevoProfesor = true;
      return;
    }

    profesorEditando = p;
    mostrarEditarProfesor = true;
  }

  function volverALista() {
    profesorSeleccionado = null;
    searchQuery = "";
  }

  function abrirNuevoProfesor() {
    abrirEdicionProfesor(null);
  }

  async function onSaveProfesor(event: CustomEvent) {
    const saved = event.detail;
    const savedId = saved.id ?? saved.id_persona ?? null;

    // Optimistic update
    if (savedId != null) {
      const idx = profesores.findIndex(
        (p) => (p.id ?? p.id_persona) == savedId,
      );
      if (idx !== -1) {
        profesores = profesores.map((p, i) => (i === idx ? saved : p));
      } else {
        profesores = [...profesores, saved];
      }
    } else {
      profesores = [...profesores, saved];
    }

    mostrarNuevoProfesor = false;
    profesorEditando = null;
    
    // Refrescar inmediatamente y activar polling rápido
    await refrescarDatos(true);
    activarPollingRapido();
  }

  function onCancelNuevoProfesor() {
    mostrarNuevoProfesor = false;
    profesorEditando = null;
  }

  function onCancelEditarProfesor() {
    mostrarEditarProfesor = false;
    profesorEditando = null;
  }

  async function onSaveEditarProfesor(event: CustomEvent) {
    const saved = event.detail;
    const savedId = saved.id ?? saved.id_persona ?? null;

    // Optimistic update
    if (savedId != null) {
      const idx = profesores.findIndex(
        (p) => (p.id ?? p.id_persona) == savedId,
      );
      if (idx !== -1) {
        profesores = profesores.map((p, i) => (i === idx ? saved : p));
      } else {
        profesores = [...profesores, saved];
      }
    } else {
      profesores = [...profesores, saved];
    }

    mostrarEditarProfesor = false;
    profesorEditando = null;
    
    // Refrescar inmediatamente y activar polling rápido
    await refrescarDatos(true);
    activarPollingRapido();
  }

  $: profesoresFiltrados = profesores.filter((p) => {
    const query = searchQuery.toLowerCase();
    const cumpleBusqueda =
      p.nombres.toLowerCase().includes(query) ||
      (p.materias && p.materias.some((m) => m.toLowerCase().includes(query))) ||
      (p.cursos && p.cursos.some((c) => c.toLowerCase().includes(query)));

    const cumpleMateria =
      materiaSeleccionada === "todas" ||
      (p.materias && p.materias.includes(materiaSeleccionada));

    return cumpleBusqueda && cumpleMateria;
  });

  function getSurname(p: any) {
    const candidates = [
      p.apellido_paterno,
      p.apellido_materno,
      p.apellido,
      p.apellidos,
      p.last_name,
      p.lastname,
      p.surname,
    ].filter(Boolean);
    if (candidates.length) return candidates[0].toString().trim();

    const nombresRaw = (p.nombres || p.name || p.nombre || "").toString().trim();
    if (nombresRaw) {
      const parts = nombresRaw.split(/\s+/);
      if (parts.length > 1) return parts[parts.length - 1];
    }
    return "";
  }

  function getFirstNames(p: any) {
    const nombresRaw = (p.nombres || p.name || p.nombre || "").toString().trim();
    if (!nombresRaw) return "";
    const parts = nombresRaw.split(/\s+/);
    if (parts.length > 1) return parts.slice(0, parts.length - 1).join(" ");
    return nombresRaw;
  }

  function buildDisplayName(p: any) {
    const surname = getSurname(p);
    const first = getFirstNames(p);
    if (surname && first) return `${surname} ${first}`;
    if (surname) return surname;
    return first || p.fullName || p.nombre_completo || "";
  }

  function buildInitials(p: any) {
    const surname = getSurname(p);
    const first = getFirstNames(p);
    let a = "",
      b = "";
    if (surname) a = surname[0];
    if (first) b = first.split(/\s+/)[0]?.[0] ?? "";
    const letters = (a + b).toUpperCase();
    return letters || ((p.nombres || p.name || "")[0] || "?").toUpperCase();
  }

  function formatTime(date: Date): string {
    return date.toLocaleTimeString('es-BO', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  }
</script>

<div class="app">
  <!-- Sidebar -->
  <aside class:abierto={$abierto}>
    <div class="brand">
      <div class="brand-left">
        {#if $abierto}
          <div class="logo-mark">BR</div>
          <div class="brand-text">
            <div class="title">BRISA</div>
            <div class="subtitle">Sistema Escolar</div>
          </div>
        {:else}
          <button class="toggle-btn-collapsed" on:click={toggleSidebar}
            >❯</button
          >
        {/if}
      </div>
      {#if $abierto}
        <button class="toggle-btn" on:click={toggleSidebar}>❮</button>
      {/if}
    </div>

    <nav>
      {#each menuItems as item, i}
        <div
          class="menu-item {i === 3 ? 'active' : ''}"
          on:click={() => {
            if (item.label === "Cerrar Sesión") {
              console.log("Cerrando sesión...");
            }
          }}
          role="button"
          tabindex="0"
        >
          <item.icon size="18" />
          {#if $abierto}<span class="label">{item.label}</span>{/if}
        </div>
      {/each}
    </nav>

    <div class="nav-spacer"></div>
  </aside>

  <!-- Contenido principal -->
  <div class="main-wrap">
    {#if mostrarNuevoProfesor}
      <NuevoProfesor
        profesorInit={null}
        on:save={onSaveProfesor}
        on:cancel={onCancelNuevoProfesor}
      />
    {:else if mostrarEditarProfesor}
      <EditarProfesores
        profesor={profesorEditando}
        on:save={onSaveEditarProfesor}
        on:cancel={onCancelEditarProfesor}
      />
    {:else}
      <header class="topbar">
        <div class="controls"></div>

        <div class="top-actions">
          <button class="new-btn" on:click={abrirNuevoProfesor}>
            + Nuevo Profesor
          </button>
          <div class="user">
            <div class="avatar">AM</div>
            <div class="user-info">
              <div class="name">Ana María López</div>
              <div class="role">Administrador</div>
            </div>
          </div>
        </div>
      </header>

      <main class:expanded={$abierto}>
        {#if !profesorSeleccionado}
          <section class="page-header">
            <h1>Profesores y Materias</h1>
            <p>Gestiona la información del cuerpo docente</p>

            <div class="controls">
              <input
                class="filter-search"
                type="text"
                placeholder="Buscar por nombre o materia..."
                bind:value={searchQuery}
              />
              <div class="right-controls">
                <select class="filter-select" bind:value={materiaSeleccionada}>
                  <option value="todas">Todas las materias</option>
                  {#each materias as materia}
                    <option value={materia.nombre_materia}
                      >{materia.nombre_materia}</option
                    >
                  {/each}
                </select>
                <span
                  style="color: #64748b; font-size: 0.85rem; margin-left: 8px;"
                >
                  ({materias.length} materias)
                </span>
              </div>
            </div>
          </section>

          <section class="panel">
            <div class="panel-header">
              <h3>Lista de Profesores ({profesoresFiltrados.length})</h3>
              {#if isLoading}
                <span class="loading-indicator">Cargando...</span>
              {/if}
            </div>

            <div class="grid-profesores" class:updating={hasChanges}>
              {#each profesoresFiltrados as profesor (profesor.id ?? profesor.ci)}
                <div
                  class="card"
                  on:click={() => abrirEdicionProfesor(profesor)}
                  role="button"
                  tabindex="0"
                >
                  <div class="avatar">
                    {buildInitials(profesor)}
                  </div>

                  <div class="content">
                    <div class="top">
                      <div class="nombre">{buildDisplayName(profesor)}</div>
                       <span class="materia-pill">
                        {#if profesor.materias && profesor.materias.length}
                          {profesor.materias.join(", ")}
                        {/if}
                      </span>
                    </div>

                    <div class="curso-row">
                      {#if profesor.cursos?.length}
                        {#each profesor.cursos.slice(0, 2) as curso}
                          <span class="curso-pill">{curso}</span>
                        {/each}
                        {#if profesor.cursos.length > 2}
                          <span class="curso-pill"
                            >+{profesor.cursos.length - 2}</span
                          >
                        {/if}
                      {/if}
                    </div>

                    <hr class="divider" />

                    <div class="footer">
                      <div class="left">
                        <Clock size="16" color="#64748b" />
                        <span class="carga">
                          {profesor.cargaHoraria ?? 0}h/sem
                        </span>
                      </div>
                      <div class="right">
                        <span
                          class="estado-pill {profesor.estado_laboral?.toLowerCase() ===
                          'activo'
                            ? 'activo'
                            : 'inactivo'}"
                        >
                          {profesor.estado_laboral || "N/A"}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              {/each}
              {#if profesoresFiltrados.length === 0}
                <p>No se encontraron profesores.</p>
              {/if}
            </div>
          </section>
        {:else}
          <ProfesorDetalle profesor={profesorSeleccionado} />
          <button class="volver-btn" on:click={volverALista}
            >← Volver a la lista</button
          >
        {/if}
      </main>
    {/if}
  </div>
</div>

<style>
  :root {
    --nav: #0d2e53;
    --nav-secondary: #07264a;
    --accent: #00cfe6;
    --muted: #e9f0f4;
  }

  .app {
    display: flex;
    width: 100%;
    height: 100vh;
    font-family: "Poppins", sans-serif;
    background: #f6fafc;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    overflow: hidden;
  }

  aside {
    background: var(--nav);
    color: #cfeaf4;
    width: 260px;
    display: flex;
    flex-direction: column;
    padding: 16px 12px;
    gap: 14px;
    height: 100vh;
    position: fixed;
    left: 0;
    top: 0;
    z-index: 20;
    transition: all 0.3s ease-in-out;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  }
  aside:not(.abierto) {
    width: 50px;
    transform: translateX(0);
  }

  .brand {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }
  .brand-left {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
  }
  .logo-mark {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background: var(--accent);
    color: #042;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
  }
  .brand-text .title {
    font-weight: 700;
    color: #e6f7fb;
  }
  .brand-text .subtitle {
    font-size: 0.75rem;
    color: #8fb9c6;
  }

  nav {
    display: flex;
    flex-direction: column;
    gap: 8px;
    overflow: auto;
    padding-right: 6px;
  }
  .menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 10px;
    color: #bcdedf;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    transform-origin: left;
    user-select: none;
  }
  .menu-item:hover {
    transform: translateX(4px);
    background: rgba(255, 255, 255, 0.05);
  }
  .menu-item.active {
    background: var(--accent);
    color: #042;
    box-shadow: 0 4px 12px rgba(2, 22, 30, 0.15);
    animation: pulseActive 2s infinite;
  }
  .menu-item .label {
    font-weight: 500;
  }

  .nav-spacer {
    margin-top: auto;
    padding: 10px 6px;
  }

  .main-wrap {
    flex: 1;
    display: flex;
    flex-direction: column;
    margin-left: 260px;
    transition: all 0.3s ease-in-out;
    min-height: 100vh;
    background: #f6fafc;
  }
  aside:not(.abierto) + .main-wrap {
    margin-left: 90px;
  }

  .topbar {
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 28px;
    background: #f6fafc;
    border-bottom: 1px solid #eef6f9;
    position: fixed;
    top: 0;
    right: 0;
    left: 260px;
    z-index: 10;
    transition: all 0.3s ease-in-out;
  }
  aside:not(.abierto) ~ .main-wrap .topbar {
    left: 90px;
  }

  .top-actions {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .new-btn {
    background: var(--accent);
    color: #fff;
    border: none;
    padding: 10px 14px;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s ease;
  }

  .new-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 207, 230, 0.3);
  }

  .user {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .user .avatar {
    width: 40px;
    height: 40px;
    border-radius: 999px;
    background: #9aa9ff;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
  }
  .user-info .name {
    font-weight: 600;
    color: #1e293b;
  }
  .user-info .role {
    font-size: 0.8rem;
    color: #6b7f86;
  }

  main {
    padding: 96px 36px 24px;
    height: calc(100vh - 72px);
    margin-top: 72px;
    overflow-y: auto;
  }
  .page-header h1 {
    margin: 0;
    font-size: 1.6rem;
    color: #1e293b;
  }
  .page-header p {
    margin: 6px 0 18px 0;
    color: #6b7f86;
  }
  .controls {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 18px;
  }
  .filter-search {
    flex: 1;
    padding: 12px 14px;
    border-radius: 12px;
    border: 1px solid #e7eef2;
    background: #fff;
    color: #1e293b;
    font-size: 0.95rem;
    transition: all 0.2s ease;
  }

  .filter-search:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(0, 207, 230, 0.1);
  }

  .filter-search::placeholder {
    color: #94a3b8;
  }

  .filter-select {
    padding: 10px 14px;
    border-radius: 10px;
    background: #ffffff;
    border: 1px solid #e7eef2;
    color: #000000;
    cursor: pointer;
    font-family: "Poppins", sans-serif;
    font-size: 0.95rem;
    font-weight: 500;
    min-width: 200px;
    transition: all 0.2s ease;
  }

  .filter-select:focus {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
    border-color: var(--accent);
  }

  .panel {
    background: #fff;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 6px 18px rgba(25, 40, 60, 0.02);
    border: 1px solid #eef6fa;
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
  }

  .panel-header h3 {
    margin: 0;
  }

  .loading-indicator {
    font-size: 0.85rem;
    color: var(--accent);
    font-weight: 500;
  }

  .grid-profesores {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 14px;
    transition: opacity 0.3s ease;
  }

  .grid-profesores.updating {
    animation: fadeIn 0.5s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0.7; }
    to { opacity: 1; }
  }

  .card {
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #e6eef6;
    display: flex;
    gap: 16px;
    align-items: flex-start;
    transition: all 0.2s ease;
    cursor: pointer;
  }
  .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }

  .avatar {
    width: 48px;
    height: 48px;
    min-width: 48px;
    border-radius: 50%;
    background: #9aa9ff;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.9rem;
  }

  .content {
    flex: 1;
    min-width: 0;
    overflow: hidden;
  }

  .top {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .nombre {
    font-weight: 600;
    color: #1e293b;
    font-size: 0.95rem;
    white-space: normal;
    overflow: visible;
    text-overflow: unset;
  }

  .materia-pill {
    background: linear-gradient(180deg, #00cfe6, #00bcd4);
    color: #fff;
    padding: 6px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    box-shadow: 0 1px 0 rgba(0, 0, 0, 0.03);
  }

  .curso-row {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-top: 6px;
  }

  .curso-pill {
    font-size: 0.75rem;
    color: #3b82f6;
    border: 1px solid #d0e6ff;
    background: #fff;
    padding: 6px 10px;
    border-radius: 999px;
  }

  .divider {
    border: none;
    height: 1px;
    background: #eef4fa;
    margin: 6px 0;
  }

  .footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    font-size: 0.85rem;
    color: #64748b;
  }

  .left {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #64748b;
  }

  .carga {
    margin-left: 6px;
    font-weight: 600;
  }

  .estado-pill {
    padding: 6px 10px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.8rem;
    border: 1px solid transparent;
  }
  .estado-pill.activo {
    background: #e6fff7;
    color: #00a65a;
    border-color: rgba(0, 166, 90, 0.12);
  }
  .estado-pill.inactivo {
    background: #fff6e6;
    color: #ff9800;
    border-color: rgba(255, 152, 0, 0.12);
  }

  .right-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  @media (max-width: 1200px) {
    .grid-profesores {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  
  @media (max-width: 768px) {
    aside {
      width: 90px;
    }

    .main-wrap {
      margin-left: 90px;
    }

    .topbar {
      left: 90px;
    }

    .brand-text,
    .menu-item .label {
      display: none;
    }

    .grid-profesores {
      grid-template-columns: 1fr;
    }

    .top-actions {
      gap: 8px;
    }

    .user-info {
      display: none;
    }
  }

  @media (max-width: 480px) {
    .top {
      flex-direction: column;
      align-items: flex-start;
      gap: 6px;
    }

    .curso-row {
      flex-wrap: wrap;
    }
  }

  .volver-btn {
    margin-top: 18px;
    padding: 10px 14px;
    border-radius: 10px;
    border: none;
    background: #00bcd4;
    color: #fff;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .volver-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 188, 212, 0.3);
  }

  .toggle-btn {
    background: none;
    border: none;
    color: #cfeaf4;
    cursor: pointer;
    font-size: 18px;
  }
  .toggle-btn-collapsed {
    background: none;
    border: none;
    color: #cfeaf4;
    cursor: pointer;
    font-size: 18px;
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease-in-out;
  }

  .toggle-btn-collapsed:hover {
    color: var(--accent);
    transform: translateX(2px);
  }

  @keyframes pulseActive {
    0% {
      box-shadow: 0 0 0 0 rgba(0, 207, 230, 0.4);
    }
    70% {
      box-shadow: 0 0 0 10px rgba(0, 207, 230, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(0, 207, 230, 0);
    }
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0;
    border-bottom: 1px solid #eef6f9;
    margin-bottom: 24px;
  }

  .icon-title {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .icon {
    font-size: 28px;
    color: var(--accent);
  }

  h2 {
    margin: 0;
    font-size: 1.4rem;
    color: #1e293b;
  }

  p {
    margin: 4px 0 0 0;
    color: #6b7f86;
    font-size: 0.9rem;
  }

  .actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .btn-primary {
    background: var(--accent);
    color: #fff;
    border: none;
    padding: 10px 14px;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
  }

  .btn-outline {
    background: none;
    border: 1px solid var(--accent);
    color: var(--accent);
    padding: 10px 14px;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 500;
  }
</style>