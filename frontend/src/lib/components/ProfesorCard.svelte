<script lang="ts">
  import { onMount } from 'svelte';
  import { Clock } from "lucide-svelte";

  const API_URL = 'http://localhost:8000/api/profesores';

  let profesores = [];

  onMount(async () => {
    try {
      const response = await fetch(API_URL);
      if (!response.ok) throw new Error('Error cargando profesores');
      profesores = await response.json();
    } catch (error) {
      console.error('Error:', error);
    }
  });
</script>

<div class="profesores-grid">
  {#each profesores as profesor}
    <div class="card" role="button" tabindex="0">
      <div class="avatar">
        {profesor.nombres
          .split(" ")
          .map((n) => n[0])
          .join("")
          .toUpperCase()}
      </div>

      <div class="content">
        <div class="top">
          <div class="nombre">{profesor.nombres}</div>
          <span class="materia-pill">
            {#if profesor.materias.length}
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
              <span class="curso-pill">+{profesor.cursos.length - 2}</span>
            {/if}
          {/if}
        </div>

        <hr class="divider" />

        <div class="footer">
          <div class="left">
            <Clock size="16" color="#64748b" />
            <span class="carga">{profesor.cargaHoraria || 0}</span>
          </div>
          <div class="right">
            <span class="estado-pill {profesor.estado_laboral.toLowerCase() === 'activo' ? 'activo' : 'inactivo'}">
              {profesor.estado_laboral}
            </span>
          </div>
        </div>
      </div>
    </div>
  {/each}
</div>

<style>
  /* TODO: Mantener todo tu CSS existente */
  .profesores-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    padding: 20px;
    width: 100%;
    box-sizing: border-box;
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
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
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

  .carga { margin-left: 6px; }

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

  @media (max-width: 1200px) {
    .profesores-grid {
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      max-width: calc(100vw - 100px);
    }
  }

  @media (max-width: 768px) {
    .profesores-grid {
      grid-template-columns: 1fr;
      max-width: 100%;
      padding: 16px;
    }

    .card {
      padding: 12px;
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
</style>
