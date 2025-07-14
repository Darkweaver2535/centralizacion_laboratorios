from django.core.management.base import BaseCommand
from ingreso_datos.models import TipoEquipo, EquipoIndividual

class Command(BaseCommand):
    help = 'Crear equipos individuales de ejemplo'

    def handle(self, *args, **options):
        # Crear tipos de equipo con capacidades
        tipos_equipo_data = [
            ('microscopio_optico', 'Microscopio Óptico', 1),
            ('balanza_analitica', 'Balanza Analítica', 1),
            ('espectrofotometro', 'Espectrofotómetro', 2),
            ('centrifuga', 'Centrífuga', 1),
            ('autoclave', 'Autoclave', 4),
            ('incubadora', 'Incubadora', 3),
            ('ph_metro', 'pH Metro', 1),
            ('agitador_magnetico', 'Agitador Magnético', 1),
            ('campana_extractora', 'Campana Extractora', 2),
            ('mechero_bunsen', 'Mechero Bunsen', 1),
        ]

        for nombre, display_name, capacidad in tipos_equipo_data:
            tipo_equipo, created = TipoEquipo.objects.get_or_create(
                nombre=nombre,
                defaults={'capacidad_estudiantes': capacidad}
            )
            if created:
                self.stdout.write(f'Tipo de equipo creado: {display_name}')

        # Crear equipos individuales de ejemplo
        equipos_data = [
            # Microscopios Ópticos (15 unidades)
            ('microscopio_optico', ['MO-001', 'MO-002', 'MO-003', 'MO-004', 'MO-005', 
                                   'MO-006', 'MO-007', 'MO-008', 'MO-009', 'MO-010',
                                   'MO-011', 'MO-012', 'MO-013', 'MO-014', 'MO-015']),
            
            # Balanzas Analíticas (10 unidades)
            ('balanza_analitica', ['BA-001', 'BA-002', 'BA-003', 'BA-004', 'BA-005',
                                  'BA-006', 'BA-007', 'BA-008', 'BA-009', 'BA-010']),
            
            # Espectrofotómetros (6 unidades)
            ('espectrofotometro', ['ES-001', 'ES-002', 'ES-003', 'ES-004', 'ES-005', 'ES-006']),
            
            # Centrífugas (8 unidades)
            ('centrifuga', ['CF-001', 'CF-002', 'CF-003', 'CF-004', 'CF-005', 'CF-006', 'CF-007', 'CF-008']),
            
            # Autoclaves (3 unidades)
            ('autoclave', ['AC-001', 'AC-002', 'AC-003']),
            
            # Incubadoras (5 unidades)
            ('incubadora', ['IN-001', 'IN-002', 'IN-003', 'IN-004', 'IN-005']),
            
            # pH Metros (12 unidades)
            ('ph_metro', ['PH-001', 'PH-002', 'PH-003', 'PH-004', 'PH-005', 'PH-006',
                         'PH-007', 'PH-008', 'PH-009', 'PH-010', 'PH-011', 'PH-012']),
            
            # Agitadores Magnéticos (20 unidades)
            ('agitador_magnetico', ['AM-001', 'AM-002', 'AM-003', 'AM-004', 'AM-005',
                                   'AM-006', 'AM-007', 'AM-008', 'AM-009', 'AM-010',
                                   'AM-011', 'AM-012', 'AM-013', 'AM-014', 'AM-015',
                                   'AM-016', 'AM-017', 'AM-018', 'AM-019', 'AM-020']),
            
            # Campanas Extractoras (4 unidades)
            ('campana_extractora', ['CE-001', 'CE-002', 'CE-003', 'CE-004']),
            
            # Mecheros Bunsen (25 unidades)
            ('mechero_bunsen', ['MB-001', 'MB-002', 'MB-003', 'MB-004', 'MB-005',
                               'MB-006', 'MB-007', 'MB-008', 'MB-009', 'MB-010',
                               'MB-011', 'MB-012', 'MB-013', 'MB-014', 'MB-015',
                               'MB-016', 'MB-017', 'MB-018', 'MB-019', 'MB-020',
                               'MB-021', 'MB-022', 'MB-023', 'MB-024', 'MB-025']),
        ]

        for tipo_nombre, codigos in equipos_data:
            tipo_equipo = TipoEquipo.objects.get(nombre=tipo_nombre)
            
            for codigo in codigos:
                equipo, created = EquipoIndividual.objects.get_or_create(
                    tipo_equipo=tipo_equipo,
                    codigo=codigo,
                    defaults={'estado': 'operativo'}
                )
                if created:
                    self.stdout.write(f'Equipo creado: {equipo}')

        self.stdout.write(self.style.SUCCESS('Equipos de ejemplo creados exitosamente'))