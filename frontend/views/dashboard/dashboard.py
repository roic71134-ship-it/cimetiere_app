import flet as ft
from datetime import datetime
from config import COULEURS, APP_NOM, API_BASE_URL


BREAKPOINT_MOBILE = 700

JOURS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def _date_du_jour():
    now = datetime.now()
    return f"{JOURS[now.weekday()]} {now.day} {MOIS[now.month - 1]} {now.year}"


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

    # --- Structure du menu, regroupée par section (plus lisible / plus pro) ---
    sections_nav = [
        {
            "titre": "PRINCIPAL",
            "items": [
                {"icon": ft.icons.DASHBOARD_ROUNDED, "label": "Tableau de bord", "index": 0},
                {"icon": ft.icons.MAP_ROUNDED, "label": "Carte du cimetière", "index": 1},
            ],
        },
        {
            "titre": "GESTION",
            "items": [
                {"icon": ft.icons.BOOK_ROUNDED, "label": "Réservations", "index": 2},
                {"icon": ft.icons.DESCRIPTION_ROUNDED, "label": "Concessions", "index": 3},
                {"icon": ft.icons.PAYMENT_ROUNDED, "label": "Paiements", "index": 4},
                {"icon": ft.icons.INVENTORY_2_ROUNDED, "label": "Exhumations", "index": 6},
                {"icon": ft.icons.TERRAIN_ROUNDED, "label": "Terrain", "index": 8},
            ],
        },
        {
            "titre": "ANALYSE",
            "items": [
                {"icon": ft.icons.BAR_CHART_ROUNDED, "label": "Rapports", "index": 5},
            ],
        },
    ]

    if est_admin:
        sections_nav.append({
            "titre": "ADMINISTRATION",
            "items": [
                {"icon": ft.icons.PEOPLE_ROUNDED, "label": "Utilisateurs", "index": 7},
            ],
        })

    nav_items = [it for sec in sections_nav for it in sec["items"]]

    contenu = ft.Container(content=_vue_accueil(nom_user), expand=True)
    nav_buttons = {}
    titre_page = ft.Text("Tableau de bord", color="white", size=16, weight=ft.FontWeight.W_600)
    sous_titre_page = ft.Text("Vue d'ensemble", color="#FFFFFF99", size=12)

    def afficher_contenu(index):
        for i, btn in nav_buttons.items():
            actif = i == index
            btn.bgcolor = "#FFFFFF26" if actif else "transparent"
            btn.content.controls[0].color = "white" if actif else "#FFFFFFB3"
            btn.content.controls[1].color = "white" if actif else "#FFFFFFB3"
            btn.content.controls[1].weight = ft.FontWeight.W_600 if actif else ft.FontWeight.W_400

        label = next((it["label"] for it in nav_items if it["index"] == index), "")
        titre_page.value = label
        sous_titre_page.value = "Cimetière de France · Pointe-Noire"

        if index == 0:
            contenu.content = _vue_accueil(nom_user)
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

    def construire_bouton(item):
        idx = item["index"]
        actif = idx == 0
        icone = ft.Icon(item["icon"], color="white" if actif else "#FFFFFFB3", size=19)
        texte = ft.Text(
            item["label"], color="white" if actif else "#FFFFFFB3", size=13.5,
            weight=ft.FontWeight.W_600 if actif else ft.FontWeight.W_400,
        )
        btn = ft.Container(
            content=ft.Row(controls=[icone, texte], spacing=13),
            padding=ft.padding.symmetric(horizontal=16, vertical=11),
            margin=ft.margin.symmetric(horizontal=10),
            border_radius=8,
            bgcolor="#FFFFFF26" if actif else "transparent",
            on_click=lambda e, i=idx: afficher_contenu(i),
            ink=True,
            animate=100,
        )
        nav_buttons[idx] = btn
        return btn

    def bloc_section(section):
        controles = [
            ft.Container(
                content=ft.Text(section["titre"], size=10.5, color="#FFFFFF66",
                                 weight=ft.FontWeight.W_700, letter_spacing=0.8),
                padding=ft.padding.only(left=20, top=14, bottom=6),
            )
        ]
        controles += [construire_bouton(it) for it in section["items"]]
        return ft.Column(controls=controles, spacing=1)

    blocs_navigation = [bloc_section(sec) for sec in sections_nav]

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
                        ft.Text(nom_user, color="white", size=13, weight=ft.FontWeight.W_600),
                        ft.Text(role_user, color="#FFFFFFB3", size=11),
                    ],
                    spacing=0,
                ),
            ],
            spacing=10,
        ),
        padding=ft.padding.symmetric(horizontal=15, vertical=12),
    )

    bouton_deconnexion = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.LOGOUT_ROUNDED, color="#FFFFFFB3", size=17),
                ft.Text("Déconnexion", color="#FFFFFFB3", size=13),
            ],
            spacing=10,
        ),
        padding=ft.padding.symmetric(horizontal=15, vertical=10),
        margin=ft.margin.symmetric(horizontal=10, vertical=4),
        on_click=on_logout,
        ink=True,
        border_radius=8,
    )

    en_tete_menu = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.icons.HOME_WORK_ROUNDED, size=22, color="white"),
                    bgcolor="#FFFFFF26",
                    border_radius=10,
                    padding=10,
                ),
                ft.Column(
                    controls=[
                        ft.Text("Cimetière de France", size=13.5, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text("Pointe-Noire", size=11, color="#FFFFFFB3"),
                    ],
                    spacing=0,
                ),
            ],
            spacing=12,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=20),
    )

    # --- Barre supérieure commune (desktop + mobile), pour un rendu plus "app pro" ---
    def barre_superieure(avec_menu_burger=False):
        controles = []
        if avec_menu_burger:
            controles.append(
                ft.IconButton(icon=ft.icons.MENU_ROUNDED, icon_color="white",
                              on_click=lambda e: page.open(page.drawer))
            )
        controles.append(
            ft.Column(controls=[titre_page, sous_titre_page], spacing=0)
        )
        controles.append(ft.Container(expand=True))
        if not avec_menu_burger:
            controles.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.CircleAvatar(
                                content=ft.Text(initiale, size=13, color=COULEURS["primaire"],
                                                 weight=ft.FontWeight.BOLD),
                                bgcolor="white",
                                radius=15,
                            ),
                            ft.Text(nom_user, color="white", size=13),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    bgcolor="#FFFFFF14",
                    border_radius=20,
                )
            )
        controles.append(
            ft.IconButton(icon=ft.icons.LOGOUT_ROUNDED, icon_color="white",
                          tooltip="Déconnexion", on_click=on_logout)
        )
        return ft.Container(
            content=ft.Row(controls=controles, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=COULEURS["primaire"],
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
        )

    if mobile:
        page.drawer = ft.NavigationDrawer(
            controls=[
                en_tete_menu,
                ft.Divider(color="#FFFFFF26", height=1),
                *blocs_navigation,
                ft.Container(expand=True),
                ft.Divider(color="#FFFFFF26", height=1),
                profil_utilisateur,
                bouton_deconnexion,
                ft.Container(height=10),
            ],
            bgcolor=COULEURS["primaire"],
        )

        return ft.Column(
            controls=[barre_superieure(avec_menu_burger=True), contenu],
            expand=True,
            spacing=0,
        )

    # --- Sidebar desktop, sectionnée ---
    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                en_tete_menu,
                ft.Divider(color="#FFFFFF26", height=1),
                ft.Container(
                    content=ft.Column(controls=blocs_navigation, spacing=2, scroll=ft.ScrollMode.AUTO),
                    expand=True,
                ),
                ft.Divider(color="#FFFFFF26", height=1),
                profil_utilisateur,
                bouton_deconnexion,
                ft.Container(height=10),
            ],
            spacing=0,
        ),
        bgcolor=COULEURS["primaire"],
        width=250,
    )

    zone_droite = ft.Column(
        controls=[barre_superieure(), contenu],
        expand=True,
        spacing=0,
    )

    return ft.Row(controls=[sidebar, zone_droite], expand=True, spacing=0)


def _vue_accueil(nom_user="Utilisateur"):
    from api_client import client

    geojson = client.get_caveaux_geojson()
    features = geojson.get("features", [])
    total = len(features)
    disponibles = sum(1 for f in features if f["properties"]["statut"] == "DISPONIBLE")
    occupes = sum(1 for f in features if f["properties"]["statut"] == "OCCUPE")
    reserves = sum(1 for f in features if f["properties"]["statut"] == "RESERVE")
    taux = round((occupes / total * 100), 1) if total > 0 else 0
    prenom = nom_user.strip().split(" ")[0] if nom_user else "Utilisateur"

    def stat_card(titre, valeur, icone, couleur, sous_texte=None):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(icone, color=couleur, size=22),
                                bgcolor=f"{couleur}1F",
                                border_radius=10,
                                padding=11,
                            ),
                            ft.Container(expand=True),
                        ],
                    ),
                    ft.Container(height=14),
                    ft.Text(str(valeur), size=28, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
                    ft.Text(titre, size=13, color=COULEURS["texte_clair"]),
                    ft.Container(height=4) if sous_texte else ft.Container(height=0),
                    ft.Text(sous_texte, size=11.5, color=couleur, weight=ft.FontWeight.W_600) if sous_texte else ft.Container(height=0),
                ],
                spacing=0,
            ),
            bgcolor=COULEURS["blanc"],
            border_radius=14,
            padding=20,
            border=ft.border.all(1, "#00000010"),
            shadow=ft.BoxShadow(blur_radius=10, color="#0A000000", offset=ft.Offset(0, 3)),
            expand=1,
        )

    entete = ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(f"Bonjour, {prenom} 👋", size=23, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                        ft.Text(_date_du_jour(), size=13.5, color=COULEURS["texte_clair"]),
                    ],
                    spacing=3,
                ),
                ft.Container(expand=True),
            ],
        ),
        padding=ft.padding.only(bottom=4),
    )

    carte_repartition = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Taux d'occupation", size=15, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                        ft.Container(expand=True),
                        ft.Text(f"{taux}%", size=15, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                    ],
                ),
                ft.Container(height=14),
                ft.ProgressBar(value=taux / 100, bgcolor="#EDEDED", color=COULEURS["primaire"], height=10, border_radius=6),
                ft.Container(height=10),
                ft.Text(f"{occupes} caveaux occupés sur {total} au total", size=12.5, color=COULEURS["texte_clair"]),
                ft.Container(height=18),
                ft.Row(
                    controls=[
                        _repartition_item("Disponibles", disponibles, total, COULEURS["success"]),
                        _repartition_item("Occupés", occupes, total, COULEURS["danger"]),
                        _repartition_item("Réservés", reserves, total, COULEURS["warning"]),
                    ],
                    spacing=25,
                ),
            ],
        ),
        bgcolor=COULEURS["blanc"],
        border_radius=14,
        padding=22,
        border=ft.border.all(1, "#00000010"),
        shadow=ft.BoxShadow(blur_radius=10, color="#0A000000", offset=ft.Offset(0, 3)),
        expand=2,
    )

    carte_raccourcis = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Accès rapide", size=15, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Container(height=14),
                _raccourci_item(ft.icons.MAP_ROUNDED, "Carte du cimetière", COULEURS["primaire"]),
                _raccourci_item(ft.icons.BOOK_ROUNDED, "Nouvelle réservation", COULEURS["success"]),
                _raccourci_item(ft.icons.PAYMENT_ROUNDED, "Enregistrer un paiement", COULEURS["warning"]),
                _raccourci_item(ft.icons.BAR_CHART_ROUNDED, "Voir les rapports", COULEURS["danger"]),
            ],
            spacing=10,
        ),
        bgcolor=COULEURS["blanc"],
        border_radius=14,
        padding=22,
        border=ft.border.all(1, "#00000010"),
        shadow=ft.BoxShadow(blur_radius=10, color="#0A000000", offset=ft.Offset(0, 3)),
        expand=1,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                entete,
                ft.Container(height=22),
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
                ft.Container(height=18),
                ft.Row(
                    controls=[carte_repartition, carte_raccourcis],
                    spacing=16,
                    wrap=True,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(28),
        expand=True,
        bgcolor=COULEURS["fond"],
    )


def _repartition_item(label, valeur, total, couleur):
    pourcentage = round((valeur / total * 100), 0) if total > 0 else 0
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Container(width=10, height=10, bgcolor=couleur, border_radius=5),
                    ft.Text(label, size=12.5, color=COULEURS["texte_clair"]),
                ],
                spacing=6,
            ),
            ft.Text(f"{valeur}", size=17, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
            ft.Text(f"{pourcentage:.0f}%", size=11.5, color=couleur, weight=ft.FontWeight.W_600),
        ],
        spacing=3,
    )


def _raccourci_item(icone, label, couleur):
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(icone, size=16, color=couleur),
                    bgcolor=f"{couleur}1F",
                    border_radius=8,
                    padding=8,
                ),
                ft.Text(label, size=13, color=COULEURS["texte"], expand=True),
                ft.Icon(ft.icons.CHEVRON_RIGHT_ROUNDED, size=16, color=COULEURS["texte_clair"]),
            ],
            spacing=10,
        ),
        padding=ft.padding.symmetric(horizontal=10, vertical=8),
        border_radius=8,
        ink=True,
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

    entete = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Carte du cimetière", size=23, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Text("Vue géographique des emplacements", size=13.5, color=COULEURS["texte_clair"]),
            ],
            spacing=3,
        ),
    )

    ligne_stats = ft.Row(
        controls=[
            _stat_mini("Total", total, COULEURS["primaire"]),
            _stat_mini("Disponibles", disponibles, "#28a745"),
            _stat_mini("Occupés", occupes, "#dc3545"),
            _stat_mini("Réservés", reserves, "#fd7e14"),
        ],
        spacing=14,
        wrap=True,
    )

    carte_principale = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.icons.MAP_ROUNDED, size=52, color=COULEURS["primaire"]),
                    bgcolor=f"{COULEURS['primaire']}14",
                    border_radius=100,
                    padding=22,
                ),
                ft.Container(height=18),
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
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                    on_click=ouvrir_carte,
                ),
                ft.Container(height=26),
                ft.Divider(color="#00000012", height=1),
                ft.Container(height=18),
                ft.Row(
                    controls=[
                        _legende_item("Disponible", "#28a745"),
                        _legende_item("Réservé", "#fd7e14"),
                        _legende_item("Occupé", "#dc3545"),
                        _legende_item("Non exploitable", "#6c757d"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    wrap=True,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=COULEURS["blanc"],
        border_radius=14,
        padding=40,
        border=ft.border.all(1, "#00000010"),
        shadow=ft.BoxShadow(blur_radius=10, color="#0A000000", offset=ft.Offset(0, 3)),
        alignment=ft.alignment.center,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                entete,
                ft.Container(height=22),
                ligne_stats,
                ft.Container(height=22),
                carte_principale,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(28),
        expand=True,
        bgcolor=COULEURS["fond"],
    )


def _stat_mini(titre, valeur, couleur):
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(width=6, height=36, bgcolor="white", border_radius=3, opacity=0.5),
                ft.Column(
                    controls=[
                        ft.Text(str(valeur), size=22, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text(titre, size=12, color="#FFFFFFD9"),
                    ],
                    spacing=0,
                ),
            ],
            spacing=12,
        ),
        bgcolor=couleur,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=18, vertical=14),
        expand=True,
    )


def _legende_item(label, couleur):
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(width=10, height=10, bgcolor=couleur, border_radius=5),
                ft.Text(label, size=12.5, color=COULEURS["texte"]),
            ],
            spacing=8,
        ),
        bgcolor="#00000006",
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
    )
