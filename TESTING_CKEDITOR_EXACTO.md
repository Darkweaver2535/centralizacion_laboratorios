# 🎯 INSTRUCCIONES EXACTAS para Testing CKEditor

## 🚀 Pasos EXACTOS para Verificar CKEditor

### 1. Preparación
1. ✅ Servidor debe estar corriendo: `python manage.py runserver 8001`
2. ✅ Abrir: http://127.0.0.1:8001/dashboard/malla-curricular/agregar-datos/
3. ✅ Si pide login, usar cualquier usuario válido
4. ✅ Presionar **F12** → pestaña **Console**

### 2. Llenar Formulario Básico
1. **Unidad Académica**: Seleccionar cualquiera
2. **Carrera**: Seleccionar basada en unidad  
3. **Asignatura**: Seleccionar cualquiera
4. **Contenido Analítico**: Escribir "Test CKEditor"
5. **Unidad Didáctica**: Escribir "Test"

### 3. Test Paso a Paso

#### Paso 3.1: Agregar Grupo
1. Hacer clic en **"Agregar Grupo de Datos Adicionales"**
2. **OBSERVAR Console** - debería mostrar:
   ```
   ➕ Grupo agregado - Contenido: 0, Grupo: 0
   🔥 Inicializando CKEditor INMEDIATAMENTE...
   🎯 Intento 1 (100ms)
   🔧 Inicialización SIMPLE de CKEditor...
   ```

#### Paso 3.2: Test Básico (NUEVO)
1. Hacer clic en botón **"Test Básico"** (color azul verdoso)
2. Debería aparecer un alert: **"¡CKEditor básico funcionando!"**
3. **Verificar** que el campo "Fundamento Teórico" ahora tiene una barra de herramientas

#### Paso 3.3: Debug Completo  
1. Hacer clic en botón **"Debug CKEditor"** (color rojo)
2. **Observar Console** - debería mostrar información detallada

### 4. Verificación Visual

#### ✅ Lo que DEBERÍA verse:
- **Fundamento Teórico**: Textarea con barra de herramientas arriba
- **Materiales**: Textarea con barra de herramientas
- **Herramientas**: Textarea con barra de herramientas  
- **Equipos**: Textarea con barra de herramientas
- **Procedimientos**: Textarea con barra de herramientas
- **Cálculos y Resultados**: Textarea con barra de herramientas
- **Cuestionario**: Textarea con barra de herramientas

#### ❌ Lo que NO debería verse:
- Textareas simples sin barras de herramientas
- Errores en la console
- Botones que no responden

### 5. Tests de Funcionalidad

Si aparecen las barras de herramientas:

1. **Test Bold**: Hacer clic en **B** → escribir texto → debería aparecer en negritas
2. **Test Italic**: Hacer clic en **I** → escribir texto → debería aparecer en cursiva  
3. **Test Lists**: Hacer clic en botón de lista → crear lista
4. **Test Images**: Hacer clic en botón imagen → debería abrir dialog

## 🚨 Troubleshooting

### Problema A: No aparecen barras de herramientas
**Posible causa**: CKEDITOR no se carga desde CDN
**Solución**:
1. Verificar conexión a internet
2. En Console ejecutar: `typeof CKEDITOR`
3. Debería devolver `"object"`, no `"undefined"`

### Problema B: Error "CKEDITOR no disponible"  
**Posible causa**: Bloqueador de ads o firewall
**Solución**:
1. Desactivar bloqueadores temporalmente
2. Recargar página (F5)
3. Verificar que no hay errores de red en Network tab

### Problema C: Campos no se encuentran
**Posible causa**: HTML no se generó correctamente
**Solución**:
1. Verificar que hiciste clic en "Agregar Grupo"
2. En Console ejecutar: `document.querySelectorAll('.ckeditor-field').length`
3. Debería devolver `7`

### Problema D: Test básico no funciona
**Posible causa**: Timing o configuración
**Solución**:
1. Esperar 2-3 segundos después de agregar grupo
2. Volver a hacer clic en "Test Básico"
3. Verificar Console por errores específicos

## 📋 Comandos de Emergency Debug

Si nada funciona, ejecutar en Console:

```javascript
// Verificación completa
console.log('=== EMERGENCY DEBUG ===');
console.log('1. CKEDITOR:', typeof CKEDITOR);
console.log('2. Campos:', document.querySelectorAll('.ckeditor-field').length);
console.log('3. Instancias:', Object.keys(CKEDITOR.instances || {}));

// Forzar inicialización manual
if (typeof CKEDITOR !== 'undefined') {
    const field = document.querySelector('.ckeditor-field');
    if (field) {
        field.id = 'emergency_test';
        CKEDITOR.replace('emergency_test', {toolbar: [['Bold']]});
        console.log('4. Emergency editor creado');
    }
}
```

## 🎯 Resultado Final Esperado

**✅ ÉXITO se ve así:**
1. Grupo de datos adicionales aparece con 7 campos
2. Cada campo tiene una barra gris arriba con botones
3. Botones Bold, Italic, etc. son clickeables  
4. Al escribir y usar formato, el texto se ve enriquecido
5. Console muestra logs sin errores

**❌ FALLO se ve así:**
1. Campos aparecen como textareas normales
2. No hay barras de herramientas
3. Console muestra errores rojos
4. Botones Debug/Test no responden

---

**🔥 PRUEBA ESTE PROCESO EXACTO y reporta qué ves en cada paso**