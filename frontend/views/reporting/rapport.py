import flet as ft
from config import COULEURS, API_BASE_URL


def vue_reporting(page: ft.Page):
    from api_client import client

    stats = client.get_statistiques()

    if not stats or stats.get("error"):
        return ft.Container(
            content=ft.Text("Erreur de chargement des statistiques.", color=COULEURS["danger"]),
            padding=25,
        )

    caveaux = stats.get("caveaux", {})
    reservations = stats.get("reservations", {})
    finances = stats.get("finances", {})
    paiements_canal = stats.get("paiements_par_canal", [])
    types_concession = stats.get("types_concession", [])

    def stat_card(titre, valeur, soustitre, couleur, icone):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(icone, color="white", size=22),
                                bgcolor=couleur,
                                border_radius=8,
                                padding=10,
                            ),
                            ft.Container(expand=True),
                        ],
                    ),
                    ft.Container(height=10),
                    ft.Text(str(valeur), size=26, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
                    ft.Text(titre, size=13, weight=ft.FontWeight.W_500, color=COULEURS["primaire"]),
                    ft.Text(soustitre, size=11, color=COULEURS["texte_clair"]),
                ],
                spacing=2,
            ),
            bgcolor=COULEURS["blanc"],
            border_radius=12,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=8, color="#1A000000", offset=ft.Offset(0, 2)),
            expand=True,
        )

    def barre_occupation(label, valeur, total, couleur):
        pct = round((valeur / total * 100), 1) if total > 0 else 0
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(label, size=13, color=COULEURS["texte"], expand=True),
                            ft.Text(f"{valeur} ({pct}%)", size=13, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
                        ],
                    ),
                    ft.ProgressBar(
                        value=pct / 100,
                        bgcolor="#E0E0E0",
                        color=couleur,
                        height=8,
                        border_radius=4,
                    ),
                ],
                spacing=5,
            ),
        )

    def ligne_canal(canal_data):
        canal = canal_data.get("canal", "")
        total = canal_data.get("total", 0)
        montant = int(canal_data.get("montant", 0))
        canal_labels = {
            "ESPECES": "Espèces",
            "AIRTEL_MONEY": "Airtel Money",
            "MTN_MOMO": "MTN MoMo",
            "VIREMENT": "Virement",
            "CHEQUE": "Chèque",
        }
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=10,
                        height=10,
                        bgcolor=COULEURS["primaire"],
                        border_radius=5,
                    ),
                    ft.Text(canal_labels.get(canal, canal), size=13, color=COULEURS["texte"], expand=True),
                    ft.Text(f"{total} tx", size=12, color=COULEURS["texte_clair"]),
                    ft.Text(
                        f"{montant:,} FCFA".replace(",", " "),
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=COULEURS["texte"],
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.symmetric(vertical=8),
        )

    def ouvrir_export_reservations(e):
        import webbrowser
        webbrowser.open(f"{API_BASE_URL}/reporting/export/reservations")

    def ouvrir_export_paiements(e):
        import webbrowser
        webbrowser.open(f"{API_BASE_URL}/reporting/export/paiements")

    def ouvrir_export_reservations_excel(e):
        import webbrowser
        webbrowser.open(f"{API_BASE_URL}/reporting/export/reservations-excel")

    def ouvrir_export_paiements_excel(e):
        import webbrowser
        webbrowser.open(f"{API_BASE_URL}/reporting/export/paiements-excel")

    def envoyer_alertes_concessions(e):
        res = client.envoyer_alertes_expiration()
        snack(res.get("message", "Alertes envoyées !"))

    def snack(msg, couleur=None):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=couleur or COULEURS["success"],
        )
        page.snack_bar.open = True
        page.update()    

    total_caveaux = caveaux.get("total", 0)
    taux = caveaux.get("taux_occupation", 0)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Row(
                    controls=[
                        ft.Text("Rapports & Statistiques", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                    ],
                ),
                ft.Container(height=10),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Réservations CSV",
                            icon=ft.icons.DOWNLOAD,
                            bgcolor=COULEURS["primaire"],
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=ouvrir_export_reservations,
                        ),
                        ft.ElevatedButton(
                            "Réservations Excel",
                            icon=ft.icons.TABLE_CHART,
                            bgcolor="#2E7D32",
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=ouvrir_export_reservations_excel,
                        ),
                        ft.ElevatedButton(
                            "Paiements CSV",
                            icon=ft.icons.DOWNLOAD,
                            bgcolor=COULEURS["secondaire"],
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=ouvrir_export_paiements,
                        ),
                        ft.ElevatedButton(
                            "Paiements Excel",
                            icon=ft.icons.TABLE_CHART,
                            bgcolor="#1565C0",
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=ouvrir_export_paiements_excel,
                        ),
                        ft.ElevatedButton(
                            "🔔 Alertes concessions",
                            icon=ft.icons.NOTIFICATIONS,
                            bgcolor="#E65100",
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=envoyer_alertes_concessions,
                        ),
                    ],
                    spacing=10,
                    wrap=True,
                ),
                ft.Text("Vue d'ensemble et exports", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=20),

                # Cartes statistiques
                ft.Row(
                    controls=[
                        stat_card("Total caveaux", total_caveaux, "Inventaire complet", COULEURS["primaire"], ft.icons.GRID_VIEW),
                        stat_card("Taux occupation", f"{taux}%", f"{caveaux.get('occupes', 0)} occupés", COULEURS["danger"], ft.icons.DONUT_LARGE),
                        stat_card("Réservations", reservations.get("total", 0), f"{reservations.get('en_attente', 0)} en attente", COULEURS["warning"], ft.icons.BOOK),
                        stat_card(
                            "Revenus totaux",
                            f"{int(finances.get('total_paye_xaf', 0)):,} FCFA".replace(",", " "),
                            f"Ce mois : {int(finances.get('paiements_mois_xaf', 0)):,} FCFA".replace(",", " "),
                            COULEURS["success"],
                            ft.icons.PAYMENTS,
                        ),
                    ],
                    spacing=15,
                ),
                ft.Container(height=20),

                # Ligne 2 — Occupation + Finances
                ft.Row(
                    controls=[
                        # Occupation des caveaux
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Occupation des caveaux", size=15, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                                    ft.Container(height=15),
                                    barre_occupation("Disponibles", caveaux.get("disponibles", 0), total_caveaux, "#28a745"),
                                    ft.Container(height=8),
                                    barre_occupation("Occupés", caveaux.get("occupes", 0), total_caveaux, "#dc3545"),
                                    ft.Container(height=8),
                                    barre_occupation("Réservés", caveaux.get("reserves", 0), total_caveaux, "#fd7e14"),
                                    ft.Container(height=8),
                                    barre_occupation("Non exploitables", caveaux.get("non_exploitables", 0), total_caveaux, "#6c757d"),
                                ],
                                spacing=0,
                            ),
                            bgcolor=COULEURS["blanc"],
                            border_radius=12,
                            padding=20,
                            shadow=ft.BoxShadow(blur_radius=8, color="#1A000000", offset=ft.Offset(0, 2)),
                            expand=True,
                        ),

                        # Paiements par canal
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Paiements par canal", size=15, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                                    ft.Container(height=10),
                                    *([ligne_canal(c) for c in paiements_canal] if paiements_canal else [
                                        ft.Text("Aucun paiement enregistré", size=13, color=COULEURS["texte_clair"])
                                    ]),
                                ],
                                spacing=0,
                            ),
                            bgcolor=COULEURS["blanc"],
                            border_radius=12,
                            padding=20,
                            shadow=ft.BoxShadow(blur_radius=8, color="#1A000000", offset=ft.Offset(0, 2)),
                            expand=True,
                        ),
                    ],
                    spacing=15,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Container(height=20),

                # Taux d'occupation par bloc
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Occupation par bloc", size=15, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                            ft.Container(height=15),
                            *([
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Row(controls=[
                                                ft.Text(b.get("bloc", ""), size=13, color=COULEURS["texte"], expand=True),
                                                ft.Text(f"{b.get('occupes', 0)}/{b.get('total', 0)} — {b.get('taux_occupation', 0)}%",
                                                    size=13, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
                                            ]),
                                            ft.ProgressBar(
                                                value=b.get("taux_occupation", 0) / 100,
                                                bgcolor="#E0E0E0",
                                                color=COULEURS["primaire"],
                                                height=8,
                                                border_radius=4,
                                            ),
                                        ],
                                        spacing=5,
                                    ),
                                    padding=ft.padding.symmetric(vertical=5),
                                )
                                for b in stats.get("blocs_stats", [])
                            ] if stats.get("blocs_stats") else [
                                ft.Text("Aucun bloc configuré", size=13, color=COULEURS["texte_clair"])
                            ]),
                        ],
                    ),
                    bgcolor=COULEURS["blanc"],
                    border_radius=12,
                    padding=20,
                    shadow=ft.BoxShadow(blur_radius=8, color="#1A000000", offset=ft.Offset(0, 2)),
                ),
                ft.Container(height=20),

                # Réservations par statut
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Réservations par statut", size=15, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                            ft.Container(height=15),
                            ft.Row(
                                controls=[
                                    _mini_stat("Confirmées", reservations.get("confirmees", 0), COULEURS["success"]),
                                    _mini_stat("En attente", reservations.get("en_attente", 0), COULEURS["warning"]),
                                    _mini_stat("Annulées", reservations.get("annulees", 0), COULEURS["danger"]),
                                ],
                                spacing=10,
                            ),
                        ],
                        spacing=0,
                    ),
                    bgcolor=COULEURS["blanc"],
                    border_radius=12,
                    padding=20,
                    shadow=ft.BoxShadow(blur_radius=8, color="#1A000000", offset=ft.Offset(0, 2)),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )


def _mini_stat(label, valeur, couleur):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(str(valeur), size=22, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(label, size=12, color="white"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=3,
        ),
        bgcolor=couleur,
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=25, vertical=15),
        expand=True,
    )