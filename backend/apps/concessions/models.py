from django.db import models
from django.utils import timezone
from datetime import date, timedelta
from auditlog.registry import auditlog

DUREES_CONCESSION = {
    "TEMPORAIRE":  5,
    "TRENTENAIRE": 30,
    "PERPETUELLE": None,
    "FAMILIALE":   None,
}


class Concession(models.Model):
    TYPE_CHOICES = [
        ("TEMPORAIRE",  "Temporaire (5 ans)"),
        ("TRENTENAIRE", "Trentenaire (30 ans)"),
        ("PERPETUELLE", "Perpétuelle"),
        ("FAMILIALE",   "Familiale perpétuelle"),
    ]

    STATUT_CHOICES = [
        ("ACTIVE",            "Active"),
        ("EN_RENOUVELLEMENT", "En cours de renouvellement"),
        ("EXPIREE",           "Expirée"),
        ("RESILIEE",          "Résiliée"),
    ]

    numero_contrat = models.CharField(max_length=30, unique=True, db_index=True)
    caveau = models.ForeignKey(
        "caveaux.Caveau",
        on_delete=models.PROTECT,
        related_name="concessions"
    )
    titulaire = models.ForeignKey(
        "auth_app.Utilisateur",
        on_delete=models.PROTECT,
        related_name="concessions"
    )
    reservation_origine = models.OneToOneField(
        "reservations.Reservation",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="concession"
    )
    type_concession = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    date_alerte_renouvellement = models.DateField(null=True, blank=True)
    nombre_renouvellements = models.PositiveIntegerField(default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="ACTIVE", db_index=True)
    montant_initial_xaf = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    montant_renouvellement_xaf = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    contrat_pdf = models.FileField(upload_to="concessions/", null=True, blank=True)
    date_resiliation = models.DateField(null=True, blank=True)
    motif_resiliation = models.TextField(blank=True)
    resilie_par = models.ForeignKey(
        "auth_app.Utilisateur",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="concessions_resiliees"
    )
    beneficiaires_json = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Concession"
        verbose_name_plural = "Concessions"
        ordering = ["-date_debut"]

    def __str__(self):
        return f"{self.numero_contrat} — {self.titulaire} — {self.caveau.reference}"

    def save(self, *args, **kwargs):
        if not self.numero_contrat:
            self.numero_contrat = self._generer_numero()
        if self.date_fin and not self.date_alerte_renouvellement:
            self.date_alerte_renouvellement = self.date_fin - timedelta(days=30)
        super().save(*args, **kwargs)

    def _generer_numero(self):
        from django.db.models import Max
        annee = timezone.now().year
        max_id = Concession.objects.filter(
            date_creation__year=annee
        ).aggregate(Max("id"))["id__max"] or 0
        return f"CONC-{annee}-{str(max_id + 1).zfill(5)}"

    @property
    def est_perpetuelle(self):
        return self.type_concession in ["PERPETUELLE", "FAMILIALE"]

    @property
    def jours_restants(self):
        if not self.date_fin:
            return None
        delta = self.date_fin - date.today()
        return delta.days

    @property
    def est_expiree(self):
        if not self.date_fin:
            return False
        return date.today() > self.date_fin

    @property
    def alerte_expiration(self):
        if not self.date_fin:
            return False
        return date.today() >= (self.date_fin - timedelta(days=30))

    @classmethod
    def creer_depuis_reservation(cls, reservation):
        type_c = reservation.type_concession
        duree = DUREES_CONCESSION.get(type_c)
        debut = date.today()
        fin = None
        if duree:
            fin = debut.replace(year=debut.year + duree)
        return cls.objects.create(
            caveau=reservation.caveau,
            titulaire=reservation.client,
            reservation_origine=reservation,
            type_concession=type_c,
            date_debut=debut,
            date_fin=fin,
            montant_initial_xaf=reservation.montant_total_xaf,
        )

    def resilier(self, agent, motif=""):
        from apps.caveaux.models import StatutCaveau
        self.statut = "RESILIEE"
        self.date_resiliation = date.today()
        self.motif_resiliation = motif
        self.resilie_par = agent
        self.save()
        self.caveau.changer_statut(StatutCaveau.DISPONIBLE, utilisateur=agent)


class RenouvellementConcession(models.Model):
    concession = models.ForeignKey(Concession, on_delete=models.CASCADE, related_name="renouvellements")
    date_ancienne_fin = models.DateField()
    date_nouvelle_fin = models.DateField()
    montant_xaf = models.DecimalField(max_digits=12, decimal_places=0)
    traite_par = models.ForeignKey("auth_app.Utilisateur", on_delete=models.PROTECT)
    date_traitement = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Renouvellement"
        ordering = ["-date_traitement"]

    def __str__(self):
        return f"Renouvellement {self.concession.numero_contrat}"

# Audit trail
auditlog.register(Concession)    