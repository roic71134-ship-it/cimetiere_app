from django.contrib import admin
from .models import Facture, Paiement

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('numero', 'reservation', 'montant_total', 'montant_paye', 'statut', 'date_emission')
    list_filter = ('statut',)
    search_fields = ('numero', 'reservation__client__email')

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('facture', 'montant', 'canal', 'date_paiement', 'enregistre_par')
    list_filter = ('canal',)
