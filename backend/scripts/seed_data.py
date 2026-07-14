"""
Script pour initialiser la base de données avec des données de démonstration.
Exécuter avec : python manage.py shell < scripts/init_data.py
Ou : python scripts/seed_data.py (depuis le dossier backend)
"""
import os
import sys
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.users.models import Utilisateur
from apps.terrain.models import Zone, Caveau, Configuration

print("🌱 Initialisation des données...")

# ── Configuration ──────────────────────────────────────────────────────────────
config, _ = Configuration.objects.get_or_create(
    id=1,
    defaults={
        "superficie_totale": 50000,
        "longueur_tombeau": 2.0,
        "largeur_tombeau": 1.0,
        "prix_concession_temporaire": 50000,
        "prix_concession_perpetuelle": 200000,
    }
)
print(f"  ✓ Configuration : superficie={config.superficie_totale} m²")

# ── Utilisateurs ──────────────────────────────────────────────────────────────
admin, created = Utilisateur.objects.get_or_create(
    email="admin@cimetiere.cg",
    defaults={"nom": "Admin", "prenom": "Super", "role": "admin"}
)
if created:
    admin.set_password("Admin@2026!")
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print("  ✓ Admin créé : admin@cimetiere.cg / Admin@2026!")
else:
    print("  · Admin déjà existant")

secretaire, created = Utilisateur.objects.get_or_create(
    email="secretaire@cimetiere.cg",
    defaults={"nom": "Moukassa", "prenom": "Marie", "role": "secretariat", "telephone": "06 111 2222"}
)
if created:
    secretaire.set_password("Secret@2026!")
    secretaire.save()
    print("  ✓ Secrétaire : secretaire@cimetiere.cg / Secret@2026!")

agent, created = Utilisateur.objects.get_or_create(
    email="agent@cimetiere.cg",
    defaults={"nom": "Bouanga", "prenom": "Paul", "role": "agent", "telephone": "05 333 4444"}
)
if created:
    agent.set_password("Agent@2026!")
    agent.save()
    print("  ✓ Agent : agent@cimetiere.cg / Agent@2026!")

client, created = Utilisateur.objects.get_or_create(
    email="client@test.cg",
    defaults={"nom": "Nkounkou", "prenom": "Jean", "role": "client", "telephone": "06 555 6666"}
)
if created:
    client.set_password("Client@2026!")
    client.save()
    print("  ✓ Client : client@test.cg / Client@2026!")

# ── Zones ──────────────────────────────────────────────────────────────────────
zones_data = [
    {"nom": "Section A", "type_zone": "section", "superficie": 5000},
    {"nom": "Section B", "type_zone": "section", "superficie": 5000},
    {"nom": "Bloc Nord", "type_zone": "bloc", "superficie": 3000},
    {"nom": "Allée Principale", "type_zone": "allee", "superficie": 1000},
    {"nom": "Zone technique", "type_zone": "non_exploitable", "superficie": 500},
]

zones = {}
for zd in zones_data:
    z, created = Zone.objects.get_or_create(nom=zd["nom"], defaults=zd)
    zones[zd["nom"]] = z
    if created:
        print(f"  ✓ Zone : {z.nom}")

# ── Caveaux (grille 10×10 dans la Section A) ──────────────────────────────────
zone_a = zones["Section A"]
base_lat = -4.7780
base_lng = 11.8630
espacement = 0.0001  # ~10m

caveaux_crees = 0
for rangee in range(1, 11):
    for col in range(1, 11):
        ref = f"A{rangee:02d}{col:02d}"
        lat = base_lat + (rangee - 1) * espacement
        lng = base_lng + (col - 1) * espacement

        # Quelques caveaux occupés pour la démo
        if rangee <= 2 and col <= 3:
            etat = "occupe"
        elif rangee == 3 and col <= 2:
            etat = "reserve"
        else:
            etat = "disponible"

        _, created = Caveau.objects.get_or_create(
            reference=ref,
            defaults={
                "zone": zone_a,
                "etat": etat,
                "latitude": lat,
                "longitude": lng,
                "rangee": rangee,
                "colonne": col,
            }
        )
        if created:
            caveaux_crees += 1

print(f"  ✓ {caveaux_crees} caveaux créés dans la Section A")

print("\n✅ Initialisation terminée !")
print("\n📋 COMPTES DE TEST :")
print("  admin@cimetiere.cg       / Admin@2026!   (Administrateur)")
print("  secretaire@cimetiere.cg  / Secret@2026!  (Secrétariat)")
print("  agent@cimetiere.cg       / Agent@2026!   (Agent terrain)")
print("  client@test.cg           / Client@2026!  (Client)")
print("\n⚠️  Note : Le MFA envoie un code par email. En développement,")
print("   configurez EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend")
print("   dans settings.py pour voir les codes dans le terminal.")
