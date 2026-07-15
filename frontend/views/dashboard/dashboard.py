import flet as ft
from config import COULEURS, APP_NOM, API_BASE_URL


BREAKPOINT_MOBILE = 700

# --- Tokens de design (dérivés de COULEURS + un accent institutionnel) ---
ACCENT = "#C9A227"          # bronze/or discret — évoque le sceau officiel
BORDURE = "#E7E9EE"         # bordure fine des cartes
SURFACE = "#F6F7FA"         # fond général, gris très clair
OMBRE = ft.BoxShadow(blur_radius=18, spread_radius=-6, color="#14000000", offset=ft.Offset(0, 6))
RAYON = 14


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

    nav_items = [
        {"icon": ft.icons.DASHBOARD_ROUNDED, "label": "Tableau de bord", "sous_titre": "Vue d'ensemble du cimetière", "index": 0},
        {"icon": ft.icons.MAP_ROUNDED, "label": "Carte du cimetière", "sous_titre": "Vue géographique des emplacements", "index": 1},
        {"icon": ft.icons.BOOK_ROUNDED, "label": "Réservations", "sous_titre": "Suivi des réservations en cours", "index": 2},
        {"icon": ft.icons.DESCRIPTION_ROUNDED, "label": "Concessions", "sous_titre": "Registre des concessions", "index": 3},
        {"icon": ft.icons.PAYMENT_ROUNDED, "label": "Paiements", "sous_titre": "Historique et suivi des paiements", "index": 4},
        {"icon": ft.icons.BAR_CHART_ROUNDED, "label": "Rapports", "sous_titre": "Statistiques et exports", "index": 5},
        {"icon": ft.icons.INVENTORY_ROUNDED, "label": "Exhumations", "sous_titre": "Dossiers d'exhumation", "index": 6},
        {"icon": ft.icons.TERRAIN_ROUNDED, "label": "Terrain", "sous_titre": "Gestion des parcelles", "index": 8},
    ]

    if est_admin:
        nav_items.insert(4, {"icon": ft.icons.PEOPLE_ROUNDED, "label": "Utilisateurs", "sous_titre": "Gestion des comptes utilisateurs", "index": 7})

    contenu = ft.Container(content=_vue_accueil(), expand=True)
    nav_buttons = []
    titre_page = ft.Text(
        "Tableau de bord",
        color="white" if mobile else COULEURS["titre"],
        size=17 if mobile else 20,
        weight=ft.FontWeight.BOLD,
    )
    sous_titre_page = ft.Text("Vue d'ensemble du cimetière", color=COULEURS["texte_clair"], size=13)
    liseres = []  # liseré latéral d'état actif, un par item

    def afficher_contenu(index):
        for i, (btn, liserer) in enumerate(zip(nav_buttons, liseres)):
            actif = i == index
            btn.bgcolor = "#FFFFFF14" if actif else "transparent"
            liserer.bgcolor = ACCENT if actif else "transparent"
        item = next((it for it in nav_items if it["index"] == index), None)
        if item:
            titre_page.value = item["label"]
            sous_titre_page.value = item["sous_titre"]

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
        liserer = ft.Container(width=3, height=36, bgcolor=ACCENT if idx == 0 else "transparent", border_radius=2)
        liseres.append(liserer)
        btn = ft.Container(
            content=ft.Row(
                controls=[
                    liserer,
                    ft.Container(width=8),
                    ft.Icon(item["icon"], color="white", size=19),
                    ft.Text(item["label"], color="white", size=14, weight=ft.FontWeight.W_500),
                ],
                spacing=13,
            ),
            padding=ft.padding.only(left=8, right=16, top=11, bottom=11),
            border_radius=10,
            bgcolor="#FFFFFF14" if idx == 0 else "transparent",
            on_click=lambda e, i=idx: afficher_contenu(i),
            ink=True,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )
        nav_buttons.append(btn)

    profil_utilisateur = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(initiale, color=COULEURS["primaire"], weight=ft.FontWeight.BOLD, size=15),
                    bgcolor="white",
                    width=38,
                    height=38,
                    border_radius=19,
                    alignment=ft.alignment.center,
                ),
                ft.Column(
                    controls=[
                        ft.Text(nom_user, color="white", size=13, weight=ft.FontWeight.W_600),
                        ft.Text(role_user, color="#FFFFFFB3", size=11),
                    ],
                    spacing=1,
                ),
            ],
            spacing=11,
        ),
        padding=ft.padding.symmetric(horizontal=14, vertical=10),
        bgcolor="#FFFFFF0D",
        border_radius=10,
        margin=ft.margin.symmetric(horizontal=8),
    )

    bouton_deconnexion = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.LOGOUT_ROUNDED, color="#FFFFFFB3", size=17),
                ft.Text("Déconnexion", color="#FFFFFFB3", size=13, weight=ft.FontWeight.W_500),
            ],
            spacing=11,
        ),
        padding=ft.padding.symmetric(horizontal=22, vertical=10),
        on_click=on_logout,
        ink=True,
        border_radius=10,
    )

    # Badge "sceau" — cercle à double liseré autour du pictogramme institutionnel
    sceau = ft.Container(
        content=ft.Container(
            content=ft.Icon(ft.icons.HOME_WORK_ROUNDED, size=26, color="white"),
            width=52,
            height=52,
            border_radius=26,
            alignment=ft.alignment.center,
            border=ft.border.all(1.5, "#FFFFFF40"),
        ),
        width=64,
        height=64,
        border_radius=32,
        alignment=ft.alignment.center,
        border=ft.border.all(1, ACCENT),
        padding=6,
    )

    en_tete_menu = ft.Container(
        content=ft.Column(
            controls=[
                sceau,
                ft.Container(height=12),
                ft.Text("Cimetière Municipal", size=13, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
                ft.Text("POINTE-NOIRE", size=10, color=ACCENT, text_align=ft.TextAlign.CENTER,
                        style=ft.TextStyle(letter_spacing=1.5)),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(vertical=26),
    )

    if mobile:
        page.drawer = ft.NavigationDrawer(
            controls=[
                en_tete_menu,
                ft.Divider(color="#FFFFFF26", height=1),
                ft.Container(height=10),
                *nav_buttons,
                ft.Container(height=8),
                ft.Divider(color="#FFFFFF26", height=1),
                ft.Container(height=10),
                profil_utilisateur,
                ft.Container(height=4),
                bouton_deconnexion,
                ft.Container(height=10),
            ],
            bgcolor=COULEURS["primaire"],
        )

        barre_haut = ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.icons.MENU_ROUNDED,
                        icon_color="white",
                        on_click=lambda e: page.open(page.drawer),
                    ),
                    titre_page,
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.icons.LOGOUT_ROUNDED,
                        icon_color="white",
                        tooltip="Déconnexion",
                        on_click=on_logout,
                    ),
                ],
            ),
            bgcolor=COULEURS["primaire"],
            padding=ft.padding.symmetric(horizontal=6, vertical=4),
        )

        return ft.Column(
            controls=[barre_haut, contenu],
            expand=True,
            spacing=0,
            bgcolor=SURFACE,
        )

    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                en_tete_menu,
                ft.Divider(color="#FFFFFF26", height=1),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column(controls=nav_buttons, spacing=2),
                    padding=ft.padding.symmetric(horizontal=6),
                ),
                ft.Container(expand=True),
                ft.Divider(color="#FFFFFF26", height=1),
                ft.Container(height=10),
                profil_utilisateur,
                ft.Container(height=4),
                bouton_deconnexion,
                ft.Container(height=14),
            ],
            spacing=2,
        ),
        bgcolor=COULEURS["primaire"],
        width=248,
    )

    barre_titre_desktop = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[titre_page, sous_titre_page],
                    spacing=2,
                ),
            ],
        ),
        padding=ft.padding.symmetric(horizontal=32, vertical=20),
        bgcolor=COULEURS["blanc"],
        border=ft.border.only(bottom=ft.BorderSide(1, BORDURE)),
    )

    zone_contenu = ft.Column(
        controls=[barre_titre_desktop, ft.Container(content=contenu, expand=True)],
        expand=True,
        spacing=0,
    )

    return ft.Row(controls=[sidebar, zone_contenu], expand=True, spacing=0, bgcolor=SURFACE)


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
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(icone, color=couleur, size=22),
                        bgcolor=f"{couleur}1A",
                        border_radius=12,
                        padding=12,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(str(valeur), size=26, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
                            ft.Text(titre, size=12.5, color=COULEURS["texte_clair"]),
                        ],
                        spacing=0,
                    ),
                ],
                spacing=15,
            ),
            bgcolor=COULEURS["blanc"],
            border_radius=RAYON,
            border=ft.border.all(1, BORDURE),
            padding=ft.padding.symmetric(horizontal=18, vertical=18),
            shadow=OMBRE,
            width=225,
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=6),
                ft.Row(
                    controls=[
                        stat_card("Total caveaux", total, ft.icons.GRID_VIEW_ROUNDED, COULEURS["primaire"]),
                        stat_card("Disponibles", disponibles, ft.icons.CHECK_CIRCLE_ROUNDED, COULEURS["success"]),
                        stat_card("Occupés", occupes, ft.icons.CANCEL_ROUNDED, COULEURS["danger"]),
                        stat_card("Réservés", reserves, ft.icons.PENDING_ROUNDED, COULEURS["warning"]),
                    ],
                    spacing=16,
                    wrap=True,
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.icons.INSIGHTS_ROUNDED, color=COULEURS["primaire"], size=19),
                                    ft.Text("Taux d'occupation", size=15.5, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                                ],
                                spacing=8,
                            ),
                            ft.Container(height=14),
                            ft.ProgressBar(value=taux / 100, bgcolor=SURFACE, color=COULEURS["primaire"], height=10, border_radius=6),
                            ft.Container(height=6),
                            ft.Text(f"{taux}% des caveaux sont occupés", size=13, color=COULEURS["texte_clair"]),
                        ],
                    ),
                    bgcolor=COULEURS["blanc"],
                    border_radius=RAYON,
                    border=ft.border.all(1, BORDURE),
                    padding=22,
                    shadow=OMBRE,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(28),
        expand=True,
        bgcolor=SURFACE,
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
                ft.Container(height=6),
                ft.Row(
                    controls=[
                        _stat_mini("Total", total, COULEURS["primaire"]),
                        _stat_mini("Disponibles", disponibles, COULEURS["success"]),
                        _stat_mini("Occupés", occupes, COULEURS["danger"]),
                        _stat_mini("Réservés", reserves, COULEURS["warning"]),
                    ],
                    spacing=16,
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.icons.MAP_ROUNDED, size=42, color=COULEURS["primaire"]),
                                bgcolor=f"{COULEURS['primaire']}1A",
                                border_radius=18,
                                padding=18,
                            ),
                            ft.Container(height=16),
                            ft.Text("Carte interactive Leaflet", size=18, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                            ft.Container(height=8),
                            ft.Text(
                                "Visualisez tous les caveaux géolocalisés.\nCliquez sur chaque emplacement pour voir ses détails.",
                                size=13,
                                color=COULEURS["texte_clair"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=26),
                            ft.ElevatedButton(
                                text="Ouvrir la carte interactive",
                                icon=ft.icons.OPEN_IN_NEW_ROUNDED,
                                bgcolor=COULEURS["primaire"],
                                color="white",
                                height=46,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=0,
                                ),
                                on_click=ouvrir_carte,
                            ),
                            ft.Container(height=26),
                            ft.Row(
                                controls=[
                                    _legende_item("Disponible", COULEURS["success"]),
                                    _legende_item("Réservé", COULEURS["warning"]),
                                    _legende_item("Occupé", COULEURS["danger"]),
                                    _legende_item("Non exploitable", "#6c757d"),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=22,
                                wrap=True,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor=COULEURS["blanc"],
                    border_radius=RAYON,
                    border=ft.border.all(1, BORDURE),
                    padding=42,
                    shadow=OMBRE,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(28),
        expand=True,
        bgcolor=SURFACE,
    )


def _stat_mini(titre, valeur, couleur):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(str(valeur), size=23, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(titre, size=12, color="#FFFFFFD9"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=3,
        ),
        bgcolor=couleur,
        border_radius=RAYON,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
        expand=True,
    )


def _legende_item(label, couleur):
    return ft.Row(
        controls=[
            ft.Container(width=12, height=12, bgcolor=couleur, border_radius=4),
            ft.Text(label, size=13, color=COULEURS["texte"]),
        ],
        spacing=8,
    )
