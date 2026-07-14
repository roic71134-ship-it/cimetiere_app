from ninja import Router
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import date, timedelta
from .models import Concession, RenouvellementConcession
from .schemas import ConcessionSchema, RenouvellementSchema, ResiliationSchema, MessageSchema

router = Router()


@router.get("/", response=list[ConcessionSchema])
def liste_concessions(request, statut: str = None):
    qs = Concession.objects.select_related("caveau", "titulaire")
    if statut:
        qs = qs.filter(statut=statut)
    if request.auth.role and request.auth.role.nom == "CLIENT":
        qs = qs.filter(titulaire=request.auth)
    return qs


@router.get("/{concession_id}", response=ConcessionSchema)
def detail_concession(request, concession_id: int):
    return get_object_or_404(Concession, id=concession_id)


@router.get("/alertes/expiration")
def alertes_expiration(request):
    aujourd_hui = date.today()
    dans_30_jours = aujourd_hui + timedelta(days=30)
    concessions = Concession.objects.filter(
        statut="ACTIVE",
        date_fin__lte=dans_30_jours,
        date_fin__gte=aujourd_hui,
    ).select_related("caveau", "titulaire")
    return {
        "total": concessions.count(),
        "concessions": [
            {
                "numero_contrat": c.numero_contrat,
                "caveau": c.caveau.reference,
                "titulaire": c.titulaire.nom_complet,
                "date_fin": str(c.date_fin),
                "jours_restants": c.jours_restants,
            }
            for c in concessions
        ],
    }


@router.post("/{concession_id}/renouveler", response=MessageSchema)
def renouveler_concession(request, concession_id: int, data: RenouvellementSchema):
    if not request.auth.a_permission("peut_gerer_concessions"):
        return {"message": "Permission refusée.", "numero_contrat": ""}

    concession = get_object_or_404(Concession, id=concession_id)

    if concession.est_perpetuelle:
        return {"message": "Une concession perpétuelle ne peut pas être renouvelée.", "numero_contrat": ""}

    from apps.concessions.models import DUREES_CONCESSION
    duree = DUREES_CONCESSION.get(concession.type_concession, 5)
    ancienne_fin = concession.date_fin
    nouvelle_fin = ancienne_fin.replace(year=ancienne_fin.year + duree)

    RenouvellementConcession.objects.create(
        concession=concession,
        date_ancienne_fin=ancienne_fin,
        date_nouvelle_fin=nouvelle_fin,
        montant_xaf=data.montant_xaf,
        traite_par=request.auth,
        notes=data.notes,
    )

    concession.date_fin = nouvelle_fin
    concession.nombre_renouvellements += 1
    concession.statut = "ACTIVE"
    concession.date_alerte_renouvellement = nouvelle_fin - timedelta(days=30)
    concession.montant_renouvellement_xaf = data.montant_xaf
    concession.save()

    return {
        "message": f"Concession renouvelée jusqu'au {nouvelle_fin}.",
        "numero_contrat": concession.numero_contrat,
    }


@router.post("/{concession_id}/resilier", response=MessageSchema)
def resilier_concession(request, concession_id: int, data: ResiliationSchema):
    if not request.auth.a_permission("peut_gerer_concessions"):
        return {"message": "Permission refusée.", "numero_contrat": ""}

    concession = get_object_or_404(Concession, id=concession_id)

    if concession.statut == "RESILIEE":
        return {"message": "Cette concession est déjà résiliée.", "numero_contrat": ""}

    concession.resilier(agent=request.auth, motif=data.motif_resiliation)

    return {
        "message": f"Concession {concession.numero_contrat} résiliée.",
        "numero_contrat": concession.numero_contrat,
    }


@router.post("/alertes-expiration", auth=None)
def envoyer_alertes_expiration(request):
    """Endpoint à appeler manuellement ou via un cron job."""
    from datetime import date, timedelta
    from apps.notifications.services import envoyer_email

    aujourd_hui = date.today()
    dans_30_jours = aujourd_hui + timedelta(days=30)

    # Concessions qui expirent dans 30 jours et encore actives
    concessions_alertes = Concession.objects.filter(
        statut="ACTIVE",
        date_fin__isnull=False,
        date_fin__lte=dans_30_jours,
        date_fin__gte=aujourd_hui,
    ).select_related("titulaire", "caveau")

    nb_alertes = 0
    for c in concessions_alertes:
        jours = (c.date_fin - aujourd_hui).days
        try:
            envoyer_email(
                destinataire=c.titulaire.email,
                sujet=f"⚠️ Votre concession expire dans {jours} jours",
                message=f"""
Bonjour {c.titulaire.prenom} {c.titulaire.nom},

Votre concession {c.numero_contrat} pour le caveau {c.caveau.reference} expire le {c.date_fin.strftime('%d/%m/%Y')} (dans {jours} jours).

Veuillez contacter le cimetière pour procéder au renouvellement.

Cordialement,
Cimetière Municipal de Pointe-Noire
                """,
            )
            nb_alertes += 1
        except Exception:
            pass

    # Marquer les concessions expirées
    Concession.objects.filter(
        statut="ACTIVE",
        date_fin__lt=aujourd_hui,
    ).update(statut="EXPIREE")

    return {
        "message": f"{nb_alertes} alertes envoyées. Concessions expirées mises à jour.",
        "alertes_envoyees": nb_alertes,
    }