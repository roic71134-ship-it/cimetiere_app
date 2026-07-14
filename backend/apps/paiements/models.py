from django.db import models
from django.utils import timezone
from auditlog.registry import auditlog


class Paiement(models.Model):
    CANAL_CHOICES = [
        ("ESPECES", "Espèces"),
        ("AIRTEL_MONEY", "Airtel Money"),
        ("MTN_MOMO", "MTN Mobile Money"),
        ("VIREMENT", "Virement bancaire"),
        ("CHEQUE", "Chèque"),
    ]

    STATUT_CHOICES = [
        ("EN_ATTENTE", "En attente"),
        ("CONFIRME", "Confirmé"),
        ("ECHEC", "Échec"),
        ("REMBOURSE", "Remboursé"),
    ]

    reservation = models.ForeignKey(
        "reservations.Reservation",
        on_delete=models.PROTECT,
        related_name="paiements",
        null=True,
        blank=True,
    )
    client = models.ForeignKey(
        "auth_app.Utilisateur",
        on_delete=models.PROTECT,
        related_name="paiements",
    )
    enregistre_par = models.ForeignKey(
        "auth_app.Utilisateur",
        on_delete=models.PROTECT,
        related_name="paiements_enregistres",
        null=True,
        blank=True,
    )
    montant_xaf = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Montant (FCFA)"
    )
    canal = models.CharField(
        max_length=20,
        choices=CANAL_CHOICES,
        verbose_name="Canal de paiement"
    )
    statut = models.CharField(
        max_length=15,
        choices=STATUT_CHOICES,
        default="EN_ATTENTE",
        db_index=True
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Référence de transaction"
    )
    numero_transaction = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Numéro de transaction"
    )
    notes = models.TextField(blank=True)
    date_paiement = models.DateTimeField(default=timezone.now)
    date_confirmation = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ["-date_paiement"]

    def __str__(self):
        return f"Paiement {self.reference} — {self.montant_xaf} FCFA — {self.get_statut_display()}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generer_reference()
        super().save(*args, **kwargs)

    def _generer_reference(self):
        from django.db.models import Max
        annee = timezone.now().year
        max_id = Paiement.objects.filter(
            date_creation__year=annee
        ).aggregate(Max("id"))["id__max"] or 0
        return f"PAY-{annee}-{str(max_id + 1).zfill(5)}"

    def confirmer(self, agent=None):
        self.statut = "CONFIRME"
        self.date_confirmation = timezone.now()
        self.enregistre_par = agent
        self.save()

# Audit trail
auditlog.register(Paiement)        