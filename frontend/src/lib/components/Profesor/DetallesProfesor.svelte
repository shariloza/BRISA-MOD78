<script lang="ts">
    import { createEventDispatcher, onMount } from "svelte";
    import { fade, scale } from "svelte/transition";
    import {
        X,
        Edit,
        User,
        Mail,
        Phone,
        MapPin,
        BookOpen,
        GraduationCap,
        Briefcase,
        Calendar,
    } from "lucide-svelte";

    export let profesor: any;

    const dispatch = createEventDispatcher();
    const API_URL = "http://localhost:8000/api/profesores";

    let detalles: any = null;
    let loading = true;
    let error = "";
    let asignaciones: any[] = [];
    let bloques: any[] = [];

    onMount(async () => {
        if (profesor) {
            await cargarDetalles();
        }
    });

    async function cargarDetalles() {
        loading = true;
        try {
            const id = profesor.id ?? profesor.id_persona;
            // 1. Cargar datos básicos
            const res = await fetch(`${API_URL}/${id}`);
            if (!res.ok)
                throw new Error(
                    "No se pudo cargar la información del profesor",
                );
            detalles = await res.json();

            // 2. Cargar asignaciones
            const resAsig = await fetch(`${API_URL}/${id}/asignaciones`);
            if (resAsig.ok) {
                asignaciones = await resAsig.json();
            }

            // 3. Cargar bloques horarios
            const resBloques = await fetch(`${API_URL}/${id}/bloques`);
            if (resBloques.ok) {
                bloques = await resBloques.json();
            }
        } catch (e: any) {
            error = e.message;
        } finally {
            loading = false;
        }
    }

    function cerrar() {
        dispatch("close");
    }

    function editar() {
        dispatch("edit", profesor);
    }

    function formatFecha(fecha: string) {
        if (!fecha) return "No registrada";
        return new Date(fecha).toLocaleDateString("es-ES", {
            year: "numeric",
            month: "long",
            day: "numeric",
        });
    }

    function getDia(dia: string) {
        const dias: { [key: string]: string } = {
            LUNES: "Lunes",
            MARTES: "Martes",
            MIERCOLES: "Miércoles",
            JUEVES: "Jueves",
            VIERNES: "Viernes",
            SABADO: "Sábado",
            DOMINGO: "Domingo",
        };
        return dias[dia.toUpperCase()] || dia;
    }
</script>

<div
    class="modal-backdrop"
    on:click={cerrar}
    transition:fade={{ duration: 200 }}
>
    <div
        class="modal-content"
        on:click|stopPropagation
        transition:scale={{ duration: 200, start: 0.95 }}
    >
        <!-- HEADER -->
        <div class="modal-header">
            <div class="header-info">
                <div class="avatar-large">
                    {profesor.nombres[0]}{profesor.apellido_paterno?.[0] || ""}
                </div>
                <div>
                    <h2>
                        {profesor.nombres}
                        {profesor.apellido_paterno}
                        {profesor.apellido_materno || ""}
                    </h2>
                    <span
                        class="badge {profesor.estado_laboral?.toLowerCase() ===
                        'activo'
                            ? 'activo'
                            : 'inactivo'}"
                    >
                        {profesor.estado_laboral}
                    </span>
                </div>
            </div>
            <div class="header-actions">
                <button class="btn-edit" on:click={editar}>
                    <Edit size={18} />
                    Editar
                </button>
                <button class="btn-close" on:click={cerrar}>
                    <X size={24} />
                </button>
            </div>
        </div>

        <div class="modal-body">
            {#if loading}
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Cargando información...</p>
                </div>
            {:else if error}
                <div class="error">
                    <p>❌ {error}</p>
                </div>
            {:else if detalles}
                <div class="grid-layout">
                    <!-- COLUMNA IZQUIERDA: INFO PERSONAL -->
                    <div class="column">
                        <section class="info-card">
                            <h3><User size={18} /> Información Personal</h3>
                            <div class="info-item">
                                <label>Cédula de Identidad</label>
                                <p>{detalles.ci}</p>
                            </div>
                            <div class="info-item">
                                <label>Correo Electrónico</label>
                                <p class="flex-row">
                                    <Mail size={14} />
                                    {detalles.correo}
                                </p>
                            </div>
                            <div class="info-item">
                                <label>Teléfono</label>
                                <p class="flex-row">
                                    <Phone size={14} />
                                    {detalles.telefono || "No registrado"}
                                </p>
                            </div>
                            <div class="info-item">
                                <label>Dirección</label>
                                <p class="flex-row">
                                    <MapPin size={14} />
                                    {detalles.direccion || "No registrada"}
                                </p>
                            </div>
                        </section>

                        <section class="info-card">
                            <h3>
                                <GraduationCap size={18} /> Información Académica
                            </h3>
                            <div class="info-item">
                                <label>Título Académico</label>
                                <p>
                                    {detalles.titulo_academico ||
                                        "No registrado"}
                                </p>
                            </div>
                            <div class="info-item">
                                <label>Especialidad</label>
                                <p>
                                    {detalles.especialidad || "No registrada"}
                                </p>
                            </div>
                            <div class="info-item">
                                <label>Nivel de Enseñanza</label>
                                <p class="capitalize">
                                    {detalles.nivel_enseñanza || "Todos"}
                                </p>
                            </div>
                        </section>
                    </div>

                    <!-- COLUMNA DERECHA: ASIGNACIONES Y HORARIOS -->
                    <div class="column">
                        <section class="info-card">
                            <h3><BookOpen size={18} /> Materias y Cursos</h3>
                            {#if asignaciones.length > 0}
                                <div class="tags-container">
                                    {#each asignaciones as asig}
                                        <div class="tag">
                                            <span class="materia"
                                                >{asig.nombre_materia}</span
                                            >
                                            <span class="separator">•</span>
                                            <span class="curso"
                                                >{asig.nombre_curso}</span
                                            >
                                        </div>
                                    {/each}
                                </div>
                            {:else}
                                <p class="empty-text">
                                    Sin asignaciones registradas
                                </p>
                            {/if}
                        </section>

                        <section class="info-card">
                            <h3><Calendar size={18} /> Horario y Carga</h3>
                            {#if bloques.length > 0}
                                <div class="schedule-list">
                                    {#each bloques as bloque}
                                        <div class="schedule-item">
                                            <div class="schedule-time">
                                                <span class="day"
                                                    >{getDia(
                                                        bloque.dia_semana,
                                                    )}</span
                                                >
                                                <span class="time"
                                                    >{bloque.hora_inicio.slice(
                                                        0,
                                                        5,
                                                    )} - {bloque.hora_fin.slice(
                                                        0,
                                                        5,
                                                    )}</span
                                                >
                                            </div>
                                            <div class="schedule-details">
                                                <span class="materia-small"
                                                    >{bloque.nombre_materia}</span
                                                >
                                                <span class="curso-small"
                                                    >{bloque.nombre_curso}</span
                                                >
                                            </div>
                                        </div>
                                    {/each}
                                </div>
                            {:else}
                                <p class="empty-text">Sin horario registrado</p>
                            {/if}
                        </section>

                        {#if detalles.observaciones_profesor}
                            <section class="info-card">
                                <h3>Observaciones</h3>
                                <p class="observaciones">
                                    {detalles.observaciones_profesor}
                                </p>
                            </section>
                        {/if}
                    </div>
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        backdrop-filter: blur(4px);
    }

    .modal-content {
        background: white;
        width: 90%;
        max-width: 900px;
        max-height: 90vh;
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .modal-header {
        padding: 24px 32px;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #fff;
    }

    .header-info {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .avatar-large {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }

    .header-info h2 {
        margin: 0 0 4px 0;
        font-size: 1.5rem;
        color: #1e293b;
    }

    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 99px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge.activo {
        background: #dcfce7;
        color: #166534;
    }
    .badge.inactivo {
        background: #fee2e2;
        color: #991b1b;
    }

    .header-actions {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .btn-edit {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #0f172a;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: 600;
        cursor: pointer;
        transition: 0.2s;
    }
    .btn-edit:hover {
        background: #334155;
    }

    .btn-close {
        background: transparent;
        border: none;
        color: #64748b;
        cursor: pointer;
        padding: 8px;
        border-radius: 50%;
        transition: 0.2s;
        display: flex;
    }
    .btn-close:hover {
        background: #f1f5f9;
        color: #0f172a;
    }

    .modal-body {
        padding: 32px;
        overflow-y: auto;
        background: #f8fafc;
        flex: 1;
    }

    .grid-layout {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
    }

    @media (max-width: 768px) {
        .grid-layout {
            grid-template-columns: 1fr;
        }
    }

    .column {
        display: flex;
        flex-direction: column;
        gap: 24px;
    }

    .info-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #e2e8f0;
    }

    .info-card h3 {
        margin: 0 0 20px 0;
        font-size: 1.1rem;
        color: #334155;
        display: flex;
        align-items: center;
        gap: 10px;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 12px;
    }

    .info-item {
        margin-bottom: 16px;
    }
    .info-item:last-child {
        margin-bottom: 0;
    }

    .info-item label {
        display: block;
        font-size: 0.85rem;
        color: #64748b;
        margin-bottom: 4px;
        font-weight: 500;
    }

    .info-item p {
        margin: 0;
        color: #0f172a;
        font-weight: 500;
        font-size: 1rem;
    }

    .flex-row {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .capitalize {
        text-transform: capitalize;
    }

    /* Tags de Materias */
    .tags-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .tag {
        display: flex;
        align-items: center;
        background: #f1f5f9;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }

    .materia {
        font-weight: 600;
        color: #0f172a;
    }
    .separator {
        margin: 0 8px;
        color: #cbd5e1;
    }
    .curso {
        color: #64748b;
        font-size: 0.9rem;
    }

    .empty-text {
        color: #94a3b8;
        font-style: italic;
        text-align: center;
        padding: 10px;
    }

    /* Horarios */
    .schedule-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .schedule-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 14px;
        background: #f8fafc;
        border-radius: 8px;
        border-left: 4px solid #6366f1;
    }

    .schedule-time {
        display: flex;
        flex-direction: column;
    }

    .day {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 700;
    }
    .time {
        font-weight: 600;
        color: #0f172a;
    }

    .schedule-details {
        text-align: right;
    }

    .materia-small {
        display: block;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .curso-small {
        font-size: 0.8rem;
        color: #64748b;
    }

    .observaciones {
        background: #fffbeb;
        padding: 12px;
        border-radius: 8px;
        color: #92400e;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px;
        color: #64748b;
    }

    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #e2e8f0;
        border-top-color: #6366f1;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 16px;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
</style>
