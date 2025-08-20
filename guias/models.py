from django.db import models
from django.contrib.auth.models import User
from core.models import Carrera, Asignatura


class GuiaGenerada(models.Model):
    """Modelo para almacenar las guías generadas"""
    
    SEMESTRES = [
        ('1', 'Primer Semestre'),
        ('2', 'Segundo Semestre'),
        ('3', 'Tercer Semestre'),
        ('4', 'Cuarto Semestre'),
        ('5', 'Quinto Semestre'),
        ('6', 'Sexto Semestre'),
        ('7', 'Séptimo Semestre'),
        ('8', 'Octavo Semestre'),
        ('9', 'Noveno Semestre'),
        ('10', 'Décimo Semestre'),
    ]
    
    # Datos del formulario
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    semestre = models.CharField(max_length=2, choices=SEMESTRES)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    contenido_analitico = models.TextField()
    unidad_didactica = models.CharField(max_length=200)
    titulo = models.CharField(max_length=200)
    
    # Información del usuario
    usuario_creador = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Archivos generados
    archivo_word = models.FileField(upload_to='guias/word/', blank=True)
    archivo_pdf = models.FileField(upload_to='guias/pdf/', blank=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Guía Generada"
        verbose_name_plural = "Guías Generadas"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Guía: {self.titulo} - {self.asignatura.nombre}"
