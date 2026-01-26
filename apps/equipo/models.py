from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.lugar.models import Lugar
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


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
    fecha_eliminacion = models.DateTimeField(null=True, blank=True, db_column='fecha_eliminacion')
    eliminado_por = models.CharField(max_length=50, blank=True, null=True, db_column='eliminado_por')

    def soft_delete(self, usuario=None):
        self.fecha_eliminacion = timezone.now()
        self.eliminado_por = usuario
        self.save(update_fields=['fecha_eliminacion', 'eliminado_por'])

    class Meta:
        abstract = True


# =====================================================
# MODELO: MARCA
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

class Equipo(AuditoriaFechas, AuditoriaUsuarios, SoftDeleteModel):
    ESTADOS = [
        ("ACTIVO", "Activo"),
        ("MANTENIMIENTO", "Mantenimiento"),
        ("INACTIVO", "Inactivo"),
    ]

    id_equipo = models.AutoField(primary_key=True, db_column='id_equipo')  # PK autoincremental
    tipo = models.CharField(max_length=50, db_column='tipo')
    aec = models.CharField(max_length=50, db_column='aec')

    marca = models.CharField(max_length=50, blank=True, null=True, db_column='marca')
    modelo = models.CharField(max_length=50, blank=True, null=True, db_column='modelo')
    sistema_operativo = models.CharField(max_length=50, blank=True, null=True, db_column='sistema_operativo')
    procesador = models.CharField(max_length=50, blank=True, null=True, db_column='procesador')
    ESTADOS = [
        ("ACTIVO", "Activo"),
        ("MANTENIMIENTO", "Mantenimiento"),
        ("INACTIVO", "Inactivo"),
    ]
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
        related_name='equipos'
    )

    id_users = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_users',
        related_name='equipos'
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


# =====================================================
# MODELO: DISCO
# =====================================================

class Disco(models.Model):
    id_disco = models.AutoField(primary_key=True, db_column='id_disco')  # PK autoincremental
    equipo = models.ForeignKey(
        Equipo, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discos'
    )
    tipo = models.CharField(max_length=50)
    capacidad = models.CharField(max_length=50)
    rpm = models.IntegerField(blank=True, null=True)  # solo para HDD
    estado = models.CharField(max_length=50, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Disco'
        ordering = ['-id_disco']

    def __str__(self):
        return f"{self.tipo} {self.capacidad}"


# =====================================================
# MODELO: RAM
# =====================================================

class Ram(models.Model):
    id_ram = models.AutoField(primary_key=True, db_column='id_ram')  # PK autoincremental
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rams'
    )
    tipo = models.CharField(max_length=50)
    capacidad = models.CharField(max_length=50)
    frecuencia = models.IntegerField(blank=True, null=True)  # MHz
    voltaje = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)  # Voltios
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Ram'
        ordering = ['-id_ram']

    def __str__(self):
        return f"{self.tipo} {self.capacidad}"


# =====================================================
# MODELO: COMPONENTE
# =====================================================

class Componente(AuditoriaFechas, AuditoriaUsuarios, SoftDeleteModel):
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    id_componente = models.AutoField(primary_key=True, db_column='id_componente')
    tipo = models.CharField(max_length=50, db_column='tipo')
    aec = models.CharField(max_length=50, db_column='aec')

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
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ACTIVO', db_column='estado')
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

# =====================================================
# MODELO: GARANTIA
# =====================================================

def path_garantia_documentos(instance, filename):
    # Organiza los archivos por el ID del equipo o componente
    return f'garantias/{instance.id_garantia}/{filename}'




from django.db import models
from django.utils import timezone

class Garantia(AuditoriaFechas, AuditoriaUsuarios, SoftDeleteModel):
    id_garantia = models.AutoField(primary_key=True)
    
    # --- Relaciones ---
    equipo = models.OneToOneField(
        'Equipo', 
        on_delete=models.CASCADE, 
        null=True, blank=True, 
        related_name='garantia_info'
    )
    componente = models.OneToOneField(
        'Componente', 
        on_delete=models.CASCADE, 
        null=True, blank=True, 
        related_name='garantia_info'
    )

    # --- Datos de Identificación y Tiempos ---
    proveedor = models.CharField(max_length=150)
    contacto_soporte = models.TextField(
        blank=True, 
        null=True, 
        help_text="Teléfonos, correos o links"
    )
    
    fecha_compra = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Fecha de compra"
    )
    fecha_inicio = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Fecha de inicio de garantía"
    )
    duracion_meses = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        default=12,
        verbose_name="Duración en meses"
    )
    fecha_fin = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Fecha de fin de garantía"
    )

    # --- Archivos y Multimedia ---
    documento_pdf = models.FileField(
        upload_to='documentos/garantias/', 
        null=True, blank=True, 
        db_column='documento_pdf',
        help_text="Cargar el certificado de garantía en PDF"
    )
    foto_activo = models.ImageField(
        upload_to='fotos/activos/', 
        null=True, blank=True,
        help_text="Foto del equipo o componente físico"
    )

    class Meta:
        db_table = 'Garantia'
        verbose_name = 'Garantía'
        verbose_name_plural = 'Garantías'

    def __str__(self):
        # Manejo de errores por si no hay equipo ni componente asignado aún
        vinculo = "Sin asignar"
        if self.equipo:
            vinculo = str(self.equipo)
        elif self.componente:
            vinculo = str(self.componente)
            
        return f"Garantía {vinculo} - {self.proveedor}"

    @property
    def esta_vigente(self):
        if self.fecha_fin:
            return self.fecha_fin >= timezone.now().date()
        return False

