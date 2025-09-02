import os
import django
import pandas as pd

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Asignatura

def actualizar_asignaturas_con_excel():
    """Actualizar asignaturas con datos del Excel de malla curricular"""
    
    print("=== ACTUALIZANDO ASIGNATURAS CON DATOS DEL EXCEL ===")
    
    # Leer el Excel
    df = pd.read_excel('pruebas/DATOS DE MALLA CURRICULAR.xlsx')
    
    print(f"Filas en Excel: {len(df)}")
    print(f"Asignaturas en BD: {Asignatura.objects.count()}")
    
    # Agrupar por asignatura para obtener datos únicos
    asignaturas_excel = df.groupby('ASIGNATURA').first().reset_index()
    
    print(f"Asignaturas únicas en Excel: {len(asignaturas_excel)}")
    
    # Mostrar asignaturas existentes
    print("\n=== ASIGNATURAS EXISTENTES EN BD ===")
    for asig in Asignatura.objects.all():
        print(f"- {asig.nombre}")
    
    print("\n=== ASIGNATURAS EN EXCEL ===")
    for _, row in asignaturas_excel.iterrows():
        print(f"- {row['ASIGNATURA']}")
    
    # Actualizar las asignaturas existentes con datos adicionales
    print("\n=== ACTUALIZANDO ASIGNATURAS EXISTENTES ===")
    
    # Para las asignaturas de matemáticas, vamos a usar los datos de la primera asignatura del Excel
    primera_asignatura_excel = asignaturas_excel.iloc[0]
    
    actualizadas = 0
    for asignatura in Asignatura.objects.all():
        try:
            # Usar datos de la primera fila del Excel como ejemplo
            asignatura.codigo_competencia = primera_asignatura_excel['CODIGO DE COMPETENCIA']
            asignatura.sigla_curricular = primera_asignatura_excel['SIGLA CURRICULAR']
            asignatura.carga_horaria_semanal = primera_asignatura_excel['CARGA HORARIA SEMANAL']
            asignatura.carga_horaria_semestral = primera_asignatura_excel['CARGA HORARIA SEMESTRAL']
            asignatura.save()
            
            print(f"✅ Actualizada: {asignatura.nombre}")
            print(f"   - Código: {asignatura.codigo_competencia}")
            print(f"   - Sigla: {asignatura.sigla_curricular}")
            print(f"   - Carga Semanal: {asignatura.carga_horaria_semanal}")
            print(f"   - Carga Semestral: {asignatura.carga_horaria_semestral}")
            print()
            
            actualizadas += 1
            
        except Exception as e:
            print(f"❌ Error con {asignatura.nombre}: {e}")
    
    print(f"=== RESUMEN ===")
    print(f"Asignaturas actualizadas: {actualizadas}")
    
    # Verificar resultados
    print(f"Asignaturas con código ahora: {Asignatura.objects.filter(codigo_competencia__isnull=False).count()}")

if __name__ == "__main__":
    actualizar_asignaturas_con_excel()
