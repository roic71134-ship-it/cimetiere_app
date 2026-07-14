from ninja import Router
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Reservation, Defunt
from .schemas import (
    ReservationCreateSchema, ReservationSchema,
    ValidationSchema, RefusSchema, MessageSchema
)
from apps.caveaux.models import Caveau, StatutCaveau

router = Router()


@router.get("/", response=list[ReservationSchema])
def liste_reservations(request, statut: str = None):
    qs = Reservation.objects.select_related(
        "client", "agent_validation", "caveau", "defunt"
    )
    if statut:
        qs = qs.filter(statut=statut)
    if request.auth.role and request.auth.role.nom == "CLIENT":
        qs = qs.filter(client=request.auth)
    return qs


@router.post("/", response=MessageSchema)
def creer_reservation(request, data: ReservationCreateSchema):
    caveau = get_object_or_404(Caveau, id=data.caveau_id)

    if caveau.statut != StatutCaveau.DISPONIBLE:
        return {"message": "Ce caveau n'est pas disponible.", "numero": ""}

    montants = {
        "TEMPORAIRE": caveau.prix_temporaire_xaf,
        "TRENTENAIRE": caveau.prix_trentenaire_xaf,
        "PERPETUELLE": caveau.prix_perpetuelle_xaf,
        "FAMILIALE": caveau.prix_perpetuelle_xaf,
    }
    montant = montants.get(data.type_concession, 0)

    defunt = Defunt.objects.create(**data.defunt.dict())

    reservation = Reservation.objects.create(
        client=request.auth,
        caveau=caveau,
        defunt=defunt,
        type_concession=data.type_concession,
        montant_total_xaf=montant,
        notes_client=data.notes_client,
    )

    caveau.changer_statut(StatutCaveau.RESERVE, utilisateur=request.auth)

    # Notification email admin
    try:
        from apps.notifications.services import notifier_nouvelle_reservation
        notifier_nouvelle_reservation(reservation)
    except Exception as e:
        print(f"Erreur notification: {e}")

    return {
        "message": "Réservation soumise avec succès.",
        "numero": reservation.numero,
    }


@router.get("/{reservation_id}", response=ReservationSchema)
def detail_reservation(request, reservation_id: int):
    return get_object_or_404(Reservation, id=reservation_id)


@router.post("/{reservation_id}/valider", response=MessageSchema)
def valider_reservation(request, reservation_id: int, data: ValidationSchema):
    if not request.auth.a_permission("peut_valider_reservations"):
        return {"message": "Permission refusée.", "numero": ""}

    reservation = get_object_or_404(Reservation, id=reservation_id)

    if reservation.statut != "EN_ATTENTE":
        return {"message": "Cette réservation ne peut pas être validée.", "numero": ""}

    if data.notes_admin:
        reservation.notes_admin = data.notes_admin

    reservation.valider(request.auth)

    # Notification email client
    try:
        from apps.notifications.services import notifier_validation_reservation
        notifier_validation_reservation(reservation)
    except Exception as e:
        print(f"Erreur notification: {e}")

    # Créer la concession
    try:
        from apps.concessions.models import Concession
        Concession.creer_depuis_reservation(reservation)
    except Exception as e:
        print(f"Erreur création concession: {e}")

    return {
        "message": f"Réservation {reservation.numero} validée.",
        "numero": reservation.numero,
    }

@router.post("/{reservation_id}/refuser", response=MessageSchema)
def refuser_reservation(request, reservation_id: int, data: RefusSchema):
    if not request.auth.a_permission("peut_valider_reservations"):
        return {"message": "Permission refusée.", "numero": ""}

    reservation = get_object_or_404(Reservation, id=reservation_id)

    if reservation.statut != "EN_ATTENTE":
        return {"message": "Cette réservation ne peut pas être refusée.", "numero": ""}

    reservation.refuser(request.auth, motif=data.motif_refus)

    # Notification email client
    try:
        from apps.notifications.services import notifier_refus_reservation
        notifier_refus_reservation(reservation)
    except Exception as e:
        print(f"Erreur notification: {e}")

    return {
        "message": f"Réservation {reservation.numero} refusée.",
        "numero": reservation.numero,
    }


@router.delete("/{reservation_id}/annuler", response=MessageSchema)
def annuler_reservation(request, reservation_id: int):
    reservation = get_object_or_404(
        Reservation, id=reservation_id, client=request.auth
    )

    if reservation.statut not in ["EN_ATTENTE"]:
        return {"message": "Cette réservation ne peut plus être annulée.", "numero": ""}

    reservation.statut = "ANNULEE"
    reservation.save()
    reservation.caveau.changer_statut(StatutCaveau.DISPONIBLE, utilisateur=request.auth)

    return {
        "message": "Réservation annulée.",
        "numero": reservation.numero,
    }



@router.get("/{reservation_id}/facture-pdf", auth=None)
def telecharger_facture(request, reservation_id: int):
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404

    reservation = get_object_or_404(Reservation, id=reservation_id)

    html = _generer_html_facture(reservation)

    try:
        from xhtml2pdf import pisa
        import io
        buffer = io.BytesIO()
        pisa.CreatePDF(html.encode("utf-8"), dest=buffer)
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="facture_{reservation.numero}.pdf"'
        return response
    except Exception as e:
        print(f"xhtml2pdf erreur: {e}")
        return HttpResponse(html, content_type="text/html; charset=utf-8");

def _generer_html_facture(reservation):
    from django.utils.timezone import localtime

    client = reservation.client
    defunt = reservation.defunt
    caveau = reservation.caveau
    date_val = localtime(reservation.date_validation).strftime("%d/%m/%Y") if reservation.date_validation else "—"
    date_soumis = localtime(reservation.date_soumission).strftime("%d/%m/%Y")

    types_labels = {
        "TEMPORAIRE": "Temporaire (5 ans)",
        "TRENTENAIRE": "Trentenaire (30 ans)",
        "PERPETUELLE": "Perpétuelle",
        "FAMILIALE": "Familiale",
    }
    type_label = types_labels.get(reservation.type_concession, reservation.type_concession)
    montant = f"{int(reservation.montant_total_xaf):,}".replace(",", " ")
    statut_color = {
        "VALIDEE": "#2e7d32", "EN_ATTENTE": "#e65100", "REFUSEE": "#c62828",
    }.get(reservation.statut, "#555")

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<style>
  @page {{ margin: 20mm; size: A4; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }}
  body {{ color: #333; font-size: 13px; line-height: 1.5; }}
  .header {{ display: flex; justify-content: space-between; align-items: flex-start;
             border-bottom: 3px solid #1b5e20; padding-bottom: 15px; margin-bottom: 25px; }}
  .logo-zone h1 {{ color: #1b5e20; font-size: 20px; margin-bottom: 4px; }}
  .logo-zone p {{ color: #666; font-size: 12px; }}
  .facture-info {{ text-align: right; }}
  .facture-info h2 {{ color: #1b5e20; font-size: 22px; margin-bottom: 5px; }}
  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px;
            font-size: 12px; font-weight: bold; color: white; background: {statut_color}; }}
  .section-title {{ background: #f1f8e9; padding: 8px 12px; font-weight: bold;
                    color: #1b5e20; border-left: 4px solid #1b5e20; margin: 20px 0 10px; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px 30px; padding: 0 5px; }}
  .champ label {{ color: #888; font-size: 11px; display: block; }}
  .champ span {{ font-size: 13px; color: #222; font-weight: 500; }}
  .montant-box {{ background: #1b5e20; color: white; border-radius: 8px;
                  padding: 15px 20px; text-align: center; margin: 20px 0; }}
  .montant-box .label {{ font-size: 12px; opacity: .85; margin-bottom: 5px; }}
  .montant-box .valeur {{ font-size: 26px; font-weight: bold; }}
  .montant-box .devise {{ font-size: 13px; opacity: .8; }}
  .footer {{ border-top: 1px solid #ddd; padding-top: 12px; margin-top: 30px;
             font-size: 11px; color: #888; text-align: center; }}
</style>
</head>
<body>
<div class="header">
  <div class="logo-zone">
    <h1>Cimetière Municipal de Pointe-Noire</h1>
    <p>République du Congo — Service de gestion funéraire</p>
  </div>
  <div class="facture-info">
    <h2>FACTURE</h2>
    <div>N° {reservation.numero}</div>
    <div>Date : {date_soumis}</div>
    <span class="badge">{reservation.get_statut_display()}</span>
  </div>
</div>

<div class="section-title">Informations du client</div>
<div class="grid-2">
  <div class="champ"><label>Nom complet</label><span>{client.prenom} {client.nom}</span></div>
  <div class="champ"><label>Email</label><span>{client.email}</span></div>
  <div class="champ"><label>Date validation</label><span>{date_val}</span></div>
</div>

<div class="section-title">Informations du défunt</div>
<div class="grid-2">
  <div class="champ"><label>Nom complet</label><span>{defunt.prenom} {defunt.nom}</span></div>
  <div class="champ"><label>Date de décès</label><span>{defunt.date_deces}</span></div>
  <div class="champ"><label>Lieu de décès</label><span>{defunt.lieu_deces or "—"}</span></div>
  <div class="champ"><label>N° Acte de décès</label><span>{defunt.numero_acte_deces or "—"}</span></div>
  <div class="champ"><label>N° Permis d'inhumer</label><span>{defunt.numero_permis_inhumer or "—"}</span></div>
  <div class="champ"><label>Famille responsable</label><span>{defunt.nom_famille_responsable or "—"}</span></div>
</div>

<div class="section-title">Détails de la concession</div>
<div class="grid-2">
  <div class="champ"><label>Caveau</label><span>{caveau.reference if caveau else "—"}</span></div>
  <div class="champ"><label>Type de concession</label><span>{type_label}</span></div>
  <div class="champ"><label>Zone</label><span>{caveau.bloc.zone.nom if caveau and caveau.bloc else "—"}</span></div>
  <div class="champ"><label>Bloc</label><span>{caveau.bloc.nom if caveau and caveau.bloc else "—"}</span></div>
</div>

<div class="montant-box">
  <div class="label">MONTANT TOTAL À PAYER</div>
  <div class="valeur">{montant}</div>
  <div class="devise">Francs CFA (FCFA)</div>
</div>

<div class="footer">
  <p>Document officiel — Cimetière Municipal de Pointe-Noire</p>
  <p>Réservation N° {reservation.numero} — Généré le {date_soumis}</p>
</div>
</body>
</html>"""