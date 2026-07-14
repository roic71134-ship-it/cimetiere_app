from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from auditlog.registry import auditlog


class Role(models.Model):
    NOM_CHOICES = [
        ("ADMIN", "Administrateur"),
        ("AGENT", "Agent de terrain"),
        ("SECRETARIAT", "Secrétariat"),
        ("CLIENT", "Client"),
    ]
    nom = models.CharField(max_length=20, choices=NOM_CHOICES, unique=True)
    peut_valider_reservations = models.BooleanField(default=False)
    peut_modifier_carte = models.BooleanField(default=False)
    peut_voir_finances = models.BooleanField(default=False)
    peut_gerer_concessions = models.BooleanField(default=False)
    peut_gerer_exhumations = models.BooleanField(default=False)
    peut_enregistrer_paiements = models.BooleanField(default=False)
    peut_exporter_donnees = models.BooleanField(default=False)
    peut_voir_audit = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"

    def __str__(self):
        return self.get_nom_display()


class UtilisateurManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire.")
        email = self.normalize_email(email)
        extra_fields.setdefault("est_actif", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="utilisateurs"
    )
    est_actif = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    mfa_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    derniere_connexion_app = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom", "prenom"]

    objects = UtilisateurManager()

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def est_admin(self):
        return self.role and self.role.nom == "ADMIN"

    def a_permission(self, permission):
        if not self.role:
            return False
        return getattr(self.role, permission, False)


class SessionMFA(models.Model):
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name="sessions_mfa"
    )
    code = models.CharField(max_length=10)
    expire_a = models.DateTimeField()
    est_utilise = models.BooleanField(default=False)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Session MFA"

    def __str__(self):
        return f"MFA {self.utilisateur.email}"

    @property
    def est_valide(self):
        from django.utils import timezone
        return not self.est_utilise and timezone.now() < self.expire_a

    @classmethod
    def creer_pour(cls, utilisateur, adresse_ip=None):
        import secrets
        import string
        from django.utils import timezone
        from datetime import timedelta
        from django.conf import settings

        cls.objects.filter(
            utilisateur=utilisateur,
            est_utilise=False
        ).update(est_utilise=True)

        longueur = getattr(settings, "MFA_CODE_LENGTH", 6)
        code = "".join(secrets.choice(string.digits) for _ in range(longueur))
        expiry = getattr(settings, "MFA_CODE_EXPIRY_MINUTES", 10)

        return cls.objects.create(
            utilisateur=utilisateur,
            code=code,
            expire_a=timezone.now() + timedelta(minutes=expiry),
            adresse_ip=adresse_ip,
        )
# Audit trail
auditlog.register(Utilisateur)
auditlog.register(Role)