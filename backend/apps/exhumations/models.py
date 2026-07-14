from django.db import models
from django.utils import timezone
from auditlog.registry import auditlog

class Exhumation(models.Model):
    STATUT_CHOICES = [
        ("EN_ATTENTE",  "En attente de validation"),
        ("VALIDEE",     "Validée"),
        ("REFUSEE",     "Refusée"),
        ("EFFECTUEE",   "Effectuée"),
        ("ANNULEE",     "Annulée"),
    ]

    MOTIF_CHOICES = [
        ("TRANSFERT",    "Transfert vers un autre cimetière"),
        ("RENOVATION",   "Rénovation du caveau"),
        ("FAMILIAL",     "Regroupement familial"),
        ("JUDICIAIRE",   "Ordonnance judiciaire"),
        ("AUTRE",        "Autre motif"),
    ]

    # Référence unique
    numero = models.CharField(max_length=20, unique=True, db_index=True)

    # Relations
    caveau = models.ForeignKey(
        "caveaux.Caveau",
        on_delete=models.PROTECT,
        related_name="exhumations"
    )
    concession = models.ForeignKey(
        "concessions.Concession",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="exhumations"
    )
    defunt = models.ForeignKey(
        "reservations.Defunt",
        on_delete=models.PROTECT,
        related_name="exhumations"
    )
    demandeur = models.ForeignKey(
        "auth_app.Utilisateur",
        on_delete=models.PROTECT,
        related_name="exhumations_demandees"
    )
    agent_validation = models.ForeignKey(
        "auth_app.Utilisateur",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="exhumations_validees"
    )

    # Informations
    motif = models.CharField(max_length=20, choices=MOTIF_CHOICES)
    motif_detail = models.TextField(blank=True)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default="EN_ATTENTE", db_index=True)

    # Dates
    date_demande = models.DateTimeField(default=timezone.now)
    date_validation = models.DateTimeField(null=True, blank=True)
    date_exhumation_prevue = models.DateField(null=True, blank=True)
    date_exhumation_reelle = models.DateField(null=True, blank=True)

    # Documents
    autorisation_pdf = models.FileField(upload_to="exhumations/autorisations/", null=True, blank=True)
    pv_pdf = models.FileField(upload_to="exhumations/pv/", null=True, blank=True)

    # Notes
    motif_refus = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Exhumation"
        verbose_name_plural = "Exhumations"
        ordering = ["-date_demande"]

    def __str__(self):
        return f"{self.numero} — {self.defunt} — {self.get_statut_display()}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self._generer_numero()
        super().save(*args, **kwargs)

    def _generer_numero(self):
        from django.db.models import Max
        annee = timezone.now().year
        max_id = Exhumation.objects.filter(
            date_creation__year=annee
        ).aggregate(Max("id"))["id__max"] or 0
        return f"EXH-{annee}-{str(max_id + 1).zfill(5)}"

    def valider(self, agent):
        self.statut = "VALIDEE"
        self.agent_validation = agent
        self.date_validation = timezone.now()
        self.save()

    def refuser(self, agent, motif=""):
        self.statut = "REFUSEE"
        self.agent_validation = agent
        self.motif_refus = motif

        self.save()

# Audit trail
auditlog.register(Exhumation)        