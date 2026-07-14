from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta


@shared_task
def envoyer_alertes_concessions():
    from apps.concessions.models import Concession
    from apps.notifications.services import envoyer_email

    aujourd_hui = date.today()
    dans_30_jours = aujourd_hui + timedelta(days=30)

    # Concessions qui expirent dans 30 jours
    concessions = Concession.objects.filter(
        statut="ACTIVE",
        date_fin__isnull=False,
        date_fin__lte=dans_30_jours,
        date_fin__gte=aujourd_hui,
    ).select_related("titulaire", "caveau")

    nb = 0
    for c in concessions:
        jours = (c.date_fin - aujourd_hui).days
        try:
            envoyer_email(
                destinataire=c.titulaire.email,
                sujet=f"⚠️ Votre concession expire dans {jours} jours",
                message=f"""Bonjour {c.titulaire.prenom} {c.titulaire.nom},

Votre concession {c.numero_contrat} pour le caveau {c.caveau.reference} expire le {c.date_fin.strftime('%d/%m/%Y')} (dans {jours} jours).

Veuillez contacter le cimetière pour procéder au renouvellement.

Cordialement,
Cimetière Municipal de Pointe-Noire""",
            )
            nb += 1
        except Exception:
            pass

    # Marquer les concessions expirées
    Concession.objects.filter(
        statut="ACTIVE",
        date_fin__lt=aujourd_hui,
    ).update(statut="EXPIREE")

    return f"{nb} alertes concessions envoyées."