from ninja import Router
from django.shortcuts import get_object_or_404
from .models import Paiement
from .schemas import PaiementCreateSchema, PaiementSchema, MessageSchema

router = Router()


@router.get("/", response=list[PaiementSchema])
def liste_paiements(request, statut: str = None):
    qs = Paiement.objects.select_related("client", "reservation")
    if statut:
        qs = qs.filter(statut=statut)
    if request.auth.role and request.auth.role.nom == "CLIENT":
        qs = qs.filter(client=request.auth)
    return qs


@router.post("/", response=MessageSchema)
def enregistrer_paiement(request, data: PaiementCreateSchema):
    if not request.auth.a_permission("peut_enregistrer_paiements"):
        return {"message": "Permission refusée.", "reference": ""}

    paiement = Paiement.objects.create(
        client=request.auth,
        reservation_id=data.reservation_id,
        montant_xaf=data.montant_xaf,
        canal=data.canal,
        numero_transaction=data.numero_transaction,
        notes=data.notes,
        enregistre_par=request.auth,
        statut="CONFIRME",
    )
    paiement.date_confirmation = paiement.date_creation
    paiement.save()

    return {
        "message": f"Paiement de {int(data.montant_xaf):,} FCFA enregistré avec succès.".replace(",", " "),
        "reference": paiement.reference,
    }


@router.get("/solde/{reservation_id}")
def solde_reservation(request, reservation_id: int):
    from apps.reservations.models import Reservation
    from django.db.models import Sum

    reservation = get_object_or_404(Reservation, id=reservation_id)
    total_paye = Paiement.objects.filter(
        reservation=reservation,
        statut="CONFIRME",
    ).aggregate(total=Sum("montant_xaf"))["total"] or 0

    montant_total = reservation.montant_total_xaf
    solde_restant = float(montant_total) - float(total_paye)

    return {
        "reservation_numero": reservation.numero,
        "montant_total_xaf": int(montant_total),
        "total_paye_xaf": int(total_paye),
        "solde_restant_xaf": int(max(0, solde_restant)),
        "est_solde": solde_restant <= 0,
    }


@router.post("/simuler-mobile-money", response=MessageSchema)
def simuler_mobile_money(request, reservation_id: int, montant: float, canal: str, telephone: str):
    """Simule un paiement Mobile Money (MTN MoMo ou Airtel Money)."""
    import random
    import string
    from apps.reservations.models import Reservation

    reservation = get_object_or_404(Reservation, id=reservation_id)

    if reservation.client != request.auth:
        return {"message": "Accès refusé.", "reference": ""}

    if reservation.statut != "VALIDEE":
        return {"message": "La réservation doit être validée pour effectuer un paiement.", "reference": ""}

    numero_transaction = "SIM-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    paiement = Paiement.objects.create(
        client=request.auth,
        reservation=reservation,
        montant_xaf=montant,
        canal=canal,
        numero_transaction=numero_transaction,
        notes=f"Paiement simulé depuis le numéro {telephone}",
        statut="CONFIRME",
    )
    from django.utils import timezone
    paiement.date_confirmation = timezone.now()
    paiement.save()

    canal_label = "MTN MoMo" if canal == "MTN_MOMO" else "Airtel Money"

    # Notifier l'admin
    try:
        from apps.notifications.services import notifier_paiement_recu
        notifier_paiement_recu(paiement)
    except Exception as e:
        print(f"Erreur notification paiement: {e}")

    return {
        "message": f"Paiement {canal_label} de {int(montant):,} FCFA confirmé ! N° transaction : {numero_transaction}".replace(",", " "),
        "reference": paiement.reference,
    }


@router.get("/{paiement_id}", response=PaiementSchema)
def detail_paiement(request, paiement_id: int):
    return get_object_or_404(Paiement, id=paiement_id)


@router.post("/{paiement_id}/confirmer", response=MessageSchema)
def confirmer_paiement(request, paiement_id: int):
    if not request.auth.a_permission("peut_enregistrer_paiements"):
        return {"message": "Permission refusée.", "reference": ""}

    paiement = get_object_or_404(Paiement, id=paiement_id)
    paiement.confirmer(agent=request.auth)

    return {
        "message": f"Paiement {paiement.reference} confirmé.",
        "reference": paiement.reference,
    }