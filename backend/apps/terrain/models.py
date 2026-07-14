from django.contrib.gis.db import models as gis_models
from django.db import models
from auditlog.registry import auditlog


class Cimetiere(models.Model):
    nom = models.CharField(max_length=200, default="Cimetière Municipal de Pointe-Noire")
    adresse = models.TextField()
    ville = models.CharField(max_length=100, default="Pointe-Noire")
    pays = models.CharField(max_length=100, default="République du Congo")
    telephone = models.CharField(max_length=20, blank=True)
    email_contact = models.EmailField(blank=True)
    superficie_m2 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    taille_std_longueur = models.DecimalField(max_digits=5, decimal_places=2, default=2.50)
    taille_std_largeur = models.DecimalField(max_digits=5, decimal_places=2, default=1.20)
    taille_std_profondeur = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)
    coordonnees_centre = gis_models.PointField(null=True, blank=True, srid=4326)
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cimetière"
        verbose_name_plural = "Cimetières"

    def __str__(self):
        return self.nom


class Zone(models.Model):
    TYPE_CHOICES = [
        ("INHUMATION", "Zone d'inhumation"),
        ("ALLEE", "Allée / Chemin"),
        ("NON_EXPLOITABLE", "Zone non exploitable"),
        ("TECHNIQUE", "Zone technique"),
        ("ENTREE", "Entrée / Accueil"),
    ]
    cimetiere = models.ForeignKey(Cimetiere, on_delete=models.CASCADE, related_name="zones")
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    type_zone = models.CharField(max_length=20, choices=TYPE_CHOICES, default="INHUMATION")
    description = models.TextField(blank=True)
    couleur_carte = models.CharField(max_length=7, default="#90EE90")
    geometrie = gis_models.PolygonField(null=True, blank=True, srid=4326)
    est_active = models.BooleanField(default=True)
    ordre_affichage = models.PositiveIntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ["ordre_affichage", "code"]
        unique_together = [["cimetiere", "code"]]

    def __str__(self):
        return f"Zone {self.code} — {self.nom}"


class Bloc(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name="blocs")
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    capacite_theorique = models.PositiveIntegerField(default=0)
    geometrie = gis_models.PolygonField(null=True, blank=True, srid=4326)
    est_actif = models.BooleanField(default=True)
    ordre_affichage = models.PositiveIntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bloc"
        verbose_name_plural = "Blocs"
        ordering = ["ordre_affichage", "code"]
        unique_together = [["zone", "code"]]

    def __str__(self):
        return f"Zone {self.zone.code} — Bloc {self.code}"

    @property
    def reference(self):
        return f"{self.zone.code}-{self.code}"

 # Audit trail
auditlog.register(Cimetiere)
auditlog.register(Zone)
auditlog.register(Bloc)   