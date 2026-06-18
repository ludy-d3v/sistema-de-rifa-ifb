from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _criar_usuario(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail e obrigatorio.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._criar_usuario(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('papel', Usuario.Papel.ORGANIZADOR)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuario precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuario precisa ter is_superuser=True.')

        return self._criar_usuario(email, password, **extra_fields)


class Usuario(AbstractUser):
    class Papel(models.TextChoices):
        ORGANIZADOR = 'organizador', 'Organizador'
        VENDEDOR = 'vendedor', 'Vendedor'

    username = None
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    cpf = models.CharField(max_length=14, blank=True)
    papel = models.CharField(
        max_length=20,
        choices=Papel.choices,
        default=Papel.ORGANIZADOR,
    )
    ultimo_acesso = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def registrar_acesso(self):
        self.ultimo_acesso = timezone.now()
        self.save(update_fields=['ultimo_acesso'])

    def __str__(self):
        return f'{self.nome} ({self.email})'
