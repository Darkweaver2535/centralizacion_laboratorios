from django.core.management.base import BaseCommand
from ingreso_datos.models import TipoEquipo, EquipoIndividual
import random

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
                defaults={
                    'capacidad_estudiantes': capacidad,
                    'descripcion': f'Equipo de laboratorio - {display_name}'
                }
            )
            if created:
                self.stdout.write(f'Tipo de equipo creado: {display_name}')
            else:
                self.stdout.write(f'Tipo de equipo ya existe: {display_name}')

        # Crear equipos individuales de ejemplo
        estados_fisicos = ['bueno', 'regular', 'malo']
        estados_operativos = ['operativo', 'mantenimiento', 'reparacion']
        
        # Prefijos para códigos según el tipo de equipo
        prefijos_codigo = {
            'microscopio_optico': 'MO',
            'balanza_analitica': 'BA',
            'espectrofotometro': 'ES',
            'centrifuga': 'CE',
            'autoclave': 'AU',
            'incubadora': 'IN',
            'ph_metro': 'PH',
            'agitador_magnetico': 'AM',
            'campana_extractora': 'CA',
            'mechero_bunsen': 'MB',
        }

        for tipo_equipo in TipoEquipo.objects.all():
            prefijo = prefijos_codigo.get(tipo_equipo.nombre, 'EQ')
            
            # Crear entre 15-25 equipos por tipo
            cantidad = random.randint(15, 25)
            
            for i in range(1, cantidad + 1):
                codigo = f"{prefijo}-{i:03d}"
                
                # Distribuir estados de forma realista
                if i <= cantidad * 0.7:  # 70% en buen estado
                    estado_fisico = 'bueno'
                    estado_operativo = 'operativo'
                elif i <= cantidad * 0.9:  # 20% en estado regular
                    estado_fisico = 'regular'
                    estado_operativo = random.choice(['operativo', 'mantenimiento'])
                else:  # 10% en mal estado
                    estado_fisico = 'malo'
                    estado_operativo = random.choice(['reparacion', 'inoperativo'])
                
                equipo_individual, created = EquipoIndividual.objects.get_or_create(
                    codigo=codigo,
                    defaults={
                        'tipo_equipo': tipo_equipo,
                        'estado_fisico': estado_fisico,
                        'estado_operativo': estado_operativo,
                        'ubicacion': f'Laboratorio {random.choice(["A", "B", "C"])}-{random.randint(1, 20)}',
                        'observaciones': f'Equipo {codigo} - Estado {estado_fisico}'
                    }
                )
                
                if created:
                    self.stdout.write(f'Equipo creado: {equipo_individual}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Equipos creados exitosamente!')
        )