from django.contrib.gis.db import models as gis_models
from django.db import models
from auditlog.registry import auditlog


class StatutCaveau(models.TextChoices):
    DISPONIBLE      = "DISPONIBLE",      "Disponible (Vert)"
    RESERVE         = "RESERVE",         "Réservé (Orange)"
    OCCUPE          = "OCCUPE",          "Occupé (Rouge)"
    NON_EXPLOITABLE = "NON_EXPLOITABLE", "Non exploitable (Gris)"
    MAINTENANCE     = "MAINTENANCE",     "En maintenance (Jaune)"


COULEURS_STATUT = {
    "DISPONIBLE":      "#28a745",
    "RESERVE":         "#fd7e14",
    "OCCUPE":          "#dc3545",
    "NON_EXPLOITABLE": "#6c757d",
    "MAINTENANCE":     "#ffc107",
}


class Caveau(models.Model):
    TYPE_CONCESSION_CHOICES = [
        ("TEMPORAIRE",  "Temporaire (5 ans)"),
        ("TRENTENAIRE", "Trentenaire (30 ans)"),
        ("PERPETUELLE", "Perpétuelle"),
        ("FAMILIALE",   "Familiale"),
    ]

    bloc = models.ForeignKey(
        "terrain.Bloc",
        on_delete=models.PROTECT,
        related_name="caveaux"
    )
    reference = models.CharField(max_length=20, unique=True, db_index=True)
    numero = models.PositiveIntegerField()
    statut = models.CharField(
        max_length=20,
        choices=StatutCaveau.choices,
        default=StatutCaveau.DISPONIBLE,
        db_index=True
    )
    statut_change_le = models.DateTimeField(null=True, blank=True)
    statut_change_par = models.ForeignKey(
        "auth_app.Utilisateur",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="caveaux_modifies"
    )
    coordonnees = gis_models.PointField(srid=4326)
    longueur_m = models.DecimalField(max_digits=5, decimal_places=2, default=2.50)
    largeur_m = models.DecimalField(max_digits=5, decimal_places=2, default=1.20)
    profondeur_m = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)
    type_concession_autorise = models.CharField(
        max_length=20,
        choices=TYPE_CONCESSION_CHOICES,
        default="TEMPORAIRE"
    )
    est_accessible_pmr = models.BooleanField(default=False)
    capacite_corps = models.PositiveIntegerField(default=1)
    prix_temporaire_xaf = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    prix_trentenaire_xaf = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    prix_perpetuelle_xaf = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Caveau"
        verbose_name_plural = "Caveaux"
        ordering = ["reference"]
        unique_together = [["bloc", "numero"]]

    def __str__(self):
        return f"Caveau {self.reference} — {self.get_statut_display()}"

    @property
    def couleur_carte(self):
        return COULEURS_STATUT.get(self.statut, "#6c757d")

    @property
    def latitude(self):
        return self.coordonnees.y if self.coordonnees else None

    @property
    def longitude(self):
        return self.coordonnees.x if self.coordonnees else None

    def to_geojson_feature(self):
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude],
            },
            "properties": {
                "id": self.id,
                "reference": self.reference,
                "statut": self.statut,
                "couleur": self.couleur_carte,
                "bloc": str(self.bloc),
                "zone": self.bloc.zone.code,
                "type_concession": self.type_concession_autorise,
                "prix_temporaire": str(self.prix_temporaire_xaf),
                "prix_perpetuelle": str(self.prix_perpetuelle_xaf),
                "capacite": self.capacite_corps,
            },
        }

    def changer_statut(self, nouveau_statut, utilisateur=None):
        from django.utils import timezone
        self.statut = nouveau_statut
        self.statut_change_le = timezone.now()
        self.statut_change_par = utilisateur
        self.save(update_fields=["statut", "statut_change_le", "statut_change_par"])

# Audit trail
auditlog.register(Caveau)        