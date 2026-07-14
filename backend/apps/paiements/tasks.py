from celery import shared_task


@shared_task
def alertes_retard_paiement():
    from apps.paiements.models import Paiement
    from apps.notifications.services import envoyer_email
    from django.utils import timezone
    from datetime import timedelta

    date_limite = timezone.now() - timedelta(days=7)

    paiements_retard = Paiement.objects.filter(
        statut="EN_ATTENTE",
        date_paiement__lt=date_limite,
    ).select_related("reservation__client")

    nb = 0
    for p in paiements_retard:
        try:
            client = p.reservation.client if p.reservation else None
            if not client:
                continue
            envoyer_email(
                destinataire=client.email,
                sujet="⚠️ Retard de paiement — Cimetière Municipal de Pointe-Noire",
                message=f"""Bonjour {client.prenom} {client.nom},

Nous vous informons que votre paiement de {int(p.montant_xaf):,} FCFA (réf. {p.reference}) est en attente depuis plus de 7 jours.

Veuillez régulariser votre situation au plus vite.

Cordialement,
Cimetière Municipal de Pointe-Noire""".replace(",", " "),
            )
            nb += 1
        except Exception:
            pass

    return f"{nb} alertes retard paiement envoyées."