from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from apps.lugar.models import Lugar  
from apps.equipo.models import Equipo


class UsersCustomUser(AbstractUser):
    role = models.CharField(
        max_length=20, 
        choices=[('admin','Admin'),('tecnico','Técnico'),('usuario','Usuario')],
        default='admin',
        db_column='role'
    )
    firma = models.ImageField(
    upload_to='firmas/',
    blank=True,
    null=True,
    db_column='firma'
)
    id_lugar = models.ForeignKey(Lugar, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_lugar')
    id_equipo = models.ForeignKey(
    Equipo,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='usuarios',
    db_column='id_equipo'
)
    codigo = models.CharField(max_length=50, blank=True, null=True, db_column='codigo')
    nombre = models.CharField(max_length=50, blank=True, null=True, db_column='nombre')
    apellido_p = models.CharField(max_length=50, blank=True, null=True, db_column='apellido_p')
    apellido_m = models.CharField(max_length=50, blank=True, null=True, db_column='apellido_m')
    telefono = models.CharField(max_length=20, blank=True, null=True, db_column='telefono')

    @property
    def usuario_sistema(self):
        if not self.apellido_p or not self.nombre:
            return "sin-usuario"

        inicial_m = self.apellido_m[0] if self.apellido_m else ""
        return f"{self.apellido_p}{inicial_m}{self.nombre[0]}".lower()

    class Meta:
        db_table = 'users_customuser' 

    def __str__(self):
        return self.username