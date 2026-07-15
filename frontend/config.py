import os
API_BASE_URL = os.environ.get("API_BASE_URL", "https://cimetiereapp-production.up.railway.app/api/v1")

COULEURS = {
    "primaire":     "#800080",
    "secondaire":   "#9C27B0",
    "accent":       "#E040FB",
    "success":      "#00C896",
    "danger":       "#FF4D6D",
    "warning":      "#FFB703",
    "gris":         "#8892A4",
    "fond":         "#0F0A1E",
    "blanc":        "#FFFFFF",
    "texte":        "#1A1A2E",
    "texte_clair":  "#555577",
    "titre":        "#FFFFFF",
}

STATUTS_CAVEAUX = {
    "DISPONIBLE":      {"label": "Disponible",      "couleur": "#00C896"},
    "RESERVE":         {"label": "Reserve",          "couleur": "#FFB703"},
    "OCCUPE":          {"label": "Occupe",           "couleur": "#FF4D6D"},
    "NON_EXPLOITABLE": {"label": "Non exploitable",  "couleur": "#8892A4"},
    "MAINTENANCE":     {"label": "Maintenance",      "couleur": "#E040FB"},
}

APP_NOM = "Cimetiere_frrance "
APP_VERSION = "1.0.0"
