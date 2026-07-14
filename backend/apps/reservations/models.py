from django.db import models
from django.utils import timezone
from auditlog.registry import auditlog


class Defunt(models.Model):
    SEXE_CHOICES = [("M", "Masculin"), ("F", "Féminin"), ("A", "Autre")]

    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    date_naissance = models.DateField(null=True, blank=True)
    date_deces = models.DateField(verbose_name="Date de décès")
    lieu_naissance = models.CharField(max_length=200, blank=True)
    lieu_deces = models.CharField(max_length=200, blank=True)
    nationalite = models.CharField(max_length=100, default="Congolaise")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, default="M")
    numero_acte_deces = models.CharField(max_length=100, blank=True)
    numero_permis_inhumer = models.CharField(max_length=100, blank=True)
    nom_famille_responsable = models.CharField(max_length=200, blank=True)
    telephone_famille = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Défunt"
        verbose_name_plural = "Défunts"
        ordering = ["-date_deces"]

    def __str__(self):
        return f"{self.prenom} {self.nom} (†{self.date_deces})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class Reservation(models.Model):
    STATUT_CHOICES = [
        ("EN_ATTENTE", "En attente de validation"),
        ("VALIDEE", "Validée"),
        ("REFUSEE", "Refusée"),
        ("ANNULEE", "Annulée"),
        ("EXPIREE", "Expirée"),
    ]

    TYPE_CONCESSION_CHOICES = [
        ("TEMPORAIRE", "Temporaire (5 ans)"),
        ("TRENTENAIRE", "Trentenaire (30 ans)"),
        ("PERPETUELLE", "Perpétuelle"),
        ("FAMILIALE", "Familiale"),
    ]

    numero = models.CharField(max_length=20, unique=True, db_index=True)
    client = models.ForeignKey(
        "auth_app.Utilisateur",
        on_delete=models.PROTECT,
        related_name="reservations_client"
    )
    agent_validation = models.ForeignKey(
        "auth_app.Utilisateur",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="reservations_validees"
    )
    caveau = models.ForeignKey(
        "caveaux.Caveau",
        on_delete=models.PROTECT,
        related_name="reservations"
    )
    defunt = models.OneToOneField(
        Defunt,
        on_delete=models.PROTECT,
        related_name="reservation"
    )
    type_concession = models.CharField(max_length=20, choices=TYPE_CONCESSION_CHOICES)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default="EN_ATTENTE", db_index=True)
    montant_total_xaf = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    date_soumission = models.DateTimeField(default=timezone.now)
    date_validation = models.DateTimeField(null=True, blank=True)
    date_refus = models.DateTimeField(null=True, blank=True)
    notes_client = models.TextField(blank=True)
    motif_refus = models.TextField(blank=True)
    notes_admin = models.TextField(blank=True)
    facture_pdf = models.FileField(upload_to="factures/", null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ["-date_soumission"]

    def __str__(self):
        return f"{self.numero} — {self.defunt} — {self.get_statut_display()}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self._generer_numero()
        super().save(*args, **kwargs)

    def _generer_numero(self):
        from django.db.models import Max
        annee = timezone.now().year
        max_id = Reservation.objects.filter(
            date_soumission__year=annee
        ).aggregate(Max("id"))["id__max"] or 0
        return f"RES-{annee}-{str(max_id + 1).zfill(5)}"

    @property
    def montant_paye_xaf(self):
        return int(
            self.paiements.filter(statut="CONFIRME").aggregate(
                total=models.Sum("montant_xaf")
            )["total"] or 0
        )

    @property
    def montant_restant_xaf(self):
        return max(0, int(self.montant_total_xaf) - self.montant_paye_xaf)

    def valider(self, agent):
        from apps.caveaux.models import StatutCaveau
        self.statut = "VALIDEE"
        self.agent_validation = agent
        self.date_validation = timezone.now()
        self.save()
        self.caveau.changer_statut(StatutCaveau.OCCUPE, utilisateur=agent)

    def refuser(self, agent, motif=""):
        from apps.caveaux.models import StatutCaveau
        self.statut = "REFUSEE"
        self.agent_validation = agent
        self.motif_refus = motif
        self.date_refus = timezone.now()
        self.save()
        self.caveau.changer_statut(StatutCaveau.DISPONIBLE, utilisateur=agent)
        
# Audit trail
auditlog.register(Defunt)
auditlog.register(Reservation)        