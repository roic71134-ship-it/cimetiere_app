"""Administration Django - Utilisateurs."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('email', 'nom', 'prenom', 'role', 'is_active', 'date_creation')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'nom', 'prenom')
    ordering = ('-date_creation',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('nom', 'prenom', 'telephone')}),
        ('Rôle et permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('MFA', {'fields': ('mfa_code', 'mfa_code_expiry', 'mfa_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nom', 'prenom', 'role', 'password1', 'password2'),
        }),
    )
