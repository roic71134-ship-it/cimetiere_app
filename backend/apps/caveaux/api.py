from ninja import Router
from django.shortcuts import get_object_or_404
from .models import Caveau
from .schemas import CaveauSchema, CaveauGeoJSONSchema

router = Router()


@router.get("/", response=list[CaveauSchema])
def liste_caveaux(request, statut: str = None, zone_code: str = None):
    qs = Caveau.objects.select_related("bloc", "bloc__zone")
    if statut:
        qs = qs.filter(statut=statut)
    if zone_code:
        qs = qs.filter(bloc__zone__code=zone_code)
    return qs


@router.get("/geojson", auth=None)
def caveaux_geojson(request, zone_code: str = None):
    """Retourne tous les caveaux au format GeoJSON pour la carte Leaflet."""
    qs = Caveau.objects.select_related("bloc", "bloc__zone")
    if zone_code:
        qs = qs.filter(bloc__zone__code=zone_code)
    features = [c.to_geojson_feature() for c in qs]
    return {
        "type": "FeatureCollection",
        "features": features,
        "total": len(features),
    }


@router.get("/{caveau_id}", response=CaveauSchema)
def detail_caveau(request, caveau_id: int):
    return get_object_or_404(Caveau, id=caveau_id)


@router.patch("/{caveau_id}/statut")
def changer_statut(request, caveau_id: int, statut: str):
    """Change le statut d'un caveau."""
    caveau = get_object_or_404(Caveau, id=caveau_id)
    statuts_valides = ["DISPONIBLE", "RESERVE", "OCCUPE", "NON_EXPLOITABLE", "MAINTENANCE"]
    if statut not in statuts_valides:
        return {"error": f"Statut invalide. Choisir parmi : {statuts_valides}"}
    caveau.changer_statut(statut, utilisateur=request.auth)
    return {"message": f"Statut changé vers {statut}", "reference": caveau.reference}

from ninja import Schema
from typing import Optional


class CaveauCreateSchema(Schema):
    bloc_id: int
    numero: int
    latitude: float
    longitude: float
    type_concession: str = "TEMPORAIRE"
    prix_temporaire_xaf: int = 150000
    prix_perpetuelle_xaf: int = 500000
    capacite_corps: int = 1
    notes: str = ""


@router.post("/", auth=None)
def creer_caveau(request, data: CaveauCreateSchema):
    from django.contrib.gis.geos import Point
    from apps.terrain.models import Bloc
    
    bloc = Bloc.objects.filter(id=data.bloc_id).first()
    if not bloc:
        return {"message": "Bloc introuvable."}

    reference = f"{bloc.zone.code}-{bloc.code}-{str(data.numero).zfill(3)}"

    if Caveau.objects.filter(reference=reference).exists():
        return {"message": f"Le caveau {reference} existe déjà."}

    caveau = Caveau.objects.create(
        bloc=bloc,
        reference=reference,
        numero=data.numero,
        coordonnees=Point(data.longitude, data.latitude, srid=4326),
        type_concession_autorise=data.type_concession,
        prix_temporaire_xaf=data.prix_temporaire_xaf,
        prix_perpetuelle_xaf=data.prix_perpetuelle_xaf,
        capacite_corps=data.capacite_corps,
        notes=data.notes,
    )
    return {"message": f"Caveau {caveau.reference} créé avec succès.", "id": caveau.id, "reference": caveau.reference}