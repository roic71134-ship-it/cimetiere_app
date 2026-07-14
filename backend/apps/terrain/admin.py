from django.contrib import admin
from .models import Cimetiere, Zone, Bloc


@admin.register(Cimetiere)
class CimetiereAdmin(admin.ModelAdmin):
    list_display = ("nom", "ville", "pays", "est_actif", "date_creation")
    list_filter = ("est_actif",)
    search_fields = ("nom", "ville")


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "cimetiere", "type_zone", "est_active")
    list_filter = ("type_zone", "est_active", "cimetiere")
    search_fields = ("nom", "code")


@admin.register(Bloc)
class BlocAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "zone", "capacite_theorique", "est_actif")
    list_filter = ("est_actif", "zone")
    search_fields = ("nom", "code")