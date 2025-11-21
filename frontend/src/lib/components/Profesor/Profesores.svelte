<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { Clock } from "lucide-svelte";
  import NuevoProfesor from "./NuevoProfesor.svelte";
  import EditarProfesores from "./EditarProfesores.svelte";

  // ==================== API ===========================
  const API_URL = "http://localhost:8000/api/profesores";
  const API_MATERIAS_URL = "http://localhost:8000/api/profesores/materias";
  const API_BLOQUES_URL = "http://localhost:8000/api/profesores";

  const POLLING_INTERVAL = 5000;
  const FAST_POLLING_INTERVAL = 2000;

  // ==================== TIPOS ====================
  type Materia = { id_materia: number; nombre_materia: string; nivel: string };
  type Profesor = {
    id?: number;
    id_persona?: number;
    nombres: string;
    apellido_paterno?: string;
    apellido_materno?: string;
    materias?: string[];
    cursos?: string[];
    cargaHoraria?: number;
    estado_laboral: string;
  };

  // ==================== ESTADO ====================
  let profesores: Profesor[] = [];
  let materias: Materia[] = [];
  let materiaSeleccionada = "todas";
  let searchQuery = "";
  let mostrarNuevo = false;
  let mostrarEditar = false;
  let profesorEditando: Profesor | null = null;
  let isLoading = false;
  let hasChanges = false;
  let polling: number | null = null;
  let cargas: { [key: number]: number } = {};

  // ==================== UTILIDADES ====================
  function hash(data: any) {
    return JSON.stringify(data)
      .split("")
      .reduce((a, b) => (a = (a << 5) - a + b.charCodeAt(0)) & a, 0)
      .toString();
  }

  function calcularHoras(inicio: string, fin: string): number {
    try {
      const [hi, mi] = inicio.split(":").map(Number);
      const [hf, mf] = fin.split(":").map(Number);
      return hf + mf / 60 - (hi + mi / 60);
    } catch {
      return 0;
    }
  }

  function initials(p: Profesor) {
    const a = p.apellido_paterno?.[0] || p.apellido_materno?.[0] || "";
    const n = p.nombres.split(" ")[0]?.[0] || "";
    return (a + n).toUpperCase() || "?";
  }

  function fullName(p: Profesor) {
    const ape = p.apellido_paterno || p.apellido_materno || "";
    return `${ape} ${p.nombres}`.trim() || "Sin nombre";
  }

  // ==================== CARGA DATOS ====================
  async function cargarCarga(id: number): Promise<number> {
    try {
      const res = await fetch(`${API_BLOQUES_URL}/${id}/bloques`);
      if (!res.ok) return 0;
      const bloques = await res.json();
      if (!Array.isArray(bloques)) return 0;
      return (
        Math.round(
          bloques.reduce(
            (t: number, b: any) => t + calcularHoras(b.hora_inicio, b.hora_fin),
            0,
          ) * 10,
        ) / 10
      );
    } catch {
      return 0;
    }
  }

  let lastHash = "";

  async function cargarProfesores(silent = false) {
    if (!silent) isLoading = true;
    try {
      const res = await fetch(API_URL);
      if (!res.ok) return;
      const data = await res.json();
      const newHash = hash(data);

      // Only update if raw data actually changed
      if (newHash !== lastHash) {
        lastHash = newHash;

        // 1. Fetch loads for the NEW data first
        await Promise.all(
          data.map(async (p: any) => {
            const id = p.id ?? p.id_persona;
            if (id) cargas[id] = await cargarCarga(id);
          }),
        );

        // 2. Merge loads into the new data
        const newProfesores = data.map((p: any) => ({
          ...p,
          cargaHoraria: cargas[p.id ?? p.id_persona ?? 0] || 0,
        }));

        // 3. Update state in one go to prevent flickering
        profesores = newProfesores;
        hasChanges = true;
      }
    } finally {
      if (!silent) isLoading = false;
      setTimeout(() => (hasChanges = false), 1000);
    }
  }

  async function cargarMaterias() {
    try {
      const res = await fetch(API_MATERIAS_URL);
      if (res.ok) materias = await res.json();
    } catch {}
  }

  async function refrescar(silent = false) {
    await Promise.all([cargarProfesores(silent), cargarMaterias()]);
  }

  function pollingStart(interval = POLLING_INTERVAL) {
    pollingStop();
    polling = setInterval(() => refrescar(true), interval) as any;
  }

  function pollingStop() {
    if (polling) clearInterval(polling);
    polling = null;
  }

  function pollingRapido() {
    pollingStop();
    pollingStart(FAST_POLLING_INTERVAL);
    setTimeout(() => pollingStart(POLLING_INTERVAL), 10000);
  }

  onMount(() => {
    refrescar();
    pollingStart();
    const vis = () => !document.hidden && refrescar(true);
    document.addEventListener("visibilitychange", vis);
    onDestroy(() => {
      pollingStop();
      document.removeEventListener("visibilitychange", vis);
    });
  });

  // ==================== ACCIONES ====================
  function abrirNuevo() {
    mostrarNuevo = true;
  }
  function abrirEditar(p: Profesor) {
    profesorEditando = p;
    mostrarEditar = true;
  }

  function cerrarForms() {
    mostrarNuevo = false;
    mostrarEditar = false;
    profesorEditando = null;
  }

  async function onSave(e: CustomEvent<Profesor>) {
    const saved = e.detail;
    const idx = profesores.findIndex(
      (p) => (p.id ?? p.id_persona) === (saved.id ?? saved.id_persona),
    );
    if (idx >= 0) profesores[idx] = saved;
    else profesores = [...profesores, saved];
    profesores = profesores;
    cerrarForms();
    await refrescar(true);
    pollingRapido();
  }

  // ==================== FILTROS ====================
  $: filtrados = profesores.filter((p) => {
    const q = searchQuery.toLowerCase();
    const okNombre = p.nombres.toLowerCase().includes(q);
    const okMateria =
      p.materias?.some((m) => m.toLowerCase().includes(q)) ?? false;
    const okCurso = p.cursos?.some((c) => c.toLowerCase().includes(q)) ?? false;
    const okMateriaSelect =
      materiaSeleccionada === "todas" ||
      p.materias?.includes(materiaSeleccionada);
    return (okNombre || okMateria || okCurso) && okMateriaSelect;
  });
</script>

{#if mostrarNuevo}
  <NuevoProfesor on:save={onSave} on:cancel={cerrarForms} />
{:else if mostrarEditar && profesorEditando}
  <EditarProfesores
    profesor={profesorEditando}
    on:save={onSave}
    on:cancel={cerrarForms}
  />
{:else}
  <div class="profesores-container panel">
    <!-- TÍTULO -->
    <div class="title-section">
      <h1>Profesores y Materias</h1>
      <p>Gestiona la información del cuerpo docente</p>
    </div>

    <!-- BOTÓN A LA DERECHA (DEBAJO DEL TÍTULO) -->
    <div class="button-row">
      <button class="btn-nuevo" on:click={abrirNuevo}>
        + Nuevo Profesor
      </button>
    </div>

    <!-- FILTROS -->
    <div class="filters">
      <input
        type="text"
        placeholder="Buscar por nombre o materia..."
        bind:value={searchQuery}
      />
      <div class="materia-filter">
        <select bind:value={materiaSeleccionada}>
          <option value="todas">Todas las materias</option>
          {#each materias as m}
            <option value={m.nombre_materia}>{m.nombre_materia}</option>
          {/each}
        </select>
        <span class="count">({materias.length} materias)</span>
      </div>
    </div>

    <!-- GRID DE PROFESORES -->
    <div class="grid" class:updating={hasChanges}>
      {#each filtrados as p (p.id ?? p.id_persona ?? Math.random())}
        <div class="card" on:click={() => abrirEditar(p)}>
          <div class="avatar-circle">{initials(p)}</div>

          <div class="info">
            <div class="name-line">
              <h3>{fullName(p)}</h3>

              {#if p.materias?.length}
                <span class="materia-pill">{p.materias.join(", ")}</span>
              {/if}
            </div>

            {#if p.cursos?.length}
              <div class="cursos">
                {#each p.cursos.slice(0, 2) as curso}
                  <span class="curso-tag">{curso}</span>
                {/each}
                {#if p.cursos.length > 2}
                  <span class="curso-tag">+{p.cursos.length - 2}</span>
                {/if}
              </div>
            {/if}

            <div class="footer">
              <div class="carga">
                <Clock size={14} />
                <span>{p.cargaHoraria ?? 0} h/sem</span>
              </div>

              <span
                class="estado {p.estado_laboral?.toLowerCase() === 'activo'
                  ? 'activo'
                  : 'inactivo'}"
              >
                {p.estado_laboral || "N/A"}
              </span>
            </div>
          </div>
        </div>
      {/each}

      {#if filtrados.length === 0}
        <p class="empty">No se encontraron profesores.</p>
      {/if}
    </div>
  </div>
{/if}

<style>
  :root {
    --cyan: #00cfe6;
    --text: #1e293b;
    --muted: #64748b;
  }

  /* .profesores-container removed */

  /* ==================== TÍTULO ==================== */
  .title-section {
    margin-bottom: 8px;
  }

  .title-section h1 {
    font-size: 1.8rem;
    color: var(--text);
    margin: 0 0 6px;
  }

  .title-section p {
    color: black;
    margin: 0;
  }

  /* ==================== BOTÓN A LA DERECHA ==================== */
  .button-row {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 24px;
  }

  .btn-nuevo {
    background: var(--cyan);
    color: white;
    border: none;
    padding: 10px 22px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: 0.2s ease;
    box-shadow: 0 4px 10px rgba(0, 207, 230, 0.3);
  }

  .btn-nuevo:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(0, 207, 230, 0.4);
  }

  /* ==================== FILTROS ==================== */
  .filters {
    display: flex;
    gap: 16px;
    margin-bottom: 28px;
    align-items: center;
    flex-wrap: wrap;
  }

  .filters input {
    flex: 1;
    min-width: 280px;
    padding: 12px 18px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    background: white;
    font-size: 0.95rem;
    color: black;
  }

  .filters input:focus {
    outline: none;
    border-color: var(--cyan);
  }

  .materia-filter {
    display: flex;
    align-items: center;
    gap: 10px;
    background: white;
    padding: 6px 14px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
  }

  .materia-filter select {
    border: none;
    background: transparent;
    font-size: 0.95rem;
    cursor: pointer;
    color: black;
  }

  .materia-filter .count {
    color: var(--muted);
    font-size: 0.85rem;
    color: black;
  }

  /* ==================== GRID ==================== */
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    transition: opacity 0.3s;
  }

  .grid.updating {
    opacity: 0.6;
  }

  /* ==================== CARD ==================== */
  .card {
    background: white;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 3px 14px rgba(0, 0, 0, 0.06);
    border: 1px solid #f1f5f9;
    display: flex;
    gap: 16px;
    cursor: pointer;
    transition: 0.25s;
  }

  .card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.12);
  }

  .avatar-circle {
    width: 52px;
    height: 52px;
    background: #c4b5fd;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.2rem;
    flex-shrink: 0;
  }

  .name-line {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
    flex-wrap: wrap;
  }

  .name-line h3 {
    margin: 0;
    font-size: 1rem;
    color: var(--text);
  }

  .materia-pill {
    background: linear-gradient(135deg, var(--cyan), #00a6b8);
    color: white;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .cursos {
    display: flex;
    gap: 6px;
    margin-bottom: 10px;
    flex-wrap: wrap;
  }

  .curso-tag {
    background: #f1f5f9;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    color: black;
  }

  .footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 6px;
  }

  .carga {
    display: flex;
    align-items: center;
    gap: 6px;
    color: black;
    font-size: 0.85rem;
  }

  .estado {
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .estado.activo {
    background: #ecfdf5;
    color: #16a34a;
  }

  .estado.inactivo {
    background: #fffbeb;
    color: #d97706;
  }

  .empty {
    grid-column: 1 / -1;
    text-align: center;
    color: var(--muted);
    padding: 30px;
    font-size: 1rem;
  }
  .panel {
    background: #fff;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 6px 18px rgba(25, 40, 60, 0.02);
    border: 1px solid #eef6fa;
  }
</style>
