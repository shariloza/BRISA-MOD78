<script lang="ts">
  import { onMount, createEventDispatcher } from "svelte";

  const API_URL = "http://localhost:8000/api/profesores";
  const dispatch = createEventDispatcher();

  export let mostrar = false;
  export let materiaSeleccionada: any = null;

  let materias: any[] = [];
  let cargando = false;
  let error = "";

  async function cargarMaterias() {
    cargando = true;
    error = "";
    
    try {
      const res = await fetch(`${API_URL}/materias`);
      if (!res.ok) throw new Error("Error al cargar materias");
      
      materias = await res.json();
    } catch (err: any) {
      error = err.message;
      console.error("Error cargando materias:", err);
    } finally {
      cargando = false;
    }
  }

  function seleccionarMateria(materia: any) {
    materiaSeleccionada = materia;
    dispatch('materiaSeleccionada', { materia });
  }

  function cerrar() {
    dispatch('cerrar');
  }

  $: if (mostrar) {
    cargarMaterias();
  }
</script>

{#if mostrar}
<div class="overlay" on:click={cerrar}>
  <div class="modal" on:click|stopPropagation>
    <div class="header">
      <h2>Materias</h2>
      <button class="btn-cerrar" on:click={cerrar}>×</button>
    </div>

    <div class="content">
      {#if cargando}
        <div class="estado">Cargando materias...</div>
      {:else if error}
        <div class="error">{error}</div>
      {:else if materias.length === 0}
        <div class="estado">No hay materias registradas</div>
      {:else}
        <div class="lista-materias">
          {#each materias as materia}
            <div 
              class="materia-item {materiaSeleccionada?.id_materia === materia.id_materia ? 'seleccionada' : ''}"
              on:click={() => seleccionarMateria(materia)}
            >
              <span class="nombre">{materia.nombre_materia}</span>
              <span class="nivel">{materia.nivel}</span>
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
    max-width: 500px;
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

  .lista-materias {
    max-height: 450px;
    overflow-y: auto;
    padding: 8px 0;
  }

  .materia-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    transition: background-color 0.2s;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: black;
  }

  .materia-item:hover {
    background: #aebcca;
  }

  .materia-item.seleccionada {
    background: #007bff;
    color: white;
  }

  .materia-item.seleccionada .nivel {
    color: rgba(255, 255, 255, 0.9);
    background: rgba(255, 255, 255, 0.2);
  }

  .nombre {
    font-weight: 500;
    font-size: 1rem;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }

  .nivel {
    font-size: 0.85rem;
    color: #666;
    text-transform: capitalize;
    background: #f0f0f0;
    padding: 4px 12px;
    border-radius: 12px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-weight: 500;
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