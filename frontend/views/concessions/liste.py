import flet as ft
from config import COULEURS


STATUT_COULEURS = {
    "ACTIVE":            "#28a745",
    "EN_RENOUVELLEMENT": "#fd7e14",
    "EXPIREE":           "#dc3545",
    "RESILIEE":          "#6c757d",
}

STATUT_LABELS = {
    "ACTIVE":            "Active",
    "EN_RENOUVELLEMENT": "En renouvellement",
    "EXPIREE":           "Expirée",
    "RESILIEE":          "Résiliée",
}

TYPE_LABELS = {
    "TEMPORAIRE":  "Temporaire (5 ans)",
    "TRENTENAIRE": "Trentenaire (30 ans)",
    "PERPETUELLE": "Perpétuelle",
    "FAMILIALE":   "Familiale",
}


def vue_concessions(page: ft.Page):
    from api_client import client

    liste = ft.Column(spacing=10)

    def badge_statut(statut):
        return ft.Container(
            content=ft.Text(
                STATUT_LABELS.get(statut, statut),
                size=11,
                color="white",
                weight=ft.FontWeight.BOLD,
            ),
            bgcolor=STATUT_COULEURS.get(statut, "#6c757d"),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
        )

    def carte_concession(c):
        jours = c.get("jours_restants")
        alerte = c.get("alerte_expiration", False)
        est_perpetuelle = c.get("date_fin") is None

        info_duree = "Perpétuelle" if est_perpetuelle else (
            f"{jours} jours restants" if jours is not None else "—"
        )

        couleur_duree = COULEURS["danger"] if (alerte and not est_perpetuelle) else COULEURS["texte_clair"]

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        c.get("numero_contrat", ""),
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=COULEURS["primaire"],
                                    ),
                                    ft.Text(
                                        f"Type : {TYPE_LABELS.get(c.get('type_concession', ''), '')}",
                                        size=13,
                                        color=COULEURS["texte"],
                                    ),
                                    ft.Text(
                                        f"Caveau ID : {c.get('caveau_id', '')}",
                                        size=12,
                                        color=COULEURS["texte_clair"],
                                    ),
                                ],
                                spacing=3,
                                expand=True,
                            ),
                            ft.Column(
                                controls=[
                                    badge_statut(c.get("statut", "")),
                                    ft.Container(height=5),
                                    ft.Text(
                                        info_duree,
                                        size=12,
                                        color=couleur_duree,
                                        weight=ft.FontWeight.BOLD if alerte else ft.FontWeight.NORMAL,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=0,
                            ),
                        ],
                    ),
                    ft.Divider(height=1, color="#E0E0E0"),
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"Début : {c.get('date_debut', '')}",
                                size=11,
                                color=COULEURS["texte_clair"],
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                f"{int(c.get('montant_initial_xaf', 0)):,} FCFA".replace(",", " "),
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=COULEURS["texte"],
                            ),
                        ],
                    ),
                ],
                spacing=8,
            ),
            bgcolor=COULEURS["blanc"],
            border_radius=12,
            padding=15,
            shadow=ft.BoxShadow(
                blur_radius=6,
                color="#1A000000" if not alerte else "#33dc3545",
                offset=ft.Offset(0, 2),
            ),
            border=ft.border.all(1, "#dc3545") if alerte else None,
        )

    def charger_liste(statut=None):
        data = client.get_concessions(statut=statut)
        liste.controls.clear()
        if not data:
            liste.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.icons.DESCRIPTION, size=50, color=COULEURS["texte_clair"]),
                            ft.Text("Aucune concession trouvée", size=15, color=COULEURS["texte_clair"]),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    padding=50,
                )
            )
        else:
            for c in data:
                liste.controls.append(carte_concession(c))

    charger_liste()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Row(
                    controls=[
                        ft.Text("Concessions", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                        ft.Container(expand=True),
                    ],
                ),
                ft.Text("Gestion des contrats de concession funéraire", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=15),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Toutes",
                            bgcolor=COULEURS["primaire"],
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=lambda e: [charger_liste(None), page.update()],
                        ),
                        ft.OutlinedButton(
                            "Actives",
                            style=ft.ButtonStyle(color="#28a745"),
                            on_click=lambda e: [charger_liste("ACTIVE"), page.update()],
                        ),
                        ft.OutlinedButton(
                            "Expirées",
                            style=ft.ButtonStyle(color="#dc3545"),
                            on_click=lambda e: [charger_liste("EXPIREE"), page.update()],
                        ),
                        ft.OutlinedButton(
                            "Résiliées",
                            style=ft.ButtonStyle(color="#6c757d"),
                            on_click=lambda e: [charger_liste("RESILIEE"), page.update()],
                        ),
                    ],
                    spacing=10,
                ),
                ft.Container(height=10),
                liste,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )