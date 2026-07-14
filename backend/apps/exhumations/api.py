from ninja import Router
from django.shortcuts import get_object_or_404
from .models import Exhumation
from .schemas import (
    ExhumationCreateSchema, ExhumationSchema,
    ValidationExhumationSchema, RefusExhumationSchema, MessageSchema
)

router = Router()


@router.get("/", response=list[ExhumationSchema])
def liste_exhumations(request, statut: str = None):
    qs = Exhumation.objects.select_related(
        "caveau", "defunt", "demandeur", "agent_validation"
    )
    if statut:
        qs = qs.filter(statut=statut)
    if request.auth.role and request.auth.role.nom == "CLIENT":
        qs = qs.filter(demandeur=request.auth)
    return qs


@router.post("/", response=MessageSchema)
def creer_exhumation(request, data: ExhumationCreateSchema):
    exhumation = Exhumation.objects.create(
        caveau_id=data.caveau_id,
        defunt_id=data.defunt_id,
        concession_id=data.concession_id,
        demandeur=request.auth,
        motif=data.motif,
        motif_detail=data.motif_detail,
        date_exhumation_prevue=data.date_exhumation_prevue,
        notes=data.notes,
    )
    return {
        "message": f"Demande d'exhumation {exhumation.numero} soumise avec succès.",
        "numero": exhumation.numero,
    }


@router.get("/{exhumation_id}", response=ExhumationSchema)
def detail_exhumation(request, exhumation_id: int):
    return get_object_or_404(Exhumation, id=exhumation_id)


@router.post("/{exhumation_id}/valider", response=MessageSchema)
def valider_exhumation(request, exhumation_id: int, data: ValidationExhumationSchema):
    if not request.auth.a_permission("peut_gerer_exhumations"):
        return {"message": "Permission refusée.", "numero": ""}

    exhumation = get_object_or_404(Exhumation, id=exhumation_id)

    if exhumation.statut != "EN_ATTENTE":
        return {"message": "Cette exhumation ne peut pas être validée.", "numero": ""}

    if data.notes:
        exhumation.notes = data.notes

    exhumation.valider(request.auth)

    return {
        "message": f"Exhumation {exhumation.numero} validée.",
        "numero": exhumation.numero,
    }


@router.post("/{exhumation_id}/refuser", response=MessageSchema)
def refuser_exhumation(request, exhumation_id: int, data: RefusExhumationSchema):
    if not request.auth.a_permission("peut_gerer_exhumations"):
        return {"message": "Permission refusée.", "numero": ""}

    exhumation = get_object_or_404(Exhumation, id=exhumation_id)

    if exhumation.statut != "EN_ATTENTE":
        return {"message": "Cette exhumation ne peut pas être refusée.", "numero": ""}

    exhumation.refuser(request.auth, motif=data.motif_refus)

    return {
        "message": f"Exhumation {exhumation.numero} refusée.",
        "numero": exhumation.numero,
    }

@router.get("/{exhumation_id}/autorisation-pdf", auth=None)
def telecharger_autorisation_exhumation(request, exhumation_id: int):
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404

    exhumation = get_object_or_404(Exhumation, id=exhumation_id)
    html = _generer_html_autorisation(exhumation)

    try:
        from xhtml2pdf import pisa
        import io
        buffer = io.BytesIO()
        pisa.CreatePDF(html.encode("utf-8"), dest=buffer)
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="autorisation_{exhumation.numero}.pdf"'
        return response
    except Exception as e:
        return HttpResponse(html, content_type="text/html; charset=utf-8")


def _generer_html_autorisation(exhumation):
    from django.utils.timezone import localtime

    demandeur = exhumation.demandeur
    caveau = exhumation.caveau
    defunt = exhumation.defunt
    date_demande = localtime(exhumation.date_demande).strftime("%d/%m/%Y")
    date_validation = localtime(exhumation.date_validation).strftime("%d/%m/%Y") if exhumation.date_validation else "—"
    date_prevue = exhumation.date_exhumation_prevue.strftime("%d/%m/%Y") if exhumation.date_exhumation_prevue else "—"

    motif_labels = {
        "TRANSFERT": "Transfert vers un autre cimetière",
        "RENOVATION": "Rénovation du caveau",
        "FAMILIAL": "Regroupement familial",
        "JUDICIAIRE": "Ordonnance judiciaire",
        "AUTRE": "Autre motif",
    }
    motif_label = motif_labels.get(exhumation.motif, exhumation.motif)

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<style>
  @page {{ margin: 20mm; size: A4; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }}
  body {{ color: #333; font-size: 13px; line-height: 1.6; }}

  .header {{ text-align: center; border-bottom: 3px solid #1b5e20; padding-bottom: 15px; margin-bottom: 25px; }}
  .header h1 {{ color: #1b5e20; font-size: 18px; margin-bottom: 5px; }}
  .header p {{ color: #666; font-size: 12px; }}

  .titre-doc {{ text-align: center; margin: 20px 0; }}
  .titre-doc h2 {{ font-size: 20px; color: #1b5e20; text-transform: uppercase; letter-spacing: 2px; }}
  .titre-doc .numero {{ font-size: 14px; color: #555; margin-top: 5px; }}

  .section-title {{ background: #f1f8e9; padding: 8px 12px; font-weight: bold;
                    color: #1b5e20; border-left: 4px solid #1b5e20; margin: 20px 0 10px; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px 30px; padding: 0 5px; }}
  .champ label {{ color: #888; font-size: 11px; display: block; }}
  .champ span {{ font-size: 13px; color: #222; font-weight: 500; }}

  .motif-box {{ background: #fff3e0; border-left: 4px solid #e65100;
                padding: 12px 15px; margin: 15px 0; border-radius: 4px; }}
  .motif-box .label {{ color: #e65100; font-size: 11px; font-weight: bold; }}
  .motif-box .valeur {{ font-size: 14px; color: #333; margin-top: 3px; }}

  .signature-zone {{ margin-top: 40px; display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
  .signature-box {{ border-top: 1px solid #ccc; padding-top: 10px; text-align: center; }}
  .signature-box .label {{ font-size: 11px; color: #888; }}
  .signature-box .espace {{ height: 60px; }}

  .footer {{ border-top: 1px solid #ddd; padding-top: 12px; margin-top: 30px;
             font-size: 11px; color: #888; text-align: center; }}

  .badge-valide {{ display: inline-block; background: #2e7d32; color: white;
                   padding: 4px 14px; border-radius: 20px; font-size: 12px;
                   font-weight: bold; margin-top: 8px; }}
</style>
</head>
<body>

<div class="header">
  <h1>🏛 Cimetière Municipal de Pointe-Noire</h1>
  <p>République du Congo — Service de gestion funéraire</p>
  <p>Email : contact@cimetiere-pn.cg</p>
</div>

<div class="titre-doc">
  <h2>Autorisation d'Exhumation</h2>
  <div class="numero">N° {exhumation.numero}</div>
  <span class="badge-valide">✓ VALIDÉE</span>
</div>

<div class="section-title">Informations du demandeur</div>
<div class="grid-2">
  <div class="champ"><label>Nom complet</label><span>{demandeur.prenom} {demandeur.nom}</span></div>
  <div class="champ"><label>Email</label><span>{demandeur.email}</span></div>
  <div class="champ"><label>Date de la demande</label><span>{date_demande}</span></div>
  <div class="champ"><label>Date de validation</label><span>{date_validation}</span></div>
</div>

<div class="section-title">Informations du défunt</div>
<div class="grid-2">
  <div class="champ"><label>Nom complet</label><span>{defunt.prenom if defunt else '—'} {defunt.nom if defunt else ''}</span></div>
  <div class="champ"><label>Date de décès</label><span>{defunt.date_deces if defunt else '—'}</span></div>
  <div class="champ"><label>N° Acte de décès</label><span>{defunt.numero_acte_deces if defunt else '—'}</span></div>
  <div class="champ"><label>Caveau</label><span>{caveau.reference if caveau else '—'}</span></div>
</div>

<div class="section-title">Détails de l'exhumation</div>
<div class="motif-box">
  <div class="label">MOTIF DE L'EXHUMATION</div>
  <div class="valeur">{motif_label}</div>
  {f'<div style="margin-top:8px; font-size:12px; color:#555">{exhumation.motif_detail}</div>' if exhumation.motif_detail else ''}
</div>
<div class="grid-2">
  <div class="champ"><label>Date prévue</label><span>{date_prevue}</span></div>
  <div class="champ"><label>Statut</label><span>{exhumation.get_statut_display()}</span></div>
</div>

<div class="signature-zone">
  <div class="signature-box">
    <div class="espace"></div>
    <div class="label">Le Demandeur</div>
    <div style="font-size:12px; margin-top:5px">{demandeur.prenom} {demandeur.nom}</div>
  </div>
  <div class="signature-box">
    <div class="espace"></div>
    <div class="label">Le Directeur du Cimetière Municipal</div>
    <div style="font-size:12px; margin-top:5px">Cimetière Municipal de Pointe-Noire</div>
  </div>
</div>

<div class="footer">
  <p>Document officiel — Cimetière Municipal de Pointe-Noire — République du Congo</p>
  <p>Autorisation N° {exhumation.numero} — Générée le {date_demande}</p>
</div>

</body>
</html>"""    

@router.post("/{exhumation_id}/effectuer", response=MessageSchema)
def marquer_effectuee(request, exhumation_id: int):
    exhumation = get_object_or_404(Exhumation, id=exhumation_id)

    if exhumation.statut != "VALIDEE":
        return {"message": "Cette exhumation doit être validée avant d'être effectuée.", "numero": ""}

    from datetime import date
    exhumation.statut = "EFFECTUEE"
    exhumation.date_exhumation_reelle = date.today()
    exhumation.save()

    return {
        "message": f"Exhumation {exhumation.numero} marquée comme effectuée.",
        "numero": exhumation.numero,
    }

@router.get("/{exhumation_id}/proces-verbal-pdf", auth=None)
def telecharger_proces_verbal(request, exhumation_id: int):
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404

    exhumation = get_object_or_404(Exhumation, id=exhumation_id)

    if exhumation.statut != "EFFECTUEE":
        return HttpResponse("L'exhumation doit être effectuée pour générer le procès-verbal.", status=400)

    html = _generer_html_pv(exhumation)

    try:
        from xhtml2pdf import pisa
        import io
        buffer = io.BytesIO()
        pisa.CreatePDF(html.encode("utf-8"), dest=buffer)
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="pv_{exhumation.numero}.pdf"'
        return response
    except Exception as e:
        return HttpResponse(html, content_type="text/html; charset=utf-8")


def _generer_html_pv(exhumation):
    from django.utils.timezone import localtime

    demandeur = exhumation.demandeur
    caveau = exhumation.caveau
    defunt = exhumation.defunt
    date_demande = localtime(exhumation.date_demande).strftime("%d/%m/%Y")
    date_validation = localtime(exhumation.date_validation).strftime("%d/%m/%Y") if exhumation.date_validation else "—"
    date_prevue = exhumation.date_exhumation_prevue.strftime("%d/%m/%Y") if exhumation.date_exhumation_prevue else "—"
    date_reelle = exhumation.date_exhumation_reelle.strftime("%d/%m/%Y") if exhumation.date_exhumation_reelle else "—"

    motif_labels = {
        "TRANSFERT": "Transfert vers un autre cimetière",
        "RENOVATION": "Rénovation du caveau",
        "FAMILIAL": "Regroupement familial",
        "JUDICIAIRE": "Ordonnance judiciaire",
        "AUTRE": "Autre motif",
    }
    motif_label = motif_labels.get(exhumation.motif, exhumation.motif)

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<style>
  @page {{ margin: 20mm; size: A4; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }}
  body {{ color: #333; font-size: 13px; line-height: 1.6; }}
  .header {{ text-align: center; border-bottom: 3px solid #1b5e20; padding-bottom: 15px; margin-bottom: 25px; }}
  .header h1 {{ color: #1b5e20; font-size: 18px; margin-bottom: 5px; }}
  .header p {{ color: #666; font-size: 12px; }}
  .titre-doc {{ text-align: center; margin: 20px 0; }}
  .titre-doc h2 {{ font-size: 20px; color: #1b5e20; text-transform: uppercase; letter-spacing: 2px; }}
  .titre-doc .numero {{ font-size: 14px; color: #555; margin-top: 5px; }}
  .badge {{ display: inline-block; background: #1B4F72; color: white;
            padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-top: 8px; }}
  .section-title {{ background: #f1f8e9; padding: 8px 12px; font-weight: bold;
                    color: #1b5e20; border-left: 4px solid #1b5e20; margin: 20px 0 10px; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px 30px; padding: 0 5px; }}
  .champ label {{ color: #888; font-size: 11px; display: block; }}
  .champ span {{ font-size: 13px; color: #222; font-weight: 500; }}
  .motif-box {{ background: #e8f5e9; border-left: 4px solid #1b5e20;
                padding: 12px 15px; margin: 15px 0; border-radius: 4px; }}
  .signature-zone {{ margin-top: 40px; display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
  .signature-box {{ border-top: 1px solid #ccc; padding-top: 10px; text-align: center; }}
  .signature-box .espace {{ height: 60px; }}
  .footer {{ border-top: 1px solid #ddd; padding-top: 12px; margin-top: 30px;
             font-size: 11px; color: #888; text-align: center; }}
</style>
</head>
<body>

<div class="header">
  <h1>🏛 Cimetière Municipal de Pointe-Noire</h1>
  <p>République du Congo — Service de gestion funéraire</p>
</div>

<div class="titre-doc">
  <h2>Procès-Verbal d'Exhumation</h2>
  <div class="numero">Réf. {exhumation.numero}</div>
  <span class="badge">✓ EFFECTUÉE</span>
</div>

<div class="section-title">Informations du demandeur</div>
<div class="grid-2">
  <div class="champ"><label>Nom complet</label><span>{demandeur.prenom} {demandeur.nom}</span></div>
  <div class="champ"><label>Email</label><span>{demandeur.email}</span></div>
  <div class="champ"><label>Date de la demande</label><span>{date_demande}</span></div>
  <div class="champ"><label>Date de validation</label><span>{date_validation}</span></div>
</div>

<div class="section-title">Informations du défunt</div>
<div class="grid-2">
  <div class="champ"><label>Nom complet</label><span>{defunt.prenom if defunt else '—'} {defunt.nom if defunt else ''}</span></div>
  <div class="champ"><label>Date de décès</label><span>{defunt.date_deces if defunt else '—'}</span></div>
  <div class="champ"><label>N° Acte de décès</label><span>{defunt.numero_acte_deces if defunt else '—'}</span></div>
  <div class="champ"><label>Caveau</label><span>{caveau.reference if caveau else '—'}</span></div>
</div>

<div class="section-title">Détails de l'exhumation</div>
<div class="motif-box">
  <strong>Motif :</strong> {motif_label}<br>
  {f'<em>{exhumation.motif_detail}</em>' if exhumation.motif_detail else ''}
</div>
<div class="grid-2">
  <div class="champ"><label>Date prévue</label><span>{date_prevue}</span></div>
  <div class="champ"><label>Date effective</label><span>{date_reelle}</span></div>
</div>

<div class="section-title">Attestation</div>
<p style="padding: 0 5px; font-size: 13px;">
  Nous soussignés, certifions que l'exhumation du défunt 
  <strong>{defunt.prenom if defunt else ''} {defunt.nom if defunt else ''}</strong> 
  a été effectuée le <strong>{date_reelle}</strong> au caveau <strong>{caveau.reference if caveau else '—'}</strong>
  du Cimetière Municipal de Pointe-Noire, conformément à l'autorisation délivrée le {date_validation}.
</p>

<div class="signature-zone">
  <div class="signature-box">
    <div class="espace"></div>
    <div style="font-size:11px; color:#888">L'Agent ayant effectué l'exhumation</div>
  </div>
  <div class="signature-box">
    <div class="espace"></div>
    <div style="font-size:11px; color:#888">Le Directeur du Cimetière Municipal</div>
  </div>
</div>

<div class="footer">
  <p>Procès-verbal officiel — Cimetière Municipal de Pointe-Noire — République du Congo</p>
  <p>Réf. {exhumation.numero} — Généré le {date_demande}</p>
</div>

</body>
</html>"""    