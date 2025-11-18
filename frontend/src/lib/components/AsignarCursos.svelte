<script lang="ts">
  import { onMount, createEventDispatcher } from "svelte";

  const API_URL = "http://localhost:8000/api/profesores";
  const dispatch = createEventDispatcher();

  export let mostrar = false;
  export let cursoSeleccionado: any = null;

  let cursos: any[] = [];
  let cargando = false;
  let error = "";

  async function cargarCursos() {
    cargando = true;
    error = "";
    
    try {
      const res = await fetch(`${API_URL}/cursos`);
      if (!res.ok) throw new Error("Error al cargar cursos");
      
      cursos = await res.json();
    } catch (err: any) {
      error = err.message;
      console.error("Error cargando cursos:", err);
    } finally {
      cargando = false;
    }
  }

  function seleccionarCurso(curso: any) {
    cursoSeleccionado = curso;
    dispatch('cursoSeleccionado', { curso });
  }

  function cerrar() {
    dispatch('cerrar');
  }

  $: if (mostrar) {
    cargarCursos();
  }
</script>

{#if mostrar}
<div class="overlay" on:click={cerrar}>
  <div class="modal" on:click|stopPropagation>
    <div class="header">
      <h2>Cursos</h2>
      <button class="btn-cerrar" on:click={cerrar}>×</button>
    </div>

    <div class="content">
      {#if cargando}
        <div class="estado">Cargando cursos...</div>
      {:else if error}
        <div class="error">{error}</div>
      {:else if cursos.length === 0}
        <div class="estado">No hay cursos registrados</div>
      {:else}
        <div class="lista-cursos">
          {#each cursos as curso}
            <div 
              class="curso-item {cursoSeleccionado?.id_curso === curso.id_curso ? 'seleccionado' : ''}"
              on:click={() => seleccionarCurso(curso)}
            >
              <div class="curso-info">
                <span class="nombre">{curso.nombre_curso}</span>
                <div class="detalles">
                  <span class="nivel">{curso.nivel}</span>
                  <span class="gestion">{curso.gestion}</span>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>
{/if}

<style>
  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  .modal {
    background: white;
    border-radius: 12px;
    width: 90%;
    max-width: 550px;
    max-height: 600px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #e0e0e0;
  }

  .header h2 {
    margin: 0;
    font-size: 1.5rem;
    color: #1a1a1a;
    font-weight: 600;
  }

  .btn-cerrar {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Arial, sans-serif;
  }

  .content {
    padding: 0;
  }

  .lista-cursos {
    max-height: 450px;
    overflow-y: auto;
    padding: 8px 0;
  }

  .curso-item {
    padding: 16px 24px;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    transition: background-color 0.2s;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: black;
  }

  .curso-item:hover {
    background: #aebcca;
  }

  .curso-item.seleccionado {
    background: #007bff;
    
  }
  

  .curso-item.seleccionado .nivel,
  .curso-item.seleccionado .gestion {
    color: rgba(255, 255, 255, 0.9);
    background: rgba(255, 255, 255, 0.2);
  }

  .curso-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .nombre {
    font-weight: 500;
    font-size: 1rem;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  .detalles {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .nivel, .gestion {
    font-size: 0.8rem;
    padding: 4px 12px;
    border-radius: 12px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-weight: 500;
  }

  .nivel {
    background: #e3f2fd;
    color: #1565c0;
    text-transform: capitalize;
  }

  .gestion {
    background: #f3e5f5;
    color: #7b1fa2;
  }

  .estado, .error {
    padding: 40px 24px;
    text-align: center;
    color: #666;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  .error {
    color: #dc3545;
    background: #f8d7da;
    border-radius: 8px;
    margin: 16px;
  }
</style>