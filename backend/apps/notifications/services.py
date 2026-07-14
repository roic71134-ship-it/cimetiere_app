import base64
import requests
from django.conf import settings


def _expediteur():
    return {
        "name": settings.APP_NAME,
        "email": "mylordbokemba6@gmail.com",
    }


def envoyer_email(destinataire: str, sujet: str, message: str) -> bool:
    """Envoie un email texte simple via l'API Brevo."""
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        }
        message_html = f"<pre style='font-family:inherit;white-space:pre-wrap;'>{message}</pre>"
        payload = {
            "sender": _expediteur(),
            "to": [{"email": destinataire}],
            "subject": sujet,
            "htmlContent": message_html,
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code != 201:
            print(f"Erreur envoi email (Brevo) : {response.status_code} - {response.text}")
            return False
        return True
    except Exception as e:
        print(f"Erreur envoi email : {e}")
        return False


def envoyer_email_avec_pdf(destinataire: str, sujet: str, message: str, pdf_bytes: bytes, nom_fichier: str) -> bool:
    """Envoie un email avec une pièce jointe PDF via l'API Brevo."""
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        }
        message_html = f"<pre style='font-family:inherit;white-space:pre-wrap;'>{message}</pre>"
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        payload = {
            "sender": _expediteur(),
            "to": [{"email": destinataire}],
            "subject": sujet,
            "htmlContent": message_html,
            "attachment": [
                {"content": pdf_base64, "name": nom_fichier}
            ],
        }
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code != 201:
            print(f"Erreur envoi email avec PDF (Brevo) : {response.status_code} - {response.text}")
            return False
        return True
    except Exception as e:
        print(f"Erreur envoi email avec PDF : {e}")
        return False


def generer_pdf_facture(reservation) -> bytes:
    """Génère le PDF de la facture et retourne les bytes."""
    try:
        from apps.reservations.api import _generer_html_facture
        from xhtml2pdf import pisa
        import io
        html = _generer_html_facture(reservation)
        buffer = io.BytesIO()
        pisa.CreatePDF(html.encode("utf-8"), dest=buffer)
        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        print(f"Erreur génération PDF : {e}")
        return None


def notifier_nouvelle_reservation(reservation) -> None:
    """Notifie l'admin d'une nouvelle réservation."""
    from apps.auth_app.models import Utilisateur
    admins = Utilisateur.objects.filter(role__nom="ADMIN", est_actif=True)

    message = f"""
Nouvelle demande de réservation reçue.

Numéro : {reservation.numero}
Défunt : {reservation.defunt.nom_complet}
Caveau : {reservation.caveau.reference}
Type : {reservation.type_concession}
Montant : {int(reservation.montant_total_xaf):,} FCFA
Date : {reservation.date_soumission.strftime('%d/%m/%Y à %H:%M')}

Connectez-vous pour valider ou refuser cette demande.

— {settings.APP_NAME}
    """.replace(",", " ")

    for admin in admins:
        envoyer_email(
            destinataire=admin.email,
            sujet=f"[{settings.APP_NAME}] Nouvelle réservation {reservation.numero}",
            message=message,
        )


def notifier_validation_reservation(reservation) -> None:
    """Notifie le client que sa réservation est validée — avec facture PDF en pièce jointe."""
    message = f"""
Bonjour {reservation.client.prenom},

Votre réservation a été validée avec succès.

Numéro : {reservation.numero}
Défunt : {reservation.defunt.nom_complet}
Caveau : {reservation.caveau.reference}
Type de concession : {reservation.type_concession}
Montant total : {int(reservation.montant_total_xaf):,} FCFA
Date de validation : {reservation.date_validation.strftime('%d/%m/%Y')}

Veuillez vous rapprocher de nos services pour finaliser le paiement.
Votre facture est disponible en pièce jointe.

— {settings.APP_NAME}
    """.replace(",", " ")

    # Générer la facture PDF
    pdf_bytes = generer_pdf_facture(reservation)

    if pdf_bytes:
        envoyer_email_avec_pdf(
            destinataire=reservation.client.email,
            sujet=f"[{settings.APP_NAME}] Réservation {reservation.numero} validée",
            message=message,
            pdf_bytes=pdf_bytes,
            nom_fichier=f"facture_{reservation.numero}.pdf",
        )
    else:
        envoyer_email(
            destinataire=reservation.client.email,
            sujet=f"[{settings.APP_NAME}] Réservation {reservation.numero} validée",
            message=message,
        )


def notifier_refus_reservation(reservation) -> None:
    """Notifie le client que sa réservation est refusée."""
    message = f"""
Bonjour {reservation.client.prenom},

Nous vous informons que votre réservation a été refusée.

Numéro : {reservation.numero}
Défunt : {reservation.defunt.nom_complet}
Motif du refus : {reservation.motif_refus or 'Non précisé'}

Pour plus d'informations, contactez nos services.

— {settings.APP_NAME}
    """

    envoyer_email(
        destinataire=reservation.client.email,
        sujet=f"[{settings.APP_NAME}] Réservation {reservation.numero} refusée",
        message=message,
    )


def notifier_expiration_concession(concession) -> None:
    """Notifie le titulaire d'une concession qui expire bientôt."""
    message = f"""
Bonjour {concession.titulaire.prenom},

Votre concession arrive à expiration dans {concession.jours_restants} jours.

Numéro de contrat : {concession.numero_contrat}
Caveau : {concession.caveau.reference}
Type : {concession.type_concession}
Date d'expiration : {concession.date_fin.strftime('%d/%m/%Y')}

Veuillez contacter nos services pour le renouvellement.

— {settings.APP_NAME}
    """

    envoyer_email(
        destinataire=concession.titulaire.email,
        sujet=f"[{settings.APP_NAME}] Concession {concession.numero_contrat} expire bientôt",
        message=message,
    )


def notifier_inscription_client(utilisateur) -> None:
    """Notifie le client après son inscription."""
    message = f"""
Bonjour {utilisateur.prenom} {utilisateur.nom},

Bienvenue sur le portail du Cimetière Municipal de Pointe-Noire !

Votre compte a été créé avec succès.

Email : {utilisateur.email}

Vous pouvez maintenant vous connecter et réserver un caveau en ligne.

— {settings.APP_NAME}
    """

    envoyer_email(
        destinataire=utilisateur.email,
        sujet=f"[{settings.APP_NAME}] Bienvenue — Compte créé avec succès",
        message=message,
    )


def notifier_paiement_recu(paiement) -> None:
    """Notifie l'admin qu'un paiement a été reçu."""
    from apps.auth_app.models import Utilisateur

    admins = Utilisateur.objects.filter(role__nom__in=["ADMIN", "SECRETARIAT"], est_actif=True)

    canal_labels = {
        "MTN_MOMO": "MTN MoMo",
        "AIRTEL_MONEY": "Airtel Money",
        "ESPECES": "Espèces",
        "VIREMENT": "Virement bancaire",
        "CHEQUE": "Chèque",
    }
    canal = canal_labels.get(paiement.canal, paiement.canal)
    reservation = paiement.reservation
    client = paiement.client

    message = f"""
Nouveau paiement reçu.

Client : {client.prenom} {client.nom}
Email : {client.email}
Canal : {canal}
Montant : {int(paiement.montant_xaf):,} FCFA
N° Transaction : {paiement.numero_transaction or '—'}
Réservation : {reservation.numero if reservation else '—'}
Date : {paiement.date_paiement.strftime('%d/%m/%Y à %H:%M')}

— {settings.APP_NAME}
    """.replace(",", " ")

    for admin in admins:
        envoyer_email(
            destinataire=admin.email,
            sujet=f"[{settings.APP_NAME}] Paiement reçu — {int(paiement.montant_xaf):,} FCFA".replace(",", " "),
            message=message,
        )