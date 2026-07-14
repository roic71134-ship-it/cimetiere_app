from celery import shared_task


@shared_task
def alertes_seuil_places():
    from apps.caveaux.models import Caveau
    from apps.auth_app.models import Utilisateur
    from apps.notifications.services import envoyer_email

    total = Caveau.objects.count()
    disponibles = Caveau.objects.filter(statut="DISPONIBLE").count()

    if total == 0:
        return "Aucun caveau."

    pct = (disponibles / total) * 100

    if pct < 20:
        niveau = "CRITIQUE" if pct < 10 else "ATTENTION"
        emoji = "🚨" if pct < 10 else "⚠️"

        # Envoyer à tous les admins
        admins = Utilisateur.objects.filter(
            role__nom="ADMIN",
            est_actif=True,
        )

        for admin in admins:
            try:
                envoyer_email(
                    destinataire=admin.email,
                    sujet=f"{emoji} {niveau} — Seuil de places disponibles",
                    message=f"""Bonjour {admin.prenom} {admin.nom},

{emoji} ALERTE {niveau} :
Seulement {disponibles} place(s) disponible(s) sur {total} ({round(pct, 1)}%) au Cimetière Municipal de Pointe-Noire.

Veuillez prendre les mesures nécessaires.

Cordialement,
Système de gestion — Cimetière Municipal de Pointe-Noire""",
                )
            except Exception:
                pass

        return f"Alerte {niveau} envoyée — {disponibles}/{total} places ({round(pct, 1)}%)"

    return f"Aucune alerte — {disponibles}/{total} places disponibles ({round(pct, 1)}%)"