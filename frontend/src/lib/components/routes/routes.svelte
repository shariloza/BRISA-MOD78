<script context="module">
export const routes = [
  // Ruta principal -> redirige a profesores (si tu enrutador lo utiliza)
  { path: '/', redirect: '/profesores' },

  // ========== CURSOS ==========
  { path: '/cursos', name: 'Cursos', component: () => import('../Cursos/Cursos.svelte') },
  { path: '/cursos/asignar', name: 'AsignarCursos', component: () => import('../Cursos/AsignarCursos.svelte') },
  { path: '/cursos/crear', name: 'CrearCursos', component: () => import('../Cursos/CrearCursos.svelte') },
  { path: '/cursos/editar/:id', name: 'EditarCursos', component: () => import('../Cursos/EditarCursos.svelte') },

  // ========== MATERIAS ==========
  { path: '/materias', name: 'Materias', component: () => import('../Materias/Materias.svelte') },
  { path: '/materias/asignar', name: 'AsignarMaterias', component: () => import('../Materias/AsignarMaterias.svelte') },
  { path: '/materias/crear', name: 'CrearMaterias', component: () => import('../Materias/CrearMaterias.svelte') },
  { path: '/materias/editar/:id', name: 'EditarMaterias', component: () => import('../Materias/EditarMaterias.svelte') },

  // ========== HORARIOS ==========
  { path: '/horarios', name: 'BloqueHorarios', component: () => import('../Cargas/bloqueHorarios.svelte') },

  // ========== PROFESOR ==========
  { path: '/profesores', name: 'Profesores', component: () => import('../Profesor/Profesores.svelte') },
  { path: '/profesores/crear', name: 'NuevoProfesor', component: () => import('../Profesor/NuevoProfesor.svelte') },
  { path: '/profesores/editar/:id', name: 'EditarProfesores', component: () => import('../Profesor/EditarProfesores.svelte') },
  { path: '/profesores/card', name: 'ProfesorCard', component: () => import('../Profesor/ProfesorCard.svelte') },
  { path: '/profesores/detalle/:id', name: 'ProfesorDetalle', component: () => import('../Profesor/ProfesorDetalle.svelte') },

  // ========== ASIGNAR CARGA ==========
  { path: '/asignar-carga', name: 'AsignarCarga', component: () => import('../Cargas/AsignarCarga.svelte') },

  // Ruta 404 - Redirección
  { path: '/:catchAll(.*)', redirect: '/profesores' },
];
</script>