<script lang="ts">
  import { Phone, Mail, Edit } from "lucide-svelte";

  export let profesor: {
    nombre: string;
    materia: string;
    estado: string;
    experiencia: string;
    cargaHoraria: string;
    correo: string;
    telefono: string;
    cursos: string[];
  };

  let tab = "info";
</script>

<div class="profesor-detalle">
  <!-- Encabezado -->
  <div class="header">
    <div class="avatar">
      {profesor.nombre
        .split(" ")
        .slice(0, 2)
        .map((n) => n[0])
        .join("")
        .toUpperCase()}
    </div>

    <div class="info">
      <h2>{profesor.nombre}</h2>
      <div class="tags">
        <span class="badge">{profesor.materia}</span>
        <span class="status">{profesor.estado}</span>
      </div>
    </div>

    <button class="edit-btn"><Edit size={16} style="vertical-align:middle; margin-right:8px"/>Editar Perfil</button>
  </div>

  <!-- Tabs -->
  <div class="tabs">
    <button class:active={tab === "info"} on:click={() => (tab = "info")}
      >Información</button
    >
    <button class:active={tab === "horario"} on:click={() => (tab = "horario")}
      >Horario</button
    >
  </div>

  <!-- Contenido -->
  {#if tab === "info"}
    <div class="content">
      <div class="info-row">
        <div>
          <p class="label">Experiencia</p>
          <p class="value">{profesor.experiencia}</p>
        </div>
        <div>
          <p class="label">Carga Horaria</p>
          <p class="value">{profesor.cargaHoraria}</p>
        </div>
      </div>

      <div class="card">
        <div class="stat-icon-wrapper">
          <Mail size={24} color="#3b82f6" />
        </div>
        <div>
          <p class="label">Correo Electrónico</p>
          <p class="value">{profesor.correo}</p>
        </div>
      </div>

      <div class="card">
        <div class="stat-icon-wrapper">
          <Phone size={24} color="#3b82f6" />
        </div>
        <div>
          <p class="label">Teléfono</p>
          <p class="value">{profesor.telefono}</p>
        </div>
      </div>

      <div class="cursos">
        <p class="label">Cursos Asignados</p>
        <div class="chips">
          {#each profesor.cursos as curso}
            <span>{curso}</span>
          {/each}
        </div>
      </div>
    </div>
  {:else}
    <div class="content">
      <h3 class="horario-title">Horario Semanal</h3>

      <div class="dia-section">
        <h4>Lunes</h4>
        <div class="horario-item">
          <span class="tiempo">8:00 - 9:00:</span>
          <span class="clase">5to A</span>
        </div>
        <div class="horario-item">
          <span class="tiempo">9:00 - 10:00:</span>
          <span class="clase">5to B</span>
        </div>
        <div class="horario-item">
          <span class="tiempo">11:00 - 12:00:</span>
          <span class="clase">6to A</span>
        </div>
      </div>

      <div class="dia-section">
        <h4>Martes</h4>
        <div class="horario-item">
          <span class="tiempo">8:00 - 9:00:</span>
          <span class="clase">5to A</span>
        </div>
        <div class="horario-item">
          <span class="tiempo">10:00 - 11:00:</span>
          <span class="clase">5to B</span>
        </div>
        <div class="horario-item">
          <span class="tiempo">14:00 - 15:00:</span>
          <span class="clase">6to A</span>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .profesor-detalle {
    background: #fff;
    border-radius: 16px;
    padding: 2rem;
    font-family: "Poppins", sans-serif;
    color: #1e293b;
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .avatar {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 1.6rem;
    box-shadow: 0 8px 22px rgba(99,102,241,0.12);
  }

  .info {
    flex: 1;
    margin-left: 1rem;
  }

  h2 {
    margin: 0;
    font-size: 1.3rem;
  }

  .tags {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.4rem;
  }

  .badge {
    background: #e0f7fa;
    color: #00796b;
    padding: 0.25rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
    white-space: normal; /* allow long materia names to wrap */
    display: inline-block;
  }

  .status {
    border: 1px solid #00c853;
    color: #00c853;
    border-radius: 12px;
    padding: 0.25rem 0.6rem;
    font-size: 0.8rem;
  }

  .edit-btn {
    border: 1px solid rgba(15,23,42,0.06);
    background: white;
    color: var(--cyan);
    padding: 0.5rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    transition: 0.15s;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 2px 6px rgba(2,6,23,0.04);
  }

  .edit-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(2,6,23,0.06);
  }

  .tabs {
    display: flex;
    margin-top: 2rem;
    background: #f3f5f8;
    border-radius: 50px;
    padding: 0.25rem;
  }

  .tabs button {
    flex: 1;
    border: none;
    background: transparent;
    border-radius: 50px;
    padding: 0.75rem;
    font-weight: 600;
    color: #607d8b;
    cursor: pointer;
    transition: 0.2s;
  }

  .tabs button.active {
    background: white;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    color: #1e293b;
  }

  .content {
    margin-top: 1.5rem;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1.5rem;
  }

  .label {
    color: #607d8b;
    font-size: 0.9rem;
  }

  .value {
    font-weight: 500;
    font-size: 1.1rem;
    margin-top: 0.25rem;
  }

  .card {
    background: #f5f7fa;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    margin-top: 1rem;
  }

  .icon {
    font-size: 1.5rem;
    color: #00bcd4;
  }

  .cursos {
    margin-top: 1.5rem;
  }

  .chips {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
  }

  .chips span {
    border: 1px solid #3b82f6;
    color: #3b82f6;
    border-radius: 12px;
    padding: 0.25rem 0.75rem;
    font-size: 0.85rem;
  }

  .horario-title {
    font-size: 1.2rem;
    margin-bottom: 1.5rem;
    color: #1e293b;
  }

  .dia-section {
    margin-bottom: 2rem;
  }

  .dia-section h4 {
    color: #1e293b;
    margin-bottom: 1rem;
    font-size: 1.1rem;
  }

  .horario-item {
    background: #f8fafc;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
  }

  .tiempo {
    color: #64748b;
    min-width: 140px;
  }

  .clase {
    color: #1e293b;
    font-weight: 500;
  }
</style>
