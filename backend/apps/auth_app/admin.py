from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Role, Utilisateur


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "nom",
        "peut_valider_reservations",
        "peut_modifier_carte",
        "peut_voir_finances",
        "peut_gerer_concessions",
        "peut_gerer_exhumations",
        "peut_enregistrer_paiements",
        "peut_exporter_donnees",
        "peut_voir_audit",
    )
    list_editable = (
        "peut_valider_reservations",
        "peut_modifier_carte",
        "peut_voir_finances",
        "peut_gerer_concessions",
        "peut_gerer_exhumations",
        "peut_enregistrer_paiements",
        "peut_exporter_donnees",
        "peut_voir_audit",
    )


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    model = Utilisateur
    list_display = ("email", "prenom", "nom", "role", "est_actif", "is_staff")
    list_filter = ("role", "est_actif", "is_staff")
    search_fields = ("email", "prenom", "nom")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informations personnelles", {"fields": ("prenom", "nom", "telephone", "adresse")}),
        ("Rôle et statut", {"fields": ("role", "est_actif", "mfa_active", "is_staff", "is_superuser")}),
        ("Dates", {"fields": ("derniere_connexion_app",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "prenom", "nom", "role", "password1", "password2"),
        }),
    )
    filter_horizontal = ()