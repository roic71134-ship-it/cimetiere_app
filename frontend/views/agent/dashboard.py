import flet as ft
from config import COULEURS, API_BASE_URL
import webbrowser

BREAKPOINT_MOBILE = 700


def vue_dashboard_agent(page: ft.Page, on_deconnexion):
    from api_client import client

    user = client.get_me()
    nom_user = f"{user.get('prenom', '')} {user.get('nom', '')}" if not user.get('error') else "Agent"
    initiale = nom_user[0].upper() if nom_user else "A"
    mobile = (page.width or 1200) < BREAKPOINT_MOBILE

    nav_items = [
        {"icon": ft.icons.DASHBOARD, "label": "Tableau de bord", "index": 0},
        {"icon": ft.icons.MAP, "label": "Carte du cimetière", "index": 1},
        {"icon": ft.icons.GRID_VIEW, "label": "Gestion caveaux", "index": 2},
        {"icon": ft.icons.INVENTORY, "label": "Exhumations", "index": 3},
    ]

    contenu = ft.Container(content=_accueil_agent(user, client), expand=True)
    nav_buttons = []
    titre_page = ft.Text("Tableau de bord", color="white", size=17, weight=ft.FontWeight.BOLD)

    def afficher_contenu(index):
        for i, btn in enumerate(nav_buttons):
            btn.bgcolor = "#FFFFFF1A" if i == index else "transparent"
        label = next((it["label"] for it in nav_items if it["index"] == index), "")
        titre_page.value = label
        if index == 0:
            contenu.content = _accueil_agent(user, client)
        elif index == 1:
            contenu.content = _carte_agent(page)
        elif index == 2:
            contenu.content = _gestion_caveaux(page, client)
        elif index == 3:
            from views.exhumations.liste import vue_exhumations
            contenu.content = vue_exhumations(page)
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

    en_tete_menu = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.icons.HOME_WORK, size=40, color="white"),
                ft.Text("Cimetière Municipal", size=13, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
                ft.Text("Pointe-Noire", size=11, color="#FFFFFFB3", text_align=ft.TextAlign.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(vertical=25),
    )

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
                        ft.Text("Agent terrain", color="#FFFFFFB3", size=11),
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
        on_click=lambda e: on_deconnexion(),
        ink=True,
        border_radius=8,
    )

    if mobile:
        page.drawer = ft.NavigationDrawer(
            controls=[
                en_tete_menu,
                ft.Divider(color="#FFFFFF3D", height=1),
                ft.Container(height=10),
                *nav_buttons,
                ft.Container(height=10),
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
                    ft.IconButton(icon=ft.icons.MENU, icon_color="white", on_click=lambda e: page.open(page.drawer)),
                    titre_page,
                    ft.Container(expand=True),
                    ft.IconButton(icon=ft.icons.LOGOUT, icon_color="white", tooltip="Déconnexion", on_click=lambda e: on_deconnexion()),
                ],
            ),
            bgcolor=COULEURS["primaire"],
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
        )

        return ft.Column(controls=[barre_haut, contenu], expand=True, spacing=0)

    sidebar = ft.Container(
        content=ft.Column(
            controls=[
                en_tete_menu,
                ft.Divider(color="#FFFFFF3D", height=1),
                ft.Container(height=10),
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


def _accueil_agent(user, client):
    nom = user.get("prenom", "")
    geojson = client.get_caveaux_geojson()
    features = geojson.get("features", [])
    total = len(features)
    disponibles = sum(1 for f in features if f["properties"]["statut"] == "DISPONIBLE")
    occupes = sum(1 for f in features if f["properties"]["statut"] == "OCCUPE")
    reserves = sum(1 for f in features if f["properties"]["statut"] == "RESERVE")

    def stat(titre, valeur, couleur, icone):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(content=ft.Icon(icone, color="white", size=24), bgcolor=couleur, border_radius=10, padding=12, width=50, height=50),
                    ft.Container(height=10),
                    ft.Text(str(valeur), size=28, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
                    ft.Text(titre, size=13, color=COULEURS["texte_clair"]),
                ],
                spacing=2,
            ),
            bgcolor="white",
            border_radius=14,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=8, color="#0D000000", offset=ft.Offset(0, 2)),
            width=220,
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=25),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(f"Bonjour, {nom} 👷", size=24, weight=ft.FontWeight.BOLD, color="white"),
                                    ft.Text("Interface agent de terrain", size=13, color="#FFFFFFCC"),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                        ],
                    ),
                    bgcolor=COULEURS["secondaire"],
                    border_radius=16,
                    padding=ft.padding.symmetric(horizontal=25, vertical=20),
                ),
                ft.Container(height=25),
                ft.Text("État du cimetière", size=18, weight=ft.FontWeight.BOLD, color=COULEURS["blanc"]),
                ft.Container(height=12),
                ft.Row(
                    controls=[
                        stat("Total caveaux", total, COULEURS["primaire"], ft.icons.GRID_VIEW),
                        stat("Disponibles", disponibles, "#28a745", ft.icons.CHECK_CIRCLE),
                        stat("Occupés", occupes, "#dc3545", ft.icons.CANCEL),
                        stat("Réservés", reserves, "#fd7e14", ft.icons.PENDING),
                    ],
                    spacing=15,
                    wrap=True,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )


def _carte_agent(page):
    def ouvrir_carte(e):
        base = API_BASE_URL.replace("/api/v1", "")
        page.launch_url(f"{base}/carte/")
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=25),
                ft.Text("Carte du cimetière", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.icons.MAP, size=60, color=COULEURS["primaire"]),
                            ft.Container(height=15),
                            ft.Text("Carte interactive", size=18, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                            ft.Container(height=20),
                            ft.ElevatedButton(
                                text="Ouvrir la carte",
                                icon=ft.icons.OPEN_IN_NEW,
                                bgcolor=COULEURS["primaire"],
                                color="white",
                                height=48,
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                on_click=ouvrir_carte,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor="white",
                    border_radius=16,
                    padding=40,
                    shadow=ft.BoxShadow(blur_radius=8, color="#0D000000", offset=ft.Offset(0, 2)),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )


def _gestion_caveaux(page, client):
    geojson = client.get_caveaux_geojson()
    features = geojson.get("features", [])

    liste = ft.Column(spacing=10)

    STATUT_COULEURS = {
        "DISPONIBLE": "#28a745",
        "RESERVE": "#fd7e14",
        "OCCUPE": "#dc3545",
        "NON_EXPLOITABLE": "#6c757d",
        "MAINTENANCE": "#ffc107",
    }

    STATUT_LABELS = {
        "DISPONIBLE": "Disponible",
        "RESERVE": "Réservé",
        "OCCUPE": "Occupé",
        "NON_EXPLOITABLE": "Non exploitable",
        "MAINTENANCE": "Maintenance",
    }

    def snack(msg, couleur=None):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=couleur or "#28a745",
        )
        page.snack_bar.open = True
        page.update()

    def ouvrir_changement_statut(props):
        cid = props.get("id")
        statut_actuel = props.get("statut", "")

        nouveau_statut = ft.Dropdown(
            label="Nouveau statut",
            value=statut_actuel,
            border_radius=8,
            expand=True,
            options=[
                ft.dropdown.Option("DISPONIBLE", "✅ Disponible"),
                ft.dropdown.Option("MAINTENANCE", "🔧 Maintenance"),
                ft.dropdown.Option("NON_EXPLOITABLE", "⛔ Non exploitable"),
            ],
        )

        def confirmer(e):
            dlg.open = False
            page.update()
            res = client.changer_statut_caveau(cid, nouveau_statut.value)
            if res.get("message"):
                snack(f"✅ {res['message']}")
            else:
                snack(res.get("error", "Erreur"), "#dc3545")
            nouvelle_vue = _gestion_caveaux(page, client)
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Changer le statut", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=400,
                content=ft.Column(tight=True, spacing=10, controls=[
                    ft.Text(f"Caveau : {props.get('reference', '')}", size=13, color=COULEURS["texte_clair"]),
                    ft.Text(f"Statut actuel : {STATUT_LABELS.get(statut_actuel, statut_actuel)}", size=13),
                    ft.Container(height=5),
                    nouveau_statut,
                ]),
            ),
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                ft.ElevatedButton(
                    "Confirmer",
                    bgcolor=COULEURS["primaire"], color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=confirmer,
                ),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    for f in features:
        props = f["properties"]
        statut = props.get("statut", "")

        liste.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            width=14, height=14,
                            bgcolor=STATUT_COULEURS.get(statut, "#6c757d"),
                            border_radius=7,
                        ),
                        ft.Text(props.get("reference", "NON"), size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                        ft.Text(props.get("bloc", ""), size=12, color=ft.colors.GREY),
                        ft.Container(
                            content=ft.Text(STATUT_LABELS.get(statut, statut), size=11, color="white"),
                            bgcolor=STATUT_COULEURS.get(statut, "#6c757d"),
                            border_radius=20,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        ),
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            icon_color=COULEURS["primaire"],
                            tooltip="Changer le statut",
                            on_click=lambda e, p=props: ouvrir_changement_statut(p),
                        ),
                    ],
                    spacing=12,
                    wrap=True,
                ),
                bgcolor="white",
                border_radius=10,
                padding=14,
                shadow=ft.BoxShadow(blur_radius=4, color="#0D000000", offset=ft.Offset(0, 1)),
            )
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=25),
                ft.Text("Gestion des caveaux", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                ft.Text("Inventaire et mise à jour des statuts", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=20),
                liste,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor="#F5F5F5",
    )