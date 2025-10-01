// ===============================================
// JAVASCRIPT PARA FILTROS DINÁMICOS R2
// ===============================================

// Variables globales
let filtrosActivos = {};
let estadisticasCache = {};

// Función para cambiar categoría
function cambiarCategoria(categoria) {
    const url = new URL(window.location);
    url.searchParams.set('categoria', categoria);
    window.location.href = url.toString();
}

// ===============================================
// FILTROS EN CASCADA DINÁMICOS
// ===============================================

// Configurar event listeners cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Configurar filtros en cascada
    configurarFiltrosCascada();
    
    // Cargar estadísticas iniciales si hay categoría seleccionada
    const categoriaActual = obtenerCategoriaActual();
    if (categoriaActual) {
        actualizarEstadisticas();
    }
});

function configurarFiltrosCascada() {
    // Event listener para Unidad Académica
    const unidadSelect = document.getElementById('unidad_academica');
    if (unidadSelect) {
        unidadSelect.addEventListener('change', function() {
            const unidadId = this.value;
            filtrosActivos.unidad_academica = unidadId;
            
            if (unidadId) {
                cargarCarrerasPorUnidad(unidadId);
            } else {
                limpiarFiltrosInferiores(['carrera', 'semestre', 'asignatura', 'unidad_didactica', 'contenido']);
            }
            
            actualizarEstadisticas();
        });
    }
    
    // Event listener para Carrera
    const carreraSelect = document.getElementById('carrera');
    if (carreraSelect) {
        carreraSelect.addEventListener('change', function() {
            const carreraId = this.value;
            filtrosActivos.carrera = carreraId;
            
            if (carreraId) {
                cargarSemestresPorCarrera(carreraId);
                cargarAsignaturasPorCarrera(carreraId);
            } else {
                limpiarFiltrosInferiores(['semestre', 'asignatura', 'unidad_didactica', 'contenido']);
            }
            
            actualizarEstadisticas();
        });
    }
    
    // Event listener para Semestre
    const semestreSelect = document.getElementById('semestre');
    if (semestreSelect) {
        semestreSelect.addEventListener('change', function() {
            filtrosActivos.semestre = this.value;
            filtrarAsignaturasPorSemestre();
            actualizarEstadisticas();
        });
    }
    
    // Event listener para Asignatura
    const asignaturaSelect = document.getElementById('asignatura');
    if (asignaturaSelect) {
        asignaturaSelect.addEventListener('change', function() {
            const asignaturaId = this.value;
            filtrosActivos.asignatura = asignaturaId;
            
            if (asignaturaId) {
                cargarUnidadesDidacticasPorAsignatura(asignaturaId);
            } else {
                limpiarFiltrosInferiores(['unidad_didactica', 'contenido']);
            }
            
            actualizarEstadisticas();
        });
    }
    
    // Event listener para Unidad Didáctica
    const unidadDidacticaSelect = document.getElementById('unidad_didactica');
    if (unidadDidacticaSelect) {
        unidadDidacticaSelect.addEventListener('change', function() {
            const unidadDidacticaId = this.value;
            filtrosActivos.unidad_didactica = unidadDidacticaId;
            
            if (unidadDidacticaId) {
                cargarContenidosPorUnidadDidactica(unidadDidacticaId);
            } else {
                limpiarFiltrosInferiores(['contenido']);
            }
            
            actualizarEstadisticas();
        });
    }
}

// ===============================================
// FUNCIONES DE CARGA AJAX
// ===============================================

async function cargarCarrerasPorUnidad(unidadId) {
    mostrarCargando('carrera');
    
    try {
        const response = await fetch(`/visualizacion/ajax/carreras-por-unidad/?unidad_id=${unidadId}`);
        const data = await response.json();
        
        if (data.success) {
            populateSelect('carrera', data.carreras, 'id', 'display');
            limpiarFiltrosInferiores(['semestre', 'asignatura', 'unidad_didactica', 'contenido']);
        } else {
            console.error('Error al cargar carreras:', data.error);
        }
    } catch (error) {
        console.error('Error de red al cargar carreras:', error);
    } finally {
        ocultarCargando('carrera');
    }
}

async function cargarSemestresPorCarrera(carreraId) {
    mostrarCargando('semestre');
    
    try {
        const response = await fetch(`/visualizacion/ajax/semestres-por-carrera/?carrera_id=${carreraId}`);
        const data = await response.json();
        
        if (data.success) {
            populateSelect('semestre', data.semestres, 'numero', 'display');
        } else {
            console.error('Error al cargar semestres:', data.error);
        }
    } catch (error) {
        console.error('Error de red al cargar semestres:', error);
    } finally {
        ocultarCargando('semestre');
    }
}

async function cargarAsignaturasPorCarrera(carreraId) {
    mostrarCargando('asignatura');
    
    try {
        const response = await fetch(`/visualizacion/ajax/asignaturas-por-carrera/?carrera_id=${carreraId}`);
        const data = await response.json();
        
        if (data.success) {
            // Guardar todas las asignaturas para filtrar por semestre después
            window.todasLasAsignaturas = data.asignaturas;
            populateSelect('asignatura', data.asignaturas, 'id', 'display');
        } else {
            console.error('Error al cargar asignaturas:', data.error);
        }
    } catch (error) {
        console.error('Error de red al cargar asignaturas:', error);
    } finally {
        ocultarCargando('asignatura');
    }
}

function filtrarAsignaturasPorSemestre() {
    const semestreSeleccionado = document.getElementById('semestre').value;
    
    if (!semestreSeleccionado || !window.todasLasAsignaturas) {
        return;
    }
    
    const asignaturasFiltradas = window.todasLasAsignaturas.filter(
        asignatura => asignatura.semestre == semestreSeleccionado
    );
    
    populateSelect('asignatura', asignaturasFiltradas, 'id', 'display');
}

async function cargarUnidadesDidacticasPorAsignatura(asignaturaId) {
    mostrarCargando('unidad_didactica');
    
    try {
        const response = await fetch(`/visualizacion/ajax/unidades-didacticas-por-asignatura/?asignatura_id=${asignaturaId}`);
        const data = await response.json();
        
        if (data.success) {
            populateSelect('unidad_didactica', data.unidades_didacticas, 'id', 'display');
            limpiarFiltrosInferiores(['contenido']);
        } else {
            console.error('Error al cargar unidades didácticas:', data.error);
        }
    } catch (error) {
        console.error('Error de red al cargar unidades didácticas:', error);
    } finally {
        ocultarCargando('unidad_didactica');
    }
}

async function cargarContenidosPorUnidadDidactica(unidadDidacticaId) {
    mostrarCargando('contenido');
    
    try {
        const response = await fetch(`/visualizacion/ajax/contenidos-por-unidad-didactica/?unidad_didactica_id=${unidadDidacticaId}`);
        const data = await response.json();
        
        if (data.success) {
            populateSelect('contenido', data.contenidos, 'id', 'nombre');
        } else {
            console.error('Error al cargar contenidos:', data.error);
        }
    } catch (error) {
        console.error('Error de red al cargar contenidos:', error);
    } finally {
        ocultarCargando('contenido');
    }
}

// ===============================================
// FUNCIONES DE UTILIDAD
// ===============================================

function populateSelect(selectId, options, valueField, textField) {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    // Limpiar opciones existentes (mantener la opción "Todos")
    const primeraOpcion = select.querySelector('option[value=""]');
    select.innerHTML = '';
    
    if (primeraOpcion) {
        select.appendChild(primeraOpcion);
    } else {
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = `Todos los ${selectId.replace('_', ' ')}`;
        select.appendChild(defaultOption);
    }
    
    // Agregar nuevas opciones
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option[valueField];
        optionElement.textContent = option[textField];
        select.appendChild(optionElement);
    });
}

function limpiarFiltrosInferiores(filtros) {
    filtros.forEach(filtroId => {
        const select = document.getElementById(filtroId);
        if (select) {
            // Mantener solo la primera opción ("Todos")
            const primeraOpcion = select.querySelector('option[value=""]');
            select.innerHTML = '';
            if (primeraOpcion) {
                select.appendChild(primeraOpcion);
            }
            select.value = '';
        }
        
        // Limpiar del cache de filtros activos
        if (filtrosActivos[filtroId]) {
            delete filtrosActivos[filtroId];
        }
    });
}

function mostrarCargando(selectId) {
    const select = document.getElementById(selectId);
    if (select) {
        select.disabled = true;
        select.style.opacity = '0.6';
        
        // Agregar opción de "Cargando..."
        const loadingOption = document.createElement('option');
        loadingOption.value = 'loading';
        loadingOption.textContent = 'Cargando...';
        loadingOption.disabled = true;
        select.appendChild(loadingOption);
        select.value = 'loading';
    }
}

function ocultarCargando(selectId) {
    const select = document.getElementById(selectId);
    if (select) {
        select.disabled = false;
        select.style.opacity = '1';
        
        // Remover opción de "Cargando..."
        const loadingOption = select.querySelector('option[value="loading"]');
        if (loadingOption) {
            loadingOption.remove();
        }
    }
}

function obtenerCategoriaActual() {
    const categoriaBtn = document.querySelector('.category-btn.active');
    if (categoriaBtn) {
        const onclick = categoriaBtn.getAttribute('onclick');
        const match = onclick.match(/'(\w+)'/);
        return match ? match[1] : null;
    }
    return null;
}

// ===============================================
// ACTUALIZACIÓN DE ESTADÍSTICAS DINÁMICAS
// ===============================================

async function actualizarEstadisticas() {
    const categoria = obtenerCategoriaActual();
    if (!categoria) return;
    
    try {
        // Construir parámetros de consulta
        const params = new URLSearchParams({
            categoria: categoria,
            ...filtrosActivos
        });
        
        const response = await fetch(`/visualizacion/ajax/estadisticas-filtradas/?${params}`);
        const data = await response.json();
        
        if (data.success) {
            actualizarPanelEstadisticas(categoria, data.stats);
        } else {
            console.error('Error al cargar estadísticas:', data.error);
        }
    } catch (error) {
        console.error('Error de red al cargar estadísticas:', error);
    }
}

function actualizarPanelEstadisticas(categoria, stats) {
    const statsPanel = document.getElementById('statsPanel');
    if (!statsPanel) return;
    
    // Actualizar contadores según la categoría
    if (categoria === 'equipos') {
        actualizarContador('.stat-card:nth-child(1) h3', stats.total || 0);
        actualizarContador('.stat-card:nth-child(2) h3', stats.buenos || 0);
        actualizarContador('.stat-card:nth-child(3) h3', stats.regulares || 0);
        actualizarContador('.stat-card:nth-child(4) h3', stats.malos || 0);
    } else if (categoria === 'insumos') {
        actualizarContador('.stat-card:nth-child(1) h3', stats.total || 0);
        actualizarContador('.stat-card:nth-child(2) h3', 0); // categorías
        actualizarContador('.stat-card:nth-child(3) h3', stats.disponibles || 0);
        actualizarContador('.stat-card:nth-child(4) h3', stats.poco_stock || 0);
    } else if (categoria === 'guias') {
        actualizarContador('.stat-card:nth-child(1) h3', stats.total || 0);
        actualizarContador('.stat-card:nth-child(2) h3', 0); // prácticas
        actualizarContador('.stat-card:nth-child(3) h3', stats.aprobadas || 0);
        actualizarContador('.stat-card:nth-child(4) h3', stats.borradores || 0);
    }
}

function actualizarContador(selector, valor) {
    const elemento = document.querySelector(selector);
    if (elemento) {
        // Animación simple de contador
        const valorActual = parseInt(elemento.textContent) || 0;
        
        if (valorActual !== valor) {
            elemento.style.transform = 'scale(1.1)';
            elemento.style.color = '#1e40af';
            
            setTimeout(() => {
                elemento.textContent = valor;
                elemento.style.transform = 'scale(1)';
                elemento.style.color = '#1e3a8a';
            }, 150);
        }
    }
}

// ===============================================
// FUNCIONES DE APLICAR Y LIMPIAR FILTROS
// ===============================================

function aplicarFiltros() {
    // Los filtros ya se aplican automáticamente por AJAX
    // Esta función puede recargar la página si es necesario
    const categoria = obtenerCategoriaActual();
    if (!categoria) return;
    
    const url = new URL(window.location);
    url.searchParams.set('categoria', categoria);
    
    // Agregar filtros activos a la URL
    Object.keys(filtrosActivos).forEach(key => {
        if (filtrosActivos[key]) {
            url.searchParams.set(key, filtrosActivos[key]);
        }
    });
    
    window.location.href = url.toString();
}

function limpiarFiltros() {
    // Limpiar todos los selectores
    const selectores = ['unidad_academica', 'carrera', 'semestre', 'asignatura', 'unidad_didactica', 'contenido'];
    
    selectores.forEach(selectorId => {
        const select = document.getElementById(selectorId);
        if (select) {
            select.value = '';
        }
    });
    
    // Limpiar filtros activos
    filtrosActivos = {};
    
    // Limpiar filtros inferiores
    limpiarFiltrosInferiores(['carrera', 'semestre', 'asignatura', 'unidad_didactica', 'contenido']);
    
    // Actualizar estadísticas
    actualizarEstadisticas();
}

// Función para exportar Excel con filtros aplicados
function exportarExcel(categoria) {
    const params = new URLSearchParams({
        categoria: categoria,
        ...filtrosActivos
    });
    
    window.location.href = `/visualizacion/exportar-excel/?${params}`;
}

// ===============================================
// SISTEMA DE CORRELACIONES CRÍTICO
// ===============================================

// Variables globales para correlaciones
let correlacionesCache = {};
let elementoSeleccionado = null;

// Mostrar correlaciones de un equipo específico
async function mostrarCorrelacionesEquipo(equipoId) {
    try {
        mostrarCargandoCorrelaciones();
        
        const response = await fetch(`/visualizacion/ajax/correlaciones-equipo/?equipo_id=${equipoId}`);
        const data = await response.json();
        
        if (data.success) {
            elementoSeleccionado = { tipo: 'equipo', data: data };
            correlacionesCache[`equipo_${equipoId}`] = data;
            renderizarPanelCorrelaciones(data);
        } else {
            console.error('Error al cargar correlaciones:', data.error);
        }
    } catch (error) {
        console.error('Error de red al cargar correlaciones:', error);
    } finally {
        ocultarCargandoCorrelaciones();
    }
}

// Mostrar correlaciones de una guía específica
async function mostrarCorrelacionesGuia(guiaId) {
    try {
        mostrarCargandoCorrelaciones();
        
        const response = await fetch(`/visualizacion/ajax/correlaciones-guia/?guia_id=${guiaId}`);
        const data = await response.json();
        
        if (data.success) {
            elementoSeleccionado = { tipo: 'guia', data: data };
            correlacionesCache[`guia_${guiaId}`] = data;
            renderizarPanelCorrelaciones(data);
        } else {
            console.error('Error al cargar correlaciones:', data.error);
        }
    } catch (error) {
        console.error('Error de red al cargar correlaciones:', error);
    } finally {
        ocultarCargandoCorrelaciones();
    }
}

// Mostrar correlaciones de un insumo específico
async function mostrarCorrelacionesInsumo(insumoId) {
    try {
        mostrarCargandoCorrelaciones();
        
        const response = await fetch(`/visualizacion/ajax/correlaciones-insumo/?insumo_id=${insumoId}`);
        const data = await response.json();
        
        if (data.success) {
            elementoSeleccionado = { tipo: 'insumo', data: data };
            correlacionesCache[`insumo_${insumoId}`] = data;
            renderizarPanelCorrelaciones(data);
        } else {
            console.error('Error al cargar correlaciones:', data.error);
        }
    } catch (error) {
        console.error('Error de red al cargar correlaciones:', error);
    } finally {
        ocultarCargandoCorrelaciones();
    }
}

// Cargar resumen general de correlaciones
async function cargarResumenCorrelaciones() {
    try {
        const response = await fetch('/visualizacion/ajax/resumen-correlaciones/');
        const data = await response.json();
        
        if (data.success) {
            renderizarResumenCorrelaciones(data.resumen);
        } else {
            console.error('Error al cargar resumen:', data.error);
        }
    } catch (error) {
        console.error('Error de red al cargar resumen:', error);
    }
}

// Renderizar panel de correlaciones
function renderizarPanelCorrelaciones(data) {
    const panel = document.getElementById('correlacionesPanel');
    if (!panel) return;
    
    let html = '';
    
    if (data.equipo) {
        // Panel para correlaciones de equipo
        html = `
            <div class="correlaciones-header">
                <h4>🔧 ${data.equipo.nombre}</h4>
                <span class="badge badge-${getBadgeClass(data.equipo.estado)}">${data.equipo.estado}</span>
            </div>
            
            <div class="correlaciones-stats">
                <div class="stat-mini">
                    <span class="number">${data.correlaciones.total_guias}</span>
                    <span class="label">Guías</span>
                </div>
                <div class="stat-mini">
                    <span class="number">${data.correlaciones.total_insumos}</span>
                    <span class="label">Insumos</span>
                </div>
            </div>
            
            <div class="correlaciones-content">
                <h5>📋 Guías que usan este equipo:</h5>
                <ul class="correlaciones-list">
        `;
        
        if (data.correlaciones.guias_relacionadas.length > 0) {
            data.correlaciones.guias_relacionadas.forEach(guia => {
                html += `
                    <li onclick="mostrarCorrelacionesGuia(${guia.id})" class="correlacion-item">
                        <span class="correlacion-nombre">${guia.titulo}</span>
                        <span class="correlacion-info">${guia.carrera} - ${guia.asignatura}</span>
                        <span class="badge badge-${getBadgeClass(guia.estado)}">${guia.estado}</span>
                    </li>
                `;
            });
        } else {
            html += '<li class="no-correlaciones">No hay guías asociadas</li>';
        }
        
        html += '</ul></div>';
        
    } else if (data.guia) {
        // Panel para correlaciones de guía
        html = `
            <div class="correlaciones-header">
                <h4>📋 ${data.guia.titulo}</h4>
                <span class="badge badge-${getBadgeClass(data.guia.estado)}">${data.guia.estado}</span>
            </div>
            
            <div class="correlaciones-stats">
                <div class="stat-mini">
                    <span class="number">${data.correlaciones.total_equipos}</span>
                    <span class="label">Equipos</span>
                </div>
                <div class="stat-mini">
                    <span class="number">${data.correlaciones.total_insumos}</span>
                    <span class="label">Insumos</span>
                </div>
            </div>
            
            <div class="correlaciones-content">
                <h5>🔧 Equipos necesarios:</h5>
                <ul class="correlaciones-list">
        `;
        
        if (data.correlaciones.equipos_requeridos.length > 0) {
            data.correlaciones.equipos_requeridos.forEach(equipo => {
                html += `
                    <li onclick="mostrarCorrelacionesEquipo(${equipo.id})" class="correlacion-item">
                        <span class="correlacion-nombre">${equipo.nombre}</span>
                        <span class="correlacion-info">${equipo.laboratorio}</span>
                        <span class="badge badge-${getBadgeClass(equipo.estado)}">${equipo.estado}</span>
                    </li>
                `;
            });
        } else {
            html += '<li class="no-correlaciones">No requiere equipos</li>';
        }
        
        html += '</ul>';
        
        // Mostrar insumos si existen
        if (data.correlaciones.insumos_requeridos.length > 0) {
            html += `
                <h5>🧪 Insumos necesarios:</h5>
                <ul class="correlaciones-list">
            `;
            
            data.correlaciones.insumos_requeridos.forEach(insumo => {
                html += `
                    <li class="correlacion-item">
                        <span class="correlacion-nombre">${insumo.nombre}</span>
                        <span class="correlacion-info">${insumo.cantidad} ${insumo.unidad}</span>
                        <span class="badge badge-${getBadgeClass(insumo.estado)}">${insumo.estado}</span>
                    </li>
                `;
            });
            
            html += '</ul>';
        }
        
        html += '</div>';
        
    } else if (data.insumo) {
        // Panel para correlaciones de insumo
        html = `
            <div class="correlaciones-header">
                <h4>🧪 ${data.insumo.nombre}</h4>
                <span class="badge badge-${getBadgeClass(data.insumo.estado)}">${data.insumo.estado}</span>
            </div>
            
            <div class="correlaciones-stats">
                <div class="stat-mini">
                    <span class="number">${data.total_guias}</span>
                    <span class="label">Guías</span>
                </div>
                <div class="stat-mini">
                    <span class="number">${data.total_equipos_relacionados}</span>
                    <span class="label">Equipos Relacionados</span>
                </div>
            </div>
            
            <div class="correlaciones-content">
                <div class="insumo-info">
                    <p><strong>Categoría:</strong> ${data.insumo.categoria}</p>
                    <p><strong>Cantidad:</strong> ${data.insumo.cantidad} ${data.insumo.unidad_medida}</p>
                    <p><strong>Descripción:</strong> ${data.insumo.descripcion}</p>
                </div>
                
                <h5>📋 Guías que requieren este insumo:</h5>
                <ul class="correlaciones-list">
        `;
        
        if (data.guias_relacionadas.length > 0) {
            data.guias_relacionadas.forEach(guia => {
                html += `
                    <li onclick="mostrarCorrelacionesGuia(${guia.id})" class="correlacion-item">
                        <span class="correlacion-nombre">${guia.titulo}</span>
                        <span class="correlacion-info">${guia.carrera} - ${guia.asignatura}</span>
                        <div class="correlacion-equipos">
                            <span class="equipos-count">🔧 ${guia.total_equipos} equipos relacionados</span>
                        </div>
                    </li>
                `;
            });
        } else {
            html += '<li class="no-correlaciones">No hay guías que requieren este insumo</li>';
        }
        
        html += '</ul></div>';
    }
    
    panel.innerHTML = html;
    panel.style.display = 'block';
}

// Renderizar resumen general de correlaciones
function renderizarResumenCorrelaciones(resumen) {
    const panel = document.getElementById('resumenCorrelacionesPanel');
    if (!panel) return;
    
    const html = `
        <div class="resumen-header">
            <h4>📊 Resumen de Correlaciones</h4>
        </div>
        
        <div class="resumen-stats">
            <div class="stat-card-mini">
                <h5>${resumen.total_guias}</h5>
                <p>Total Guías</p>
            </div>
            <div class="stat-card-mini">
                <h5>${resumen.guias_con_equipos}</h5>
                <p>Con Equipos</p>
            </div>
            <div class="stat-card-mini">
                <h5>${resumen.equipos_en_guias}</h5>
                <p>Equipos Utilizados</p>
            </div>
            <div class="stat-card-mini">
                <h5>${resumen.porcentaje_equipos_utilizados}%</h5>
                <p>% Uso</p>
            </div>
        </div>
        
        <div class="equipos-populares">
            <h5>🏆 Equipos Más Utilizados</h5>
            <ul class="equipos-populares-list">
                ${resumen.equipos_mas_utilizados.map(equipo => `
                    <li onclick="mostrarCorrelacionesEquipo(${equipo.id})" class="equipo-popular">
                        <span class="equipo-nombre">${equipo.nombre}</span>
                        <span class="equipo-usos">${equipo.usos} guías</span>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
    
    panel.innerHTML = html;
}

// Funciones auxiliares para correlaciones
function getBadgeClass(estado) {
    const clases = {
        'bueno': 'success',
        'regular': 'warning', 
        'malo': 'danger',
        'aprobada': 'success',
        'revision': 'warning',
        'borrador': 'secondary'
    };
    return clases[estado] || 'secondary';
}

function mostrarCargandoCorrelaciones() {
    const panel = document.getElementById('correlacionesPanel');
    if (panel) {
        panel.innerHTML = '<div class="loading-correlaciones">🔄 Cargando correlaciones...</div>';
        panel.style.display = 'block';
    }
}

function ocultarCargandoCorrelaciones() {
    // Se oculta automáticamente cuando se renderiza el contenido
}

function cerrarPanelCorrelaciones() {
    const panel = document.getElementById('correlacionesPanel');
    if (panel) {
        panel.style.display = 'none';
    }
    elementoSeleccionado = null;
}

// ===============================================
// FUNCIONES DE EXPORTACIÓN AVANZADA PARA DOCENTES
// ===============================================

function exportarExcelAvanzado(categoria) {
    const params = new URLSearchParams({
        categoria: categoria || obtenerCategoriaActual(),
        ...filtrosActivos
    });
    
    // Mostrar indicador de carga
    mostrarIndicadorExportacion('Excel');
    
    window.location.href = `/visualizacion/exportar-excel-avanzado/?${params}`;
    
    // Ocultar indicador después de un tiempo
    setTimeout(() => {
        ocultarIndicadorExportacion();
    }, 3000);
}

function exportarPDFGuia(guiaId) {
    if (!guiaId) {
        alert('ID de guía requerido para exportar PDF');
        return;
    }
    
    mostrarIndicadorExportacion('PDF');
    
    const url = `/visualizacion/exportar-pdf-guia/?guia_id=${guiaId}`;
    
    // Crear enlace temporal para descarga
    const link = document.createElement('a');
    link.href = url;
    link.click();
    
    setTimeout(() => {
        ocultarIndicadorExportacion();
    }, 2000);
}

function exportarGuiasFiltradas() {
    const params = new URLSearchParams(filtrosActivos);
    
    mostrarIndicadorExportacion('PDF de Guías');
    
    const url = `/visualizacion/exportar-guias-pdf/?${params}`;
    
    // Crear enlace temporal para descarga
    const link = document.createElement('a');
    link.href = url;
    link.click();
    
    setTimeout(() => {
        ocultarIndicadorExportacion();
    }, 3000);
}

function mostrarIndicadorExportacion(tipo) {
    // Crear o mostrar indicador de exportación
    let indicador = document.getElementById('exportacion-indicador');
    
    if (!indicador) {
        indicador = document.createElement('div');
        indicador.id = 'exportacion-indicador';
        indicador.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #1e40af;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        document.body.appendChild(indicador);
    }
    
    indicador.innerHTML = `
        <div class="spinner" style="
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        "></div>
        <span>Exportando ${tipo}...</span>
    `;
    
    indicador.style.display = 'flex';
    
    // Agregar animación CSS si no existe
    if (!document.getElementById('spinner-style')) {
        const style = document.createElement('style');
        style.id = 'spinner-style';
        style.textContent = `
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
}

function ocultarIndicadorExportacion() {
    const indicador = document.getElementById('exportacion-indicador');
    if (indicador) {
        indicador.style.display = 'none';
    }
}

// Función mejorada para exportación desde botones de correlaciones
function exportarGuiaCompleta(guiaId, tituloGuia) {
    const confirmacion = confirm(
        `¿Deseas exportar la guía "${tituloGuia}" a PDF con todos los equipos e insumos requeridos?`
    );
    
    if (confirmacion) {
        exportarPDFGuia(guiaId);
    }
}

// Función para mostrar opciones de exportación
function mostrarOpcionesExportacion() {
    const categoria = obtenerCategoriaActual();
    
    let opciones = `
        <div id="modal-exportacion" style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 12px;
                min-width: 400px;
                max-width: 500px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            ">
                <h3 style="margin: 0 0 20px 0; color: #1e40af;">📄 Opciones de Exportación</h3>
                
                <div style="margin-bottom: 15px;">
                    <button onclick="exportarExcelAvanzado('${categoria}')" style="
                        width: 100%;
                        padding: 12px;
                        background: #16a34a;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 14px;
                        cursor: pointer;
                        margin-bottom: 10px;
                    ">
                        📊 Excel Avanzado con Correlaciones
                    </button>
                </div>
    `;
    
    if (categoria === 'guias') {
        opciones += `
                <div style="margin-bottom: 15px;">
                    <button onclick="exportarGuiasFiltradas()" style="
                        width: 100%;
                        padding: 12px;
                        background: #dc2626;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 14px;
                        cursor: pointer;
                        margin-bottom: 10px;
                    ">
                        📑 PDF de Guías Filtradas
                    </button>
                </div>
        `;
    }
    
    opciones += `
                <div style="text-align: right;">
                    <button onclick="cerrarModalExportacion()" style="
                        padding: 8px 16px;
                        background: #6b7280;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    ">
                        Cancelar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', opciones);
}

function cerrarModalExportacion() {
    const modal = document.getElementById('modal-exportacion');
    if (modal) {
        modal.remove();
    }
}