# 🔍 DEBUGGING CKEditor - Paso a Paso

## 🎯 Instrucciones para Debugging

### Paso 1: Acceder al Formulario
1. Abrir: http://127.0.0.1:8001/dashboard/malla-curricular/agregar-datos/
2. Hacer login si es necesario
3. Llenar campos básicos del formulario

### Paso 2: Preparar Herramientas de Desarrollador
1. Presionar **F12** para abrir Developer Tools
2. Ir a la pestaña **Console**
3. Limpiar la consola (botón 🗑️)

### Paso 3: Agregar Grupo y Observar Logs
1. Hacer clic en **"Agregar Grupo de Datos Adicionales"**
2. **OBSERVAR** los logs en la consola
3. Deberías ver logs como:
   ```
   ➕ Grupo agregado - Contenido: 0, Grupo: 0
   🔥 Inicializando CKEditor INMEDIATAMENTE...
   🎯 Intento 1 (100ms)
   🔧 Inicialización SIMPLE de CKEditor...
   📝 Campos encontrados: 7
   🚀 Inicializando campo: ckeditor_[timestamp]_0
   ✅ CKEditor LISTO: ckeditor_[timestamp]_0
   ```

### Paso 4: Usar Botón Debug CKEditor
1. Después de agregar un grupo, hacer clic en **"Debug CKEditor"** (botón rojo)
2. Este botón ejecuta `window.debugCKEditor()` que muestra:
   - Si CKEDITOR está disponible
   - Cuántos campos `.ckeditor-field` encuentra
   - Cuántas instancias de CKEditor están activas
   - Estado de cada campo

### Paso 5: Verificar Campos Manualmente
1. En la consola, ejecutar: `document.querySelectorAll('.ckeditor-field')`
2. Debería mostrar un NodeList con 7 elementos
3. Verificar que cada elemento tenga:
   - `name` con patrón correcto (ej: `fundamento_teorico_0_0`)
   - `class` conteniendo `ckeditor-field`
   - `id` asignado automáticamente

### Paso 6: Verificar Instancias CKEditor
1. En la consola, ejecutar: `Object.keys(CKEDITOR.instances)`
2. Debería mostrar array con los IDs de los editores inicializados
3. Para cada instancia, verificar: `CKEDITOR.instances['id_del_campo']`

## 🚨 Problemas Comunes y Soluciones

### Problema 1: "CKEDITOR no disponible"
**Síntoma:** Error en consola "CKEDITOR no está disponible"
**Solución:** 
- Verificar conexión a internet (CDN)
- Recargar página (F5)
- Verificar que no hay bloqueadores de ads

### Problema 2: "Campos encontrados: 0"
**Síntoma:** La función no encuentra campos `.ckeditor-field`
**Solución:**
- Verificar que agregaste un grupo correctamente
- Inspeccionar elemento para ver si el HTML se generó
- Ejecutar: `document.querySelectorAll('.ckeditor-field')`

### Problema 3: "Instancias: 0"
**Síntoma:** CKEditor no se inicializa aunque encuentra campos
**Solución:**
- Ejecutar manualmente: `initializeCKEditorSimple()`
- Verificar errores en consola
- Intentar configuración más básica

### Problema 4: Campos aparecen pero sin toolbar
**Síntoma:** Textareas normales sin barras de herramientas
**Solución:**
- Verificar que `CKEDITOR.instances` tiene las instancias
- Forzar re-inicialización con botón Debug
- Verificar que no hay errores CSS que oculten toolbars

## 📋 Checklist de Verificación

- [ ] Servidor Django corriendo en puerto 8001
- [ ] Página carga sin errores 404/500
- [ ] Console abierta y limpia
- [ ] Grupo de datos adicionales agregado
- [ ] Logs de inicialización aparecen en console
- [ ] Botón "Debug CKEditor" responde
- [ ] Se encuentran 7 campos `.ckeditor-field`
- [ ] CKEDITOR.instances tiene entradas
- [ ] Textareas muestran barras de herramientas

## 🔧 Comandos de Debug Manual

Ejecutar en la consola del navegador:

```javascript
// Verificar CKEDITOR
console.log('CKEDITOR disponible:', typeof CKEDITOR !== 'undefined');

// Contar campos
console.log('Campos .ckeditor-field:', document.querySelectorAll('.ckeditor-field').length);

// Ver instancias
console.log('Instancias activas:', Object.keys(CKEDITOR.instances));

// Forzar inicialización
initializeCKEditorSimple();

// Debug completo
window.debugCKEditor();
```

## 🎯 Resultado Esperado

Si todo funciona correctamente:
1. ✅ Console muestra logs de inicialización exitosa
2. ✅ 7 campos con clase `.ckeditor-field` se encuentran
3. ✅ 7 instancias en `CKEDITOR.instances`
4. ✅ Cada textarea muestra una barra de herramientas arriba
5. ✅ Puedes hacer clic en los botones de formato (Bold, Italic, etc.)
6. ✅ Los campos se comportan como editores de texto enriquecido