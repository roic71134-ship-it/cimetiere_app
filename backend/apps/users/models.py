"""Modèles utilisateurs avec gestion des rôles (RBAC)."""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import pyotp


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Utilisateur.ADMIN)
        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    """Modèle utilisateur personnalisé avec rôles."""

    ADMIN = 'admin'
    AGENT = 'agent'
    SECRETARIAT = 'secretariat'
    CLIENT = 'client'

    ROLES = [
        (ADMIN, 'Administrateur'),
        (AGENT, 'Agent de terrain'),
        (SECRETARIAT, 'Secrétariat'),
        (CLIENT, 'Client / Citoyen'),
    ]

    email = models.EmailField(unique=True, verbose_name="Email")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    role = models.CharField(max_length=20, choices=ROLES, default=CLIENT, verbose_name="Rôle")

    # MFA
    mfa_secret = models.CharField(max_length=32, blank=True, verbose_name="Secret MFA")
    mfa_code = models.CharField(max_length=6, blank=True, verbose_name="Code MFA temporaire")
    mfa_code_expiry = models.DateTimeField(null=True, blank=True, verbose_name="Expiration code MFA")
    mfa_active = models.BooleanField(default=False, verbose_name="MFA activé")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    objects = UtilisateurManager()

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_role_display()})"

    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def generer_mfa_secret(self):
        self.mfa_secret = pyotp.random_base32()
        self.save()
        return self.mfa_secret

    # Permissions par rôle
    @property
    def peut_voir_finances(self):
        return self.role in [self.ADMIN, self.SECRETARIAT]

    @property
    def peut_modifier_carte(self):
        return self.role in [self.ADMIN, self.AGENT]

    @property
    def peut_valider_reservations(self):
        return self.role in [self.ADMIN, self.SECRETARIAT]
