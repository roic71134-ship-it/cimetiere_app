import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("cimetiere")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Tâches planifiées automatiques
app.conf.beat_schedule = {
    # Alertes concessions expirantes — tous les jours à 8h00
    "alertes-concessions-quotidien": {
        "task": "apps.concessions.tasks.envoyer_alertes_concessions",
        "schedule": crontab(hour=8, minute=0),
    },
    # Alertes retard paiement — tous les jours à 9h00
    "alertes-paiements-quotidien": {
        "task": "apps.paiements.tasks.alertes_retard_paiement",
        "schedule": crontab(hour=9, minute=0),
    },
    # Alertes seuil places critiques — toutes les heures
    "alertes-seuil-places": {
        "task": "apps.caveaux.tasks.alertes_seuil_places",
        "schedule": crontab(minute=0),
    },
}