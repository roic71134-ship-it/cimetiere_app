import flet as ft
from config import COULEURS, APP_NOM, API_BASE_URL


BREAKPOINT_MOBILE = 700


def vue_dashboard(page: ft.Page, on_deconnexion):
    from api_client import client

    user = client.get_me()
    nom_user = f"{user.get('prenom', '')} {user.get('nom', '')}" if not user.get('error') else "Utilisateur"
    role_user = user.get('role', {}).get('nom', '') if user.get('role') else ""
    initiale = nom_user[0].upper() if nom_user else "U"

    est_admin = role_user == "ADMIN"
    mobile = (page.width or 1200) < BREAKPOINT_MOBILE

    def on_logout(e):
        client.deconnecter()
        on_deconnexion()

    # Utilisateurs seulement visible pour ADMIN
    nav_items = [
        {"icon": ft.icons.DASHBOARD, "label": "Tableau de bord", "index": 0},
        {"icon": ft.icons.MAP, "label": "Carte du cimetière", "index": 1},
        {"icon": ft.icons.BOOK, "label": "Réservations", "index": 2},
        {"icon": ft.icons.DESCRIPTION, "label": "Concessions", "index": 3},
        {"icon": ft.icons.PAYMENT, "label": "Paiements", "index": 4},
        {"icon": ft.icons.BAR_CHART, "label": "Rapports", "index": 5},
        {"icon": ft.icons.INVENTORY, "label": "Exhumations", "index": 6},
        {"icon": ft.icons.TERRAIN, "label": "Terrain", "index": 8},
    ]

    if est_admin:
        nav_items.insert(4, {"icon": ft.icons.PEOPLE, "label": "Utilisateurs", "index": 7})

    contenu = ft.Container(content=_vue_accueil(), expand=True)
    nav_buttons = []
    titre_page = ft.Text("Tableau de bord", color="white", size=17, weight=ft.FontWeight.BOLD)

    def afficher_contenu(index):
        for i, btn in enumerate(nav_buttons):
            btn.bgcolor = "#FFFFFF1A" if i == index else "transparent"
        label = next((it["label"] for it in nav_items if it["index"] == index), "")
        titre_page.value = label
        if index == 0:
            contenu.content = _vue_accueil()
        elif index == 1:
            contenu.content = _vue_carte(page)
        elif index == 2:
            from views.reservations.liste import vue_reservations
            contenu.content = vue_reservations(page)
        elif index == 3:
            from views.concessions.liste import vue_concessions
            contenu.content = vue_concessions(page)
        elif index == 4:
            from views.paiements.liste import vue_paiements
            contenu.content = vue_paiements(page)
        elif index == 5:
            from views.reporting.rapport import vue_reporting
            contenu.content = vue_reporting(page)
        elif index == 6:
            from views.exhumations.liste import vue_exhumations
            contenu.content = vue_exhumations(page)
        elif index == 7:
            from views.utilisateurs.liste import vue_utilisateurs
            contenu.content = vue_utilisateurs(page)
        elif index == 8:
            from views.terrain.gestion import vue_gestion_terrain
            contenu.content = vue_gestion_terrain(page)
        if mobile:
            page.drawer.open = False
        contenu.update()
        page.update()

    for item in nav_items:
        idx = item["index"]
        btn = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(item["icon"], color="white", size=20),
                    ft.Text(item["label"], color="white", size=14),
                ],
                spacing=15,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=8,
            bgcolor="#FFFFFF1A" if idx == 0 else "transparent",
            on_click=lambda e, i=idx: afficher_contenu(i),
            ink=True,
        )
        nav_buttons.append(btn)

    profil_utilisateur = ft.Container(
        content=ft.Row(
            controls=[
                ft.CircleAvatar(
                    content=ft.Text(initiale, color=COULEURS["primaire"], weight=ft.FontWeight.BOLD),
                    bgcolor="white",
                    radius=18,
                ),
                ft.Column(
                    controls=[
                        ft.Text(nom_user, color="white", size=13, weight=ft.FontWeight.W_500),
                        ft.Text(role_user, color="#FFFFFFB3", size=11),
                    ],
                    spacing=0,
                ),
            ],
            spacing=10,
        ),
        padding=ft.padding.symmetric(horizontal=15, vertical=10),
    )

    bouton_deconnexion = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.LOGOUT, color="#FFFFFFB3", size=18),
                ft.Text("Déconnexion", color="#FFFFFFB3", size=13),
            ],
            spacing=10,
        ),
        padding=ft.padding.symmetric(horizontal=15, vertical=10),
        on_click=on_logout,
        ink=True,
        border_radius=8,
    )

    en_tete_menu = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.icons.HOME_WORK, size=40, color="white"),
                ft.Text("Cimetière Municipal", size=13, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
                ft.Text("Pointe-Noire", size=11, color="#FFFFFFB3", text_align=ft.TextAlign.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(vertical=20),
    )

    if mobile:
        # Menu type "tiroir" pour mobile
        page.drawer = ft.NavigationDrawer(
            controls=[
                en_tete_menu,
                ft.Divider(color="#FFFFFF3D", height=1),
                ft.Container(height=8),
                *nav_buttons,
                ft.Container(height=8),
                ft.Divider(color="#FFFFFF3D", height=1),
                profil_utilisateur,
                bouton_deconnexion,
                ft.Container(height=10),
            ],
            bgcolor=COULEURS["primaire"],
        )

        barre_haut = ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.icons.MENU,
                        icon_color="white",
                        on_click=lambda e: page.open(page.drawer),
                    ),
                    titre_page,
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.icons.LOGOUT,
                        icon_color="white",
                        tooltip="Déconnexion",
                        on_click=on_logout,
                    ),
                ],
            ),
            bgcolor=COULEURS["primaire"],
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
        )

        return ft.Column(
            controls=[barre_haut, contenu],
            expand=True,
            spacing=0,
        )

    # Sidebar classique pour desktop
    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                en_tete_menu,
                ft.Divider(color="#FFFFFF3D", height=1),
                ft.Container(height=8),
                *nav_buttons,
                ft.Container(expand=True),
                ft.Divider(color="#FFFFFF3D", height=1),
                profil_utilisateur,
                bouton_deconnexion,
                ft.Container(height=10),
            ],
            spacing=2,
        ),
        bgcolor=COULEURS["primaire"],
        width=230,
        padding=ft.padding.symmetric(horizontal=10),
    )

    return ft.Row(controls=[sidebar, contenu], expand=True, spacing=0)


def _vue_accueil():
    from api_client import client

    geojson = client.get_caveaux_geojson()
    features = geojson.get("features", [])
    total = len(features)
    disponibles = sum(1 for f in features if f["properties"]["statut"] == "DISPONIBLE")
    occupes = sum(1 for f in features if f["properties"]["statut"] == "OCCUPE")
    reserves = sum(1 for f in features if f["properties"]["statut"] == "RESERVE")
    taux = round((occupes / total * 100), 1) if total > 0 else 0

    def stat_card(titre, valeur, icone, couleur):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(icone, color="white", size=24),
                                bgcolor=couleur,
                                border_radius=10,
                                padding=10,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(str(valeur), size=28, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
                                    ft.Text(titre, size=13, color=COULEURS["texte_clair"]),
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=15,
                    ),
                ],
            ),
            bgcolor=COULEURS["blanc"],
            border_radius=12,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=8, color="#1A000000", offset=ft.Offset(0, 2)),
            width=220,
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Text("Tableau de bord", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Text("Vue d'ensemble du cimetière", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=20),
                ft.Row(
                    controls=[
                        stat_card("Total caveaux", total, ft.icons.GRID_VIEW, COULEURS["primaire"]),
                        stat_card("Disponibles", disponibles, ft.icons.CHECK_CIRCLE, COULEURS["success"]),
                        stat_card("Occupés", occupes, ft.icons.CANCEL, COULEURS["danger"]),
                        stat_card("Réservés", reserves, ft.icons.PENDING, COULEURS["warning"]),
                    ],
                    spacing=15,
                    wrap=True,
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Taux d'occupation", size=16, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                            ft.Container(height=10),
                            ft.ProgressBar(value=taux / 100, bgcolor="#E0E0E0", color=COULEURS["primaire"], height=12, border_radius=6),
                            ft.Container(height=5),
                            ft.Text(f"{taux}% des caveaux sont occupés", size=13, color=COULEURS["texte_clair"]),
                        ],
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


def _vue_carte(page):
    from api_client import client

    geojson = client.get_caveaux_geojson()
    total = geojson.get("total", 0)
    features = geojson.get("features", [])
    disponibles = sum(1 for f in features if f["properties"]["statut"] == "DISPONIBLE")
    occupes = sum(1 for f in features if f["properties"]["statut"] == "OCCUPE")
    reserves = sum(1 for f in features if f["properties"]["statut"] == "RESERVE")

    def ouvrir_carte(e):
        base = API_BASE_URL.replace("/api/v1", "")
        page.launch_url(f"{base}/carte/")

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Text("Carte du cimetière", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Text("Vue géographique des emplacements", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=20),
                ft.Row(
                    controls=[
                        _stat_mini("Total", total, "#1B4F72"),
                        _stat_mini("Disponibles", disponibles, "#28a745"),
                        _stat_mini("Occupés", occupes, "#dc3545"),
                        _stat_mini("Réservés", reserves, "#fd7e14"),
                    ],
                    spacing=15,
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.icons.MAP, size=60, color=COULEURS["primaire"]),
                            ft.Container(height=15),
                            ft.Text("Carte interactive Leaflet", size=18, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                            ft.Container(height=8),
                            ft.Text(
                                "Visualisez tous les caveaux géolocalisés.\nCliquez sur chaque emplacement pour voir ses détails.",
                                size=13,
                                color=COULEURS["texte_clair"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=25),
                            ft.ElevatedButton(
                                text="Ouvrir la carte interactive",
                                icon=ft.icons.OPEN_IN_NEW,
                                bgcolor=COULEURS["primaire"],
                                color="white",
                                height=45,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                on_click=ouvrir_carte,
                            ),
                            ft.Container(height=25),
                            ft.Row(
                                controls=[
                                    _legende_item("Disponible", "#28a745"),
                                    _legende_item("Réservé", "#fd7e14"),
                                    _legende_item("Occupé", "#dc3545"),
                                    _legende_item("Non exploitable", "#6c757d"),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=20,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=COULEURS["blanc"],
                    border_radius=12,
                    padding=40,
                    shadow=ft.BoxShadow(blur_radius=8, color="#1A000000", offset=ft.Offset(0, 2)),
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
                ft.Text(str(valeur), size=24, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(titre, size=12, color="white"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
        bgcolor=couleur,
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=20, vertical=15),
        expand=True,
    )


def _legende_item(label, couleur):
    return ft.Row(
        controls=[
            ft.Container(width=14, height=14, bgcolor=couleur, border_radius=7),
            ft.Text(label, size=13, color=COULEURS["texte"]),
        ],
        spacing=8,
    )