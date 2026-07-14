from ninja import Router
from .models import Cimetiere, Zone, Bloc
from .schemas import CimetiereSchema, ZoneSchema, BlocSchema

router = Router()


@router.get("/cimetiere", response=list[CimetiereSchema])
def liste_cimetieres(request):
    return Cimetiere.objects.filter(est_actif=True)


@router.get("/zones", response=list[ZoneSchema])
def liste_zones(request):
    return Zone.objects.filter(est_active=True).select_related("cimetiere")


@router.get("/blocs", response=list[BlocSchema])
def liste_blocs(request):
    return Bloc.objects.filter(est_actif=True).select_related("zone")

from ninja import Schema
from typing import Optional


class ZoneCreateSchema(Schema):
    nom: str
    code: str
    type_zone: str = "INHUMATION"
    description: str = ""
    couleur_carte: str = "#90EE90"


class BlocCreateSchema(Schema):
    zone_id: int
    nom: str
    code: str
    capacite_theorique: int = 0


@router.post("/zones", auth=None)
def creer_zone(request, data: ZoneCreateSchema):
    cimetiere = Cimetiere.objects.filter(est_actif=True).first()
    if not cimetiere:
        return {"message": "Aucun cimetière configuré."}
    if Zone.objects.filter(cimetiere=cimetiere, code=data.code).exists():
        return {"message": f"Le code zone '{data.code}' existe déjà."}
    zone = Zone.objects.create(
        cimetiere=cimetiere,
        nom=data.nom,
        code=data.code,
        type_zone=data.type_zone,
        description=data.description,
        couleur_carte=data.couleur_carte,
    )
    return {"message": f"Zone {zone.code} créée avec succès.", "id": zone.id}


@router.post("/blocs", auth=None)
def creer_bloc(request, data: BlocCreateSchema):
    zone = Zone.objects.filter(id=data.zone_id).first()
    if not zone:
        return {"message": "Zone introuvable."}
    if Bloc.objects.filter(zone=zone, code=data.code).exists():
        return {"message": f"Le code bloc '{data.code}' existe déjà dans cette zone."}
    bloc = Bloc.objects.create(
        zone=zone,
        nom=data.nom,
        code=data.code,
        capacite_theorique=data.capacite_theorique,
    )
    return {"message": f"Bloc {bloc.code} créé avec succès.", "id": bloc.id}

@router.get("/cimetiere/statistiques", auth=None)
def statistiques_terrain(request):
    cimetiere = Cimetiere.objects.filter(est_actif=True).first()
    if not cimetiere:
        return {"message": "Aucun cimetière configuré."}

    from apps.caveaux.models import Caveau

    superficie = float(cimetiere.superficie_m2)
    longueur_std = float(cimetiere.taille_std_longueur)
    largeur_std = float(cimetiere.taille_std_largeur)
    surface_caveau = longueur_std * largeur_std

    # Compter les caveaux non exploitables et allées réels
    from apps.terrain.models import Zone
    zones_non_exploit = Zone.objects.filter(
        cimetiere=cimetiere,
        type_zone__in=["NON_EXPLOITABLE", "ALLEE", "TECHNIQUE", "ENTREE"],
        est_active=True,
    ).count()
    total_zones = Zone.objects.filter(cimetiere=cimetiere, est_active=True).count()

    # Calcul du pourcentage exploitable réel
    if total_zones > 0:
        pct_non_exploit = zones_non_exploit / total_zones
        pct_exploitable = 1 - pct_non_exploit
        # Minimum 50%, maximum 85%
        pct_exploitable = max(0.50, min(0.85, pct_exploitable))
    else:
        pct_exploitable = 0.70  # défaut 70%

    superficie_exploitable = superficie * pct_exploitable
    places_theoriques = int(superficie_exploitable / surface_caveau) if surface_caveau > 0 else 0

    total_caveaux = Caveau.objects.count()
    disponibles = Caveau.objects.filter(statut="DISPONIBLE").count()
    occupes = Caveau.objects.filter(statut="OCCUPE").count()

    return {
        "cimetiere": cimetiere.nom,
        "superficie_m2": superficie,
        "taille_std_longueur": longueur_std,
        "taille_std_largeur": largeur_std,
        "pct_exploitable": round(pct_exploitable * 100, 1),
        "superficie_exploitable_m2": round(superficie_exploitable, 2),
        "places_theoriques": places_theoriques,
        "places_actuelles": total_caveaux,
        "places_disponibles": disponibles,
        "places_occupees": occupes,
        "places_restantes_a_creer": max(0, places_theoriques - total_caveaux),
    }
@router.patch("/cimetiere/configuration", auth=None)
def configurer_cimetiere(request, 
    superficie_m2: float = None,
    taille_std_longueur: float = None,
    taille_std_largeur: float = None,
):
    """Configure les paramètres du cimetière."""
    cimetiere = Cimetiere.objects.filter(est_actif=True).first()
    if not cimetiere:
        return {"message": "Aucun cimetière configuré."}

    if superficie_m2:
        cimetiere.superficie_m2 = superficie_m2
    if taille_std_longueur:
        cimetiere.taille_std_longueur = taille_std_longueur
    if taille_std_largeur:
        cimetiere.taille_std_largeur = taille_std_largeur

    cimetiere.save()

    return {"message": "Configuration mise à jour avec succès."}