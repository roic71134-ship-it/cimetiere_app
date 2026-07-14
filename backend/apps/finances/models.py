"""Modèles financiers : factures et paiements."""
from django.db import models
from apps.users.models import Utilisateur
from apps.reservations.models import Reservation


class Facture(models.Model):
    """Facture générée automatiquement après validation."""

    EN_ATTENTE = 'en_attente'
    PARTIELLEMENT_PAYEE = 'partiellement_payee'
    PAYEE = 'payee'
    ANNULEE = 'annulee'

    STATUTS = [
        (EN_ATTENTE, 'En attente de paiement'),
        (PARTIELLEMENT_PAYEE, 'Partiellement payée'),
        (PAYEE, 'Payée'),
        (ANNULEE, 'Annulée'),
    ]

    reservation = models.OneToOneField(
        Reservation, on_delete=models.PROTECT, related_name='facture'
    )
    numero = models.CharField(max_length=20, unique=True, verbose_name="Numéro de facture")
    montant_total = models.DecimalField(max_digits=12, decimal_places=2)
    montant_paye = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    statut = models.CharField(max_length=30, choices=STATUTS, default=EN_ATTENTE)
    date_emission = models.DateTimeField(auto_now_add=True)
    date_echeance = models.DateField(null=True, blank=True)
    fichier_pdf = models.FileField(upload_to='factures/', blank=True, null=True)

    class Meta:
        verbose_name = "Facture"

    def __str__(self):
        return f"Facture {self.numero} — {self.statut}"

    @property
    def montant_restant(self):
        return self.montant_total - self.montant_paye

    def mettre_a_jour_statut(self):
        if self.montant_paye >= self.montant_total:
            self.statut = self.PAYEE
        elif self.montant_paye > 0:
            self.statut = self.PARTIELLEMENT_PAYEE
        else:
            self.statut = self.EN_ATTENTE
        self.save()


class Paiement(models.Model):
    """Enregistrement d'un paiement."""

    MOBILE_MONEY = 'mobile_money'
    AIRTEL_MONEY = 'airtel_money'
    ESPECES = 'especes'
    VIREMENT = 'virement'

    CANAUX = [
        (MOBILE_MONEY, 'Mobile Money'),
        (AIRTEL_MONEY, 'Airtel Money'),
        (ESPECES, 'Espèces'),
        (VIREMENT, 'Virement bancaire'),
    ]

    facture = models.ForeignKey(Facture, on_delete=models.PROTECT, related_name='paiements')
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    canal = models.CharField(max_length=20, choices=CANAUX)
    reference_transaction = models.CharField(max_length=100, blank=True)
    date_paiement = models.DateTimeField(auto_now_add=True)
    enregistre_par = models.ForeignKey(
        Utilisateur, on_delete=models.PROTECT, null=True, blank=True
    )
    observations = models.TextField(blank=True)

    class Meta:
        verbose_name = "Paiement"
        ordering = ['-date_paiement']

    def __str__(self):
        return f"Paiement {self.montant} FCFA via {self.get_canal_display()}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculer le montant payé sur la facture
        total_paye = sum(
            p.montant for p in self.facture.paiements.all()
        )
        self.facture.montant_paye = total_paye
        self.facture.mettre_a_jour_statut()
