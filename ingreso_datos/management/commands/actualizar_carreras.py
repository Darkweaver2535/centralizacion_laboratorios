from django.core.management.base import BaseCommand
from ingreso_datos.models import Carrera

class Command(BaseCommand):
    help = 'Actualiza las carreras en la base de datos con las nuevas opciones'

    def handle(self, *args, **options):
        # Crear todas las carreras definidas en el modelo
        carreras_creadas = 0
        carreras_actualizadas = 0
        
        for codigo, nombre in Carrera.CARRERAS:
            carrera, created = Carrera.objects.get_or_create(
                nombre=codigo,
                defaults={'descripcion': f'Carrera de {nombre}'}
            )
            
            if created:
                carreras_creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Creada carrera: {nombre}')
                )
            else:
                carreras_actualizadas += 1
                self.stdout.write(
                    self.style.WARNING(f'Carrera ya existe: {nombre}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado: {carreras_creadas} carreras creadas, '
                f'{carreras_actualizadas} carreras ya existían'
            )
        )
