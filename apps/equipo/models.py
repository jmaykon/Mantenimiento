from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.lugar.models import Lugar

# =====================================================
# MODELOS ABSTRACTOS DE AUDITORÍA
# =====================================================

class AuditoriaFechas(models.Model):
    """
    Manejo de fechas de auditoría
    """
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
    fecha_modificacion = models.DateTimeField(auto_now=True, db_column='fecha_modificacion')
    fecha_eliminacion = models.DateTimeField(null=True, blank=True, db_column='fecha_eliminacion')

    class Meta:
        abstract = True


class AuditoriaUsuarios(models.Model):
    """
    Manejo de usuarios de auditoría
    """
    creado_por = models.CharField(max_length=50, blank=True, null=True, db_column='creado_por')
    modificado_por = models.CharField(max_length=50, blank=True, null=True, db_column='modificado_por')
    eliminado_por = models.CharField(max_length=50, blank=True, null=True, db_column='eliminado_por')

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Borrado lógico reutilizable
    """
    def soft_delete(self, usuario=None):
        self.fecha_eliminacion = timezone.now()
        self.eliminado_por = usuario
        self.save(update_fields=['fecha_eliminacion', 'eliminado_por'])

    class Meta:
        abstract = True


# =====================================================
# MODELO: MARCA (NUEVO - NO ROMPE NADA)
# =====================================================

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'Marca'
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.nombre


# =====================================================
# MODELO: EQUIPO
# =====================================================

class Equipo(
    AuditoriaFechas,
    AuditoriaUsuarios,
    SoftDeleteModel
):
    ESTADOS = [
        ("ACTIVO", "Activo"),
        ("MANTENIMIENTO", "Mantenimiento"),
        ("INACTIVO", "Inactivo"),
    ]

    id_equipo = models.AutoField(primary_key=True, db_column='id_equipo')
    tipo = models.CharField(max_length=50, db_column='tipo')
    aec = models.CharField(max_length=50, db_column='aec')

    # Se mantiene el campo original y se agrega FK opcional
    marca = models.CharField(max_length=50, blank=True, null=True, db_column='marca')
    modelo = models.CharField(max_length=50, blank=True, null=True, db_column='modelo')
    sistema_operativo = models.CharField(max_length=50, blank=True, null=True, db_column='sistema_operativo')
    procesador = models.CharField(max_length=50, blank=True, null=True, db_column='procesador')
    tipo_ram = models.CharField(max_length=50, blank=True, null=True, db_column='tipo_ram')
    ram = models.CharField(max_length=50, blank=True, null=True, db_column='ram')
    tipo_disco = models.CharField(max_length=50, blank=True, null=True, db_column='tipo_disco')
    disco = models.CharField(max_length=50, blank=True, null=True, db_column='disco')
    estado_disco = models.CharField(max_length=300, blank=True, null=True, db_column='estado_disco')

    estado_equipo = models.CharField(
        max_length=50,
        choices=ESTADOS,
        default="ACTIVO",
        db_column='estado_equipo'
    )

    serial = models.CharField(max_length=50, unique=True, db_column='serial')

    observaciones = models.CharField(max_length=300, blank=True, null=True, db_column='observaciones')

    ip = models.GenericIPAddressField(blank=True, null=True, db_column='ip')

    id_lugar = models.ForeignKey(
        Lugar,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_lugar',
        related_name='lugar'
    )

    id_users = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_users',
        related_name='usuarios'
    )

    class Meta:
        db_table = 'Equipo'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['serial']),
            models.Index(fields=['estado_equipo']),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.serial}"

class Disco(models.Model):
    equipo = models.ForeignKey(
        'Equipo', 
        on_delete=models.SET_NULL,  # no borra el disco si se borra el equipo
        null=True,                   # permite que el campo quede vacío
        blank=True,
        related_name='discos'
    )
    tipo = models.CharField(max_length=50)
    capacidad = models.CharField(max_length=50)
    rpm = models.IntegerField(blank=True, null=True)  # para discos HDD
    estado = models.CharField(max_length=50, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Disco'
        ordering = ['-id_disco']

    def __str__(self):
        return f"{self.tipo} {self.capacidad} ({self.serial})"


class Ram(models.Model):
    equipo = models.ForeignKey(
        'Equipo',
        on_delete=models.SET_NULL,  # no borra la RAM si se borra el equipo
        null=True,
        blank=True,
        related_name='rams'
    )
    tipo = models.CharField(max_length=50)
    frecuencia = models.IntegerField(blank=True, null=True)  # MHz, ej: 3200
    voltaje = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)  # Voltios, ej: 1.2
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    capacidad = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True, null=True)


    class Meta:
        db_table = 'Ram'
        ordering = ['-id_ram']

    def __str__(self):
        return f"{self.tipo} {self.capacidad} ({self.serial})"
# =====================================================
# MODELO: COMPONENTE
# =====================================================

class Componente(
    AuditoriaFechas,
    AuditoriaUsuarios,
    SoftDeleteModel
):
    ESTADO = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    id_componente = models.AutoField(primary_key=True, db_column='id_componente')

    tipo = models.CharField(max_length=50, db_column='tipo')
    aec = models.CharField(max_length=50, db_column='aec')

    # Se mantiene y se mejora
    marca = models.CharField(max_length=50, blank=True, null=True, db_column='marca')
    marca_ref = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='componentes'
    )

    modelo = models.CharField(max_length=50, blank=True, null=True, db_column='modelo')

    serial = models.CharField(max_length=50, unique=True, db_column='serial')

    estado = models.CharField(
        max_length=20,
        choices=ESTADO,
        default='ACTIVO',
        db_column='estado'
    )

    observaciones = models.CharField(max_length=300, blank=True, null=True, db_column='observaciones')

    id_equipo = models.ForeignKey(
        Equipo,
        on_delete=models.CASCADE,
        db_column='id_equipo',
        related_name='componentes'
    )

    id_users = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_users'
    )

    id_lugar = models.ForeignKey(
        Lugar,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_lugar'
    )

    class Meta:
        db_table = 'Componente'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.tipo} - {self.serial}"
