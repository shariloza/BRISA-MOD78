<script lang="ts">
  import { onMount } from "svelte";
  import Profesores from "./components/Profesor/Profesores.svelte";
  import Cursos from "./components/Cursos/Cursos.svelte";
  import Materias from "./components/Materias/Materias.svelte";
  import {
    Home,
    Users,
    BookOpen,
    Layers,
    LogOut,
  } from "lucide-svelte";
  import { writable } from "svelte/store";

  // =============== SIDEBAR ===============
  const abierto = writable(true);

  function toggleSidebar() {
    abierto.update((v) => !v);
  }

  // Items y vista asociada (solo dashboard/profesores/cursos/materias navegan)
  let currentView: 'dashboard' | 'profesores' | 'cursos' | 'materias' = 'dashboard';

  const menuItems = [
    { icon: Home, label: "Dashboard", view: 'dashboard' },
    { icon: Users, label: "Usuarios y Roles" },
    { icon: BookOpen, label: "Estudiantes" },
    { icon: BookOpen, label: "Profesores", view: 'profesores' },
    { icon: Layers, label: "Cursos", view: 'cursos' },
    { icon: Layers, label: "Materias", view: 'materias' },
    { icon: Layers, label: "Administrativos" },
    { icon: Layers, label: "Retiros Tempranos" },
    { icon: Layers, label: "Incidentes" },
    { icon: Layers, label: "Esquelas" },
    { icon: LogOut, label: "Cerrar Sesión" },
  ];

  function navigateTo(view: string) {
    if (!view) return;
    currentView = view as any;
    const path = view === 'dashboard' ? '/' : `/${view}`;
    history.pushState({ view }, '', path);
  }

  onMount(() => {
    // inicializar desde la ruta actual
    const p = window.location.pathname.replace(/\/+$/,'') || '/';
    if (p === '/' || p === '/dashboard') currentView = 'dashboard';
    else if (p.startsWith('/profesores')) currentView = 'profesores';
    else if (p.startsWith('/cursos')) currentView = 'cursos';
    else if (p.startsWith('/materias')) currentView = 'materias';

    const onPop = () => {
      const pp = window.location.pathname.replace(/\/+$/,'') || '/';
      if (pp === '/' || pp === '/dashboard') currentView = 'dashboard';
      else if (pp.startsWith('/profesores')) currentView = 'profesores';
      else if (pp.startsWith('/cursos')) currentView = 'cursos';
      else if (pp.startsWith('/materias')) currentView = 'materias';
    };
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  });
</script>

<div class="app">
  <!-- ====================== SIDEBAR ====================== -->
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
          <button class="toggle-btn-collapsed" on:click={toggleSidebar}>
            ❯
          </button>
        {/if}
      </div>

      {#if $abierto}
        <button class="toggle-btn" on:click={toggleSidebar}>❮</button>
      {/if}
    </div>

    <nav>
      {#each menuItems as item, i}
        <div
          class="menu-item"
          class:active={item.view ? currentView === item.view : (i === 3 && currentView === 'profesores')}
          on:click={() => {
            if (item.label === "Cerrar Sesión") {
              console.log("Cerrando sesión...");
              return;
            }
            if (item.view) {
              navigateTo(item.view);
              return;
            }
            console.log(item.label);
          }}
          role="button"
          tabindex="0"
        >
          <svelte:component this={item.icon} size="18" />
          {#if $abierto}
            <span class="label">{item.label}</span>
          {/if}
        </div>
      {/each}
    </nav>

    <div class="nav-spacer"></div>
  </aside>

  <!-- ====================== CONTENIDO PRINCIPAL ====================== -->
  <div class="main-wrap">
    <header class="topbar">
      <div class="controls"></div>
      <div class="top-actions">
        <!-- Puedes agregar un botón + Nueva Entidad aquí cuando lo necesites -->
        <div class="user">
          <div class="avatar">AM</div>
          <div class="user-info">
            <div class="name">Ana María López</div>
            <div class="role">Administrador</div>
          </div>
        </div>
      </div>
    </header>

    <main>
      {#if currentView === 'dashboard'}
        <section class="page-header">
          <h1>Dashboard</h1>
          <p>Descripción o instrucciones de esta sección</p>
        </section>
        <section class="panel">
          <div class="panel-header"><h3>Contenido</h3></div>
          <div class="empty-state"><p>Panel de inicio</p></div>
        </section>
      {:else if currentView === 'profesores'}
        <section class="panel">
          <Profesores />
        </section>
      {:else if currentView === 'cursos'}
        <section class="panel">
          <Cursos />
        </section>
      {:else if currentView === 'materias'}
        <section class="panel">
          <Materias />
        </section>
      {/if}
    </main>
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

  /* ====================== SIDEBAR ====================== */
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
    font-size: 1.1rem;
  }

  .brand-text .title {
    font-weight: 700;
    color: #e6f7fb;
  }

  .brand-text .subtitle {
    font-size: 0.75rem;
    color: #8fb9c6;
  }

  /* NAV: se ajusta overflow y padding para que el scrollbar no tape iconos */
  nav {
    display: flex;
    flex-direction: column;
    gap: 8px;
    overflow-y: auto;
    padding-right: 6px;
    scrollbar-width: thin;
  }

  /* make sure svg icons inherit color and have consistent size */
  .menu-item svg {
    stroke: currentColor;
    width: 20px;
    height: 20px;
    min-width: 20px;
    flex-shrink: 0;
    display: block;
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
  }

  .menu-item:hover {
    transform: translateX(4px);
    background: rgba(255, 255, 255, 0.05);
  }

  .menu-item.active {
    background: var(--accent);
    color: #042;
    box-shadow: 0 4px 12px rgba(2, 22, 30, 0.15);
  }

  /* active icons should also get high contrast */
  .menu-item.active svg {
    stroke: #042;
  }

  .menu-item .label {
    font-weight: 500;
    white-space: nowrap;
  }

  .nav-spacer {
    margin-top: auto;
  }

  .toggle-btn,
  .toggle-btn-collapsed {
    background: none;
    border: none;
    color: #cfeaf4;
    cursor: pointer;
    font-size: 18px;
  }

  .toggle-btn-collapsed:hover {
    color: var(--accent);
  }

  /* ====================== MAIN ====================== */
  .main-wrap {
    flex: 1;
    display: flex;
    flex-direction: column;
    margin-left: 260px;
    transition: all 0.3s ease-in-out;
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
    margin-top: 72px;
    overflow-y: auto;
    height: calc(100vh - 72px);
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
    color: #1e293b;
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #64748b;
  }

  /* ====================== SIDEBAR COLAPSADO: centrar iconos y ocultar labels ====================== */
  aside:not(.abierto) .menu-item {
    justify-content: center;
    padding: 12px 0;
  }

  aside:not(.abierto) .menu-item .label {
    display: none;
  }

  /* ====================== RESPONSIVE ====================== */
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
    .user-info {
      display: none;
    }

    /* ensure icons remain visible on small screens */
    .menu-item svg {
      width: 20px;
      height: 20px;
      min-width: 20px;
    }
  }

  @media (max-width: 480px) {
    .topbar {
      padding: 16px;
    }
  }
</style>
