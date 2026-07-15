import os
API_BASE_URL = os.environ.get("API_BASE_URL", "https://cimetiereapp-production.up.railway.app/api/v1")

COULEURS = {
    "primaire":     "#1B3A5C",
    "secondaire":   "#2C5282",
    "accent":       "#4A7A96",
    "success":      "#2E7D5B",
    "danger":       "#B23A48",
    "warning":      "#C08A2E",
    "gris":         "#8892A4",
    "fond":         "#0F1419",
    "blanc":        "#FFFFFF",
    "texte":        "#1A1A2E",
    "texte_clair":  "#5A6472",
    "titre":        "#FFFFFF",
}

STATUTS_CAVEAUX = {
    "DISPONIBLE":      {"label": "Disponible",      "couleur": "#2E7D5B"},
    "RESERVE":         {"label": "Reserve",          "couleur": "#C08A2E"},
    "OCCUPE":          {"label": "Occupe",           "couleur": "#B23A48"},
    "NON_EXPLOITABLE": {"label": "Non exploitable",  "couleur": "#8892A4"},
    "MAINTENANCE":     {"label": "Maintenance",      "couleur": "#4A7A96"},
}

APP_NOM = "Cimetiere_frrance "
APP_VERSION = "1.0.0"
