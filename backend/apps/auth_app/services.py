import requests
from django.conf import settings


def envoyer_code_mfa(utilisateur, code: str) -> None:
    sujet = f"Votre code de connexion — {settings.APP_NAME}"
    message_html = (
        f"<p>Bonjour {utilisateur.prenom},</p>"
        f"<p>Votre code est : <strong>{code}</strong></p>"
        f"<p>Valable {settings.MFA_CODE_EXPIRY_MINUTES} minutes.</p>"
    )

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }
    payload = {
        "sender": {
            "name": settings.APP_NAME,
            "email": "mendeltreaor@gmail.com",
        },
        "to": [{"email": utilisateur.email}],
        "subject": sujet,
        "htmlContent": message_html,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code != 201:
        raise Exception(
            f"Échec envoi email MFA via Brevo : {response.status_code} - {response.text}"
        )