<script lang="ts">
  import { onMount, createEventDispatcher } from "svelte";

  const API_URL = "http://localhost:8000/api/profesores";

  export interface BloqueHorario {
    id_bloque?: number;
    id_profesor: number;
    id_curso: number;
    id_materia: number;
    dia_semana: string;
    hora_inicio: string;
    hora_fin: string;
    gestion: string;
    observaciones?: string;
    nombre_materia?: string;
    nombre_curso?: string;
    nombre_profesor?: string;
    fecha_registro?: string;
  }

  export interface Props {
    // Props principales
    idProfesor?: number;
    idPersona?: number;
    gestion?: string;
    
    // Modo de visualización
    modo?: 'completo' | 'resumen' | 'tarjeta';
    
    // Configuración
    permitirEditar?: boolean;
    permitirEliminar?: boolean;
    mostrarProfesor?: boolean;
    
    // Estados externos
    bloquesExternos?: BloqueHorario[];
    cargandoExterno?: boolean;
  }

  export let props: Props = {
    modo: 'completo',
    permitirEditar: false,
    permitirEliminar: false,
    mostrarProfesor: false,
    gestion: '2025'
  };

  const dispatch = createEventDispatcher<{
    bloqueSeleccionado: BloqueHorario;
    bloqueEditado: BloqueHorario;
    bloqueEliminado: { id_bloque: number };
    error: string;
  }>();

  // Estados internos
  let bloques: BloqueHorario[] = [];
  let cargando = false;
  let error = "";

  // Formatear hora (remover segundos si existen)
  function formatearHora(hora: string): string {
    return hora.includes(':') ? hora.substring(0, 5) : hora;
  }

  // Calcular duración en horas
  function calcularDuracion(horaInicio: string, horaFin: string): number {
    const inicioFormateado = formatearHora(horaInicio);
    const finFormateado = formatearHora(horaFin);
    
    const [h1, m1] = inicioFormateado.split(':').map(Number);
    const [h2, m2] = finFormateado.split(':').map(Number);
    const minutosTotales = (h2 * 60 + m2) - (h1 * 60 + m1);
    return minutosTotales / 60;
  }

  // Obtener nombre del día
  function obtenerNombreDia(dia: string): string {
    const dias: { [key: string]: string } = {
      lunes: "Lunes",
      martes: "Martes", 
      miercoles: "Miércoles",
      jueves: "Jueves",
      viernes: "Viernes",
      sabado: "Sábado",
      domingo: "Domingo"
    };
    return dias[dia] || dia;
  }

  // Calcular estadísticas
  function calcularEstadisticas() {
    const horasPorDia: { [key: string]: number } = {};
    let totalHoras = 0;

    bloques.forEach(bloque => {
      const duracion = calcularDuracion(bloque.hora_inicio, bloque.hora_fin);
      horasPorDia[bloque.dia_semana] = (horasPorDia[bloque.dia_semana] || 0) + duracion;
      totalHoras += duracion;
    });

    return { horasPorDia, totalHoras };
  }

  // Cargar bloques desde API
  async function cargarBloques() {
    if (props.bloquesExternos) {
      bloques = props.bloquesExternos.map(bloque => ({
        ...bloque,
        hora_inicio: formatearHora(bloque.hora_inicio),
        hora_fin: formatearHora(bloque.hora_fin)
      }));
      return;
    }

    const idPersona = props.idPersona;
    if (!idPersona) {
      error = "ID de persona no proporcionado";
      return;
    }

    cargando = true;
    error = "";

    try {
      const url = `${API_URL}/${idPersona}/bloques${props.gestion ? `?gestion=${props.gestion}` : ''}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      bloques = Array.isArray(data) ? data.map(bloque => ({
        ...bloque,
        hora_inicio: formatearHora(bloque.hora_inicio),
        hora_fin: formatearHora(bloque.hora_fin)
      })) : [];

    } catch (err: any) {
      error = `Error al cargar bloques horarios: ${err.message}`;
      dispatch('error', err.message);
    } finally {
      cargando = false;
    }
  }

  // Obtener bloques por día
  function obtenerBloquesPorDia(dia: string): BloqueHorario[] {
    return bloques.filter(bloque => bloque.dia_semana === dia);
  }

  // Obtener todos los días con bloques
  function obtenerDiasConBloques(): string[] {
    const dias = [...new Set(bloques.map(bloque => bloque.dia_semana))];
    const ordenDias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'];
    return dias.sort((a, b) => ordenDias.indexOf(a) - ordenDias.indexOf(b));
  }

  // Handlers de eventos
  function onBloqueClick(bloque: BloqueHorario) {
    dispatch('bloqueSeleccionado', bloque);
  }

  function onEditarBloque(bloque: BloqueHorario) {
    dispatch('bloqueEditado', bloque);
  }

  function onEliminarBloque(bloque: BloqueHorario) {
    if (bloque.id_bloque) {
      dispatch('bloqueEliminado', { id_bloque: bloque.id_bloque });
    }
  }

  // Recargar bloques
  function recargar() {
    cargarBloques();
  }

  // Cargar datos cuando cambien las props
  $: if (props.idPersona || props.bloquesExternos) {
    cargarBloques();
  }

  // Calcular estadísticas reactivas
  $: estadisticas = calcularEstadisticas();
  $: diasConBloques = obtenerDiasConBloques();
</script>

<div class="bloque-horario-component">
  
  <!-- HEADER CON ESTADÍSTICAS -->
  {#if props.modo !== 'tarjeta'}
    <div class="bloques-header">
      <div class="estadisticas-principales">
        <div class="estadistica-item">
          <span class="estadistica-label">Total de bloques:</span>
          <span class="estadistica-valor">{bloques.length}</span>
        </div>
        <div class="estadistica-item">
          <span class="estadistica-label">Horas semanales:</span>
          <span class="estadistica-valor {estadisticas.totalHoras > 40 ? 'sobrecarga' : ''}">
            {estadisticas.totalHoras.toFixed(1)}h
          </span>
        </div>
        <div class="estadistica-item">
          <span class="estadistica-label">Días con clases:</span>
          <span class="estadistica-valor">{diasConBloques.length}</span>
        </div>
      </div>
      
      {#if props.permitirEditar || props.permitirEliminar}
        <div class="acciones-header">
          {#if props.permitirEditar}
            <button class="btn-editar-todo" on:click={() => dispatch('bloqueEditado', {})}>
              ✏️ Editar Horarios
            </button>
          {/if}
        </div>
      {/if}
    </div>
  {/if}

  <!-- ESTADO DE CARGA -->
  {#if cargando || props.cargandoExterno}
    <div class="estado-carga">
      <div class="spinner"></div>
      <span>Cargando horarios...</span>
    </div>
  {/if}

  <!-- ERROR -->
  {#if error}
    <div class="estado-error">
      <span class="error-icon">⚠️</span>
      <span class="error-message">{error}</span>
      <button class="btn-reintentar" on:click={cargarBloques}>Reintentar</button>
    </div>
  {/if}

  <!-- CONTENIDO PRINCIPAL -->
  {#if !cargando && !error}
    
    <!-- MODO COMPLETO - Vista semanal -->
    {#if props.modo === 'completo'}
      <div class="vista-semanal">
        {#each diasConBloques as dia}
          <div class="dia-section">
            <h3 class="dia-header">{obtenerNombreDia(dia)}</h3>
            <div class="bloques-dia">
              {#each obtenerBloquesPorDia(dia) as bloque}
                <div 
                  class="bloque-tarjeta {bloque.observaciones ? 'con-observaciones' : ''}"
                  on:click={() => onBloqueClick(bloque)}
                >
                  <div class="bloque-contenido">
                    <div class="bloque-info-principal">
                      <span class="bloque-materia">{bloque.nombre_materia}</span>
                      <span class="bloque-curso">{bloque.nombre_curso}</span>
                    </div>
                    <div class="bloque-horario">
                      <span class="bloque-horas">{bloque.hora_inicio} - {bloque.hora_fin}</span>
                      <span class="bloque-duracion">({calcularDuracion(bloque.hora_inicio, bloque.hora_fin).toFixed(1)}h)</span>
                    </div>
                    {#if bloque.observaciones}
                      <div class="bloque-observaciones">
                        <span class="observaciones-text">📝 {bloque.observaciones}</span>
                      </div>
                    {/if}
                    {#if props.mostrarProfesor && bloque.nombre_profesor}
                      <div class="bloque-profesor">
                        <span class="profesor-text">👨‍🏫 {bloque.nombre_profesor}</span>
                      </div>
                    {/if}
                  </div>
                  
                  <!-- ACCIONES -->
                  {#if props.permitirEditar || props.permitirEliminar}
                    <div class="bloque-acciones">
                      {#if props.permitirEditar}
                        <button 
                          class="btn-accion btn-editar"
                          on:click|stopPropagation={() => onEditarBloque(bloque)}
                          title="Editar bloque"
                        >
                          ✏️
                        </button>
                      {/if}
                      {#if props.permitirEliminar}
                        <button 
                          class="btn-accion btn-eliminar"
                          on:click|stopPropagation={() => onEliminarBloque(bloque)}
                          title="Eliminar bloque"
                        >
                          🗑️
                        </button>
                      {/if}
                    </div>
                  {/if}
                </div>
              {/each}
            </div>
          </div>
        {/each}
        
        {#if bloques.length === 0}
          <div class="sin-bloques">
            <div class="sin-bloques-icon">📅</div>
            <h3>No hay horarios asignados</h3>
            <p>No se han encontrado bloques horarios para mostrar</p>
          </div>
        {/if}
      </div>

    <!-- MODO RESUMEN - Lista compacta -->
    {:else if props.modo === 'resumen'}
      <div class="vista-resumen">
        <div class="bloques-lista-compacta">
          {#each bloques as bloque}
            <div 
              class="bloque-item-compacto"
              on:click={() => onBloqueClick(bloque)}
            >
              <div class="bloque-info-compacto">
                <span class="bloque-dia">{obtenerNombreDia(bloque.dia_semana).substring(0, 3)}</span>
                <span class="bloque-horas-compacto">{bloque.hora_inicio}-{bloque.hora_fin}</span>
                <span class="bloque-materia-compacto">{bloque.nombre_materia}</span>
                <span class="bloque-curso-compacto">{bloque.nombre_curso}</span>
              </div>
              <div class="bloque-duracion-compacto">
                {calcularDuracion(bloque.hora_inicio, bloque.hora_fin).toFixed(1)}h
              </div>
            </div>
          {/each}
        </div>
      </div>

    <!-- MODO TARJETA - Para embed en otros componentes -->
    {:else if props.modo === 'tarjeta'}
      <div class="vista-tarjeta">
        <div class="tarjeta-horarios">
          <div class="tarjeta-header">
            <h4>Horarios de Clases</h4>
            <span class="total-bloques">{bloques.length} bloques</span>
          </div>
          
          <div class="tarjeta-content">
            {#each bloques.slice(0, 3) as bloque}
              <div class="bloque-mini">
                <span class="mini-dia">{obtenerNombreDia(bloque.dia_semana).substring(0, 1)}</span>
                <span class="mini-horas">{bloque.hora_inicio}-{bloque.hora_fin}</span>
                <span class="mini-materia">{bloque.nombre_materia}</span>
              </div>
            {/each}
            
            {#if bloques.length > 3}
              <div class="mas-bloques">
                +{bloques.length - 3} más...
              </div>
            {/if}
            
            {#if bloques.length === 0}
              <div class="sin-bloques-mini">
                Sin horarios asignados
              </div>
            {/if}
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>

<style>
  .bloque-horario-component {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #1e293b;
  }

  /* HEADER Y ESTADÍSTICAS */
  .bloques-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: 16px;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }

  .estadisticas-principales {
    display: flex;
    gap: 24px;
  }

  .estadistica-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }

  .estadistica-label {
    font-size: 0.8rem;
    color: #64748b;
    font-weight: 500;
  }

  .estadistica-valor {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1e293b;
  }

  .estadistica-valor.sobrecarga {
    color: #dc2626;
  }

  .acciones-header {
    display: flex;
    gap: 8px;
  }

  .btn-editar-todo {
    background: #00cfe6;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
  }

  .btn-editar-todo:hover {
    background: #00b8d4;
  }

  /* ESTADOS */
  .estado-carga, .estado-error {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 40px;
    text-align: center;
    color: #64748b;
  }

  .estado-error {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    color: #dc2626;
  }

  .error-icon {
    font-size: 1.2rem;
  }

  .error-message {
    flex: 1;
  }

  .btn-reintentar {
    background: #ef4444;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
  }

  .btn-reintentar:hover {
    background: #dc2626;
  }

  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #e2e8f0;
    border-top: 2px solid #00cfe6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* VISTA SEMANAL (MODO COMPLETO) */
  .vista-semanal {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .dia-section {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
  }

  .dia-header {
    margin: 0;
    padding: 16px;
    background: #f1f5f9;
    color: #475569;
    font-size: 1.1rem;
    font-weight: 600;
    border-bottom: 1px solid #e2e8f0;
  }

  .bloques-dia {
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .bloque-tarjeta {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 16px;
    background: #fafbfc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
  }

  .bloque-tarjeta:hover {
    border-color: #00cfe6;
    box-shadow: 0 2px 8px rgba(0, 207, 230, 0.1);
  }

  .bloque-tarjeta.con-observaciones {
    border-left: 4px solid #00cfe6;
  }

  .bloque-contenido {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .bloque-info-principal {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .bloque-materia {
    font-weight: 600;
    color: #1e293b;
    font-size: 1rem;
  }

  .bloque-curso {
    color: #475569;
    font-size: 0.9rem;
  }

  .bloque-horario {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .bloque-horas {
    color: #1e293b;
    font-weight: 500;
    font-size: 0.9rem;
  }

  .bloque-duracion {
    color: #64748b;
    font-size: 0.8rem;
    background: #f1f5f9;
    padding: 2px 6px;
    border-radius: 4px;
  }

  .bloque-observaciones, .bloque-profesor {
    font-size: 0.85rem;
    color: #64748b;
  }

  .observaciones-text, .profesor-text {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .bloque-acciones {
    display: flex;
    gap: 4px;
    margin-left: 12px;
  }

  .btn-accion {
    background: none;
    border: none;
    cursor: pointer;
    padding: 6px;
    border-radius: 4px;
    font-size: 0.9rem;
    transition: background-color 0.2s;
  }

  .btn-editar:hover {
    background: #dbeafe;
    color: #1d4ed8;
  }

  .btn-eliminar:hover {
    background: #fef2f2;
    color: #dc2626;
  }

  /* VISTA RESUMEN */
  .vista-resumen {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
  }

  .bloques-lista-compacta {
    display: flex;
    flex-direction: column;
  }

  .bloque-item-compacto {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #f1f5f9;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .bloque-item-compacto:hover {
    background: #f8fafc;
  }

  .bloque-item-compacto:last-child {
    border-bottom: none;
  }

  .bloque-info-compacto {
    display: flex;
    align-items: center;
    gap: 16px;
    flex: 1;
  }

  .bloque-dia {
    font-weight: 600;
    color: #00cfe6;
    font-size: 0.85rem;
    min-width: 30px;
  }

  .bloque-horas-compacto {
    color: #475569;
    font-size: 0.85rem;
    min-width: 80px;
  }

  .bloque-materia-compacto {
    font-weight: 500;
    color: #1e293b;
    flex: 1;
  }

  .bloque-curso-compacto {
    color: #64748b;
    font-size: 0.85rem;
    min-width: 80px;
  }

  .bloque-duracion-compacto {
    color: #64748b;
    font-size: 0.8rem;
    background: #f1f5f9;
    padding: 4px 8px;
    border-radius: 4px;
    min-width: 50px;
    text-align: center;
  }

  /* VISTA TARJETA */
  .vista-tarjeta {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    overflow: hidden;
  }

  .tarjeta-horarios {
    display: flex;
    flex-direction: column;
  }

  .tarjeta-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
  }

  .tarjeta-header h4 {
    margin: 0;
    font-size: 0.9rem;
    color: #1e293b;
    font-weight: 600;
  }

  .total-bloques {
    font-size: 0.8rem;
    color: #64748b;
    background: #e2e8f0;
    padding: 2px 6px;
    border-radius: 4px;
  }

  .tarjeta-content {
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .bloque-mini {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    font-size: 0.8rem;
  }

  .mini-dia {
    font-weight: 600;
    color: #00cfe6;
    min-width: 12px;
  }

  .mini-horas {
    color: #475569;
    min-width: 70px;
  }

  .mini-materia {
    color: #1e293b;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .mas-bloques, .sin-bloques-mini {
    text-align: center;
    color: #64748b;
    font-size: 0.8rem;
    padding: 8px;
    font-style: italic;
  }

  /* ESTADO SIN BLOQUES */
  .sin-bloques {
    text-align: center;
    padding: 40px;
    color: #64748b;
  }

  .sin-bloques-icon {
    font-size: 3rem;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  .sin-bloques h3 {
    margin: 0 0 8px 0;
    color: #475569;
  }

  .sin-bloques p {
    margin: 0;
    font-size: 0.9rem;
  }

  /* RESPONSIVE */
  @media (max-width: 768px) {
    .bloques-header {
      flex-direction: column;
      gap: 16px;
      align-items: stretch;
    }

    .estadisticas-principales {
      justify-content: space-around;
    }

    .bloque-tarjeta {
      flex-direction: column;
      gap: 12px;
    }

    .bloque-acciones {
      align-self: flex-end;
    }

    .bloque-info-compacto {
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
    }

    .bloque-dia, .bloque-horas-compacto, .bloque-curso-compacto {
      min-width: auto;
    }
  }

  @media (max-width: 480px) {
    .estadisticas-principales {
      flex-direction: column;
      gap: 12px;
    }

    .bloque-info-principal {
      text-align: center;
    }

    .bloque-horario {
      justify-content: center;
    }
  }
</style>