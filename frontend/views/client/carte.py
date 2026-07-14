import flet as ft
from config import COULEURS, API_BASE_URL
import webbrowser


def vue_carte_client(page: ft.Page, client):
    geojson = client.get_caveaux_geojson()
    features = geojson.get("features", [])
    disponibles = sum(1 for f in features if f["properties"]["statut"] == "DISPONIBLE")
    total = len(features)

    def ouvrir_carte(e):
        token = client.access_token or ""
        base = API_BASE_URL.replace("/api/v1", "")
        page.launch_url(f"{base}/carte/?token={token}")
        
    def afficher_formulaire_reservation(e):
        from views.reservations.formulaire import vue_formulaire_reservation

        def on_success(result):
            page.dialog.open = False
            page.update()
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"✅ Réservation {result.get('numero')} soumise ! Vous recevrez un email de confirmation.", color="white"),
                bgcolor=COULEURS["success"],
                duration=5000,
            )
            page.snack_bar.open = True
            page.update()

        def on_cancel():
            page.dialog.open = False
            page.update()

        mobile = (page.width or 1200) < 700
        largeur_dialog = (page.width - 20) if mobile else 700
        hauteur_dialog = (page.height - 100) if mobile else 500

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nouvelle réservation", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=vue_formulaire_reservation(page, on_success, on_cancel),
                width=largeur_dialog,
                height=hauteur_dialog,
            ),
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=25),
                ft.Text("Carte du cimetière", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Text("Consultez les emplacements disponibles et réservez en ligne", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=20),
                ft.Row(
                    controls=[
                        _stat_mini("Total caveaux", total, COULEURS["primaire"]),
                        _stat_mini("Disponibles", disponibles, "#28a745"),
                        _stat_mini("Réservés/Occupés", total - disponibles, "#dc3545"),
                    ],
                    spacing=15,
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.icons.MAP, color=COULEURS["primaire"], size=30),
                                    ft.Column(
                                        controls=[
                                            ft.Text("Carte interactive", size=18, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                                            ft.Text("Cliquez sur un caveau vert pour voir ses détails et le réserver", size=13, color=COULEURS["texte_clair"]),
                                        ],
                                        spacing=2,
                                        expand=True,
                                    ),
                                ],
                                spacing=15,
                            ),
                            ft.Container(height=15),
                            ft.Row(
                                controls=[
                                    _legende("Disponible", "#28a745"),
                                    _legende("Réservé", "#fd7e14"),
                                    _legende("Occupé", "#dc3545"),
                                    _legende("Non exploitable", "#6c757d"),
                                ],
                                spacing=20,
                            ),
                            ft.Container(height=20),
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton(
                                        text="Ouvrir la carte interactive",
                                        icon=ft.icons.OPEN_IN_NEW,
                                        bgcolor=COULEURS["primaire"],
                                        color="white",
                                        height=48,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                        on_click=ouvrir_carte,
                                        expand=True,
                                    ),
                                    ft.ElevatedButton(
                                        text="Réserver un caveau",
                                        icon=ft.icons.ADD,
                                        bgcolor="#28a745",
                                        color="white",
                                        height=48,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                        on_click=afficher_formulaire_reservation,
                                        expand=True,
                                    ),
                                ],
                                spacing=15,
                            ),
                        ],
                    ),
                    bgcolor="white",
                    border_radius=16,
                    padding=25,
                    shadow=ft.BoxShadow(blur_radius=10, color="#0D000000", offset=ft.Offset(0, 3)),
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.icons.INFO, color="#2E86C1", size=20),
                            ft.Text(
                                "Après soumission, votre demande sera examinée par l'administration. Vous recevrez une confirmation par email.",
                                size=13,
                                color=COULEURS["texte"],
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor="#EBF5FB",
                    border_radius=10,
                    padding=15,
                    border=ft.border.all(1, "#AED6F1"),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )


def _stat_mini(titre, valeur, couleur):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(str(valeur), size=26, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(titre, size=12, color="white"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=3,
        ),
        bgcolor=couleur,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=20, vertical=15),
        expand=True,
    )


def _legende(label, couleur):
    return ft.Row(
        controls=[
            ft.Container(width=12, height=12, bgcolor=couleur, border_radius=6),
            ft.Text(label, size=12, color=COULEURS["texte"]),
        ],
        spacing=6,
    )