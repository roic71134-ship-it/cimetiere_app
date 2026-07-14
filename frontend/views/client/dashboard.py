import flet as ft
from config import COULEURS, APP_NOM

BREAKPOINT_MOBILE = 700


def vue_dashboard_client(page: ft.Page, on_deconnexion, caveau_id=None):
    from api_client import client

    user = client.get_me()
    nom_user = f"{user.get('prenom', '')} {user.get('nom', '')}" if not user.get('error') else "Client"
    initiale = nom_user[0].upper() if nom_user else "C"
    mobile = (page.width or 1200) < BREAKPOINT_MOBILE

    nav_items = [
        {"icon": ft.icons.DASHBOARD, "label": "Accueil", "index": 0},
        {"icon": ft.icons.MAP, "label": "Carte & Réserver", "index": 1},
        {"icon": ft.icons.BOOK, "label": "Mes réservations", "index": 2},
        {"icon": ft.icons.DESCRIPTION, "label": "Mes concessions", "index": 3},
        {"icon": ft.icons.PAYMENT, "label": "Mes paiements", "index": 4},
    ]

    contenu = ft.Container(content=_accueil_client(user), expand=True)
    nav_buttons = []
    titre_page = ft.Text("Accueil", color="white", size=17, weight=ft.FontWeight.BOLD)

    def afficher_contenu(index):
        for i, btn in enumerate(nav_buttons):
            btn.bgcolor = "#FFFFFF1A" if i == index else "transparent"
        label = next((it["label"] for it in nav_items if it["index"] == index), "")
        titre_page.value = label
        if index == 0:
            contenu.content = _accueil_client(user)
        elif index == 1:
            contenu.content = _carte_et_reserver(page, client)
        elif index == 2:
            contenu.content = _mes_reservations(page, client)
        elif index == 3:
            contenu.content = _mes_concessions(page, client)
        elif index == 4:
            contenu.content = _mes_paiements(page, client)
        if mobile and page.drawer:
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
                        ft.Text("Client", color="#FFFFFFB3", size=11),
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

        vue = ft.Column(controls=[barre_haut, contenu], expand=True, spacing=0)
    else:
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

        vue = ft.Row(controls=[sidebar, contenu], expand=True, spacing=0)

    # Si on vient de la carte avec un caveau pré-sélectionné
    if caveau_id:
        afficher_contenu(1)

        def ouvrir_formulaire_caveau():
            from views.reservations.formulaire import vue_formulaire_reservation

            def on_success(result):
                page.dialog.open = False
                page.update()
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Réservation {result.get('numero')} soumise !", color="white"),
                    bgcolor=COULEURS["success"],
                    duration=5000,
                )
                page.snack_bar.open = True
                page.update()

            def on_cancel():
                page.dialog.open = False
                page.update()

            mobile_dlg = (page.width or 1200) < 700
            largeur_dlg = (page.width - 20) if mobile_dlg else 700
            hauteur_dlg = (page.height - 100) if mobile_dlg else 500

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"Réserver le caveau", weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    content=vue_formulaire_reservation(page, on_success, on_cancel, caveau_id_preselect=int(caveau_id)),
                    width=largeur_dlg,
                    height=hauteur_dlg,
                ),
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        page.on_loaded = lambda e: ouvrir_formulaire_caveau()

    return vue


def _accueil_client(user):
    from api_client import client

    nom = user.get("prenom", "")
    reservations = client.get_reservations()
    total_res = len(reservations)
    en_attente = sum(1 for r in reservations if r.get("statut") == "EN_ATTENTE")
    validees = sum(1 for r in reservations if r.get("statut") == "VALIDEE")

    geojson = client.get_caveaux_geojson()
    features = geojson.get("features", [])
    disponibles = sum(1 for f in features if f["properties"]["statut"] == "DISPONIBLE")

    def carte_stat(titre, valeur, icone, couleur, sous_titre):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(icone, color="white", size=26),
                        bgcolor=couleur,
                        border_radius=12,
                        padding=14,
                        width=54,
                        height=54,
                    ),
                    ft.Container(height=12),
                    ft.Text(str(valeur), size=30, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
                    ft.Text(titre, size=13, weight=ft.FontWeight.W_600, color=COULEURS["texte"]),
                    ft.Text(sous_titre, size=11, color=COULEURS["texte_clair"]),
                ],
                spacing=2,
            ),
            bgcolor="white",
            border_radius=16,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=10, color="#0D000000", offset=ft.Offset(0, 3)),
            width=200,
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
                                    ft.Text(f"Bonjour, {nom} 👋", size=26, weight=ft.FontWeight.BOLD, color="white"),
                                    ft.Text("Bienvenue sur votre espace personnel", size=14, color="#FFFFFFCC"),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.Icon(ft.icons.HOME_WORK, size=50, color="#FFFFFF33"),
                        ],
                    ),
                    bgcolor=COULEURS["primaire"],
                    border_radius=16,
                    padding=ft.padding.symmetric(horizontal=25, vertical=20),
                    shadow=ft.BoxShadow(blur_radius=15, color="#221B4F72", offset=ft.Offset(0, 4)),
                ),
                ft.Container(height=25),
                ft.Text("Vue d'ensemble", size=18, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                ft.Container(height=12),
                ft.Row(
                    controls=[
                        carte_stat("Réservations", total_res, ft.icons.BOOK, COULEURS["primaire"], "Total soumises"),
                        carte_stat("En attente", en_attente, ft.icons.PENDING, "#fd7e14", "À valider"),
                        carte_stat("Validées", validees, ft.icons.CHECK_CIRCLE, "#28a745", "Confirmées"),
                        carte_stat("Caveaux dispo", disponibles, ft.icons.GRID_VIEW, "#2E86C1", "Disponibles"),
                    ],
                    spacing=15,
                    wrap=True,
                ),
                ft.Container(height=25),
                ft.Text("Actions rapides", size=18, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                ft.Container(height=12),
                ft.Row(
                    controls=[
                        _action_card("Réserver un caveau", "Choisir un emplacement sur la carte", ft.icons.ADD_LOCATION, COULEURS["primaire"]),
                        _action_card("Voir mes réservations", "Suivre l'état de vos demandes", ft.icons.LIST_ALT, "#2E86C1"),
                        _action_card("Consulter la carte", "Voir les emplacements disponibles", ft.icons.MAP, "#28a745"),
                    ],
                    spacing=15,
                    wrap=True,
                ),
                ft.Container(height=25),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.icons.INFO, color=COULEURS["primaire"], size=20),
                            ft.Text(
                                "Pour toute question, contactez le Cimetière Municipal de Pointe-Noire.",
                                size=13,
                                color=COULEURS["texte"],
                                expand=True,
                            ),
                        ],
                        spacing=10,
                    ),
                    bgcolor="#E8F4FD",
                    border_radius=10,
                    padding=15,
                    border=ft.border.all(1, "#BEE3F8"),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )


def _action_card(titre, description, icone, couleur):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Icon(icone, color="white", size=28),
                    bgcolor=couleur,
                    border_radius=12,
                    padding=14,
                    width=56,
                    height=56,
                ),
                ft.Container(height=10),
                ft.Text(titre, size=14, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Text(description, size=12, color=COULEURS["texte_clair"]),
            ],
            spacing=2,
        ),
        bgcolor="white",
        border_radius=16,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=8, color="#0D000000", offset=ft.Offset(0, 2)),
        width=260,
    )


def _carte_et_reserver(page, client):
    from views.client.carte import vue_carte_client
    return vue_carte_client(page, client)


def _mes_reservations(page, client):
    from views.client.mes_reservations import vue_mes_reservations
    return vue_mes_reservations(page, client)


def _mes_concessions(page, client):
    concessions = client.get_concessions()

    STATUT_COULEURS = {"ACTIVE": "#28a745", "EN_RENOUVELLEMENT": "#fd7e14", "EXPIREE": "#dc3545", "RESILIEE": "#6c757d"}
    TYPE_LABELS = {"TEMPORAIRE": "Temporaire (5 ans)", "TRENTENAIRE": "Trentenaire (30 ans)", "PERPETUELLE": "Perpétuelle", "FAMILIALE": "Familiale"}

    liste = ft.Column(spacing=12)

    if not concessions:
        liste.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.DESCRIPTION, size=60, color=COULEURS["texte_clair"]),
                        ft.Text("Aucune concession", size=16, color=COULEURS["texte_clair"]),
                        ft.Text("Vos concessions apparaîtront ici après validation de vos réservations.", size=13, color=COULEURS["texte_clair"], text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.center,
                padding=60,
            )
        )
    else:
        for c in concessions:
            statut = c.get("statut", "")
            jours = c.get("jours_restants")
            est_perpetuelle = c.get("date_fin") is None
            liste.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(c.get("numero_contrat", ""), size=16, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                                            ft.Text(TYPE_LABELS.get(c.get("type_concession", ""), ""), size=13, color=COULEURS["texte"]),
                                            ft.Text(f"Début : {c.get('date_debut', '')}", size=12, color=COULEURS["texte_clair"]),
                                        ],
                                        spacing=3,
                                        expand=True,
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Container(
                                                content=ft.Text(statut, size=11, color="white", weight=ft.FontWeight.BOLD),
                                                bgcolor=STATUT_COULEURS.get(statut, "#6c757d"),
                                                border_radius=20,
                                                padding=ft.padding.symmetric(horizontal=12, vertical=5),
                                            ),
                                            ft.Text(
                                                "Perpétuelle" if est_perpetuelle else (f"{jours} jours restants" if jours else "—"),
                                                size=12,
                                                color=COULEURS["danger"] if (jours and jours < 30) else COULEURS["texte_clair"],
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                        spacing=5,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    bgcolor="white",
                    border_radius=14,
                    padding=18,
                    shadow=ft.BoxShadow(blur_radius=8, color="#0D000000", offset=ft.Offset(0, 2)),
                )
            )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=25),
                ft.Text("Mes concessions", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Text("Vos contrats de concession funéraire", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=20),
                liste,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )


def _mes_paiements(page, client):
    paiements = client.get_paiements()

    CANAL_LABELS = {"ESPECES": "Espèces", "AIRTEL_MONEY": "Airtel Money", "MTN_MOMO": "MTN MoMo", "VIREMENT": "Virement", "CHEQUE": "Chèque"}
    STATUT_COULEURS = {"EN_ATTENTE": "#fd7e14", "CONFIRME": "#28a745", "ECHEC": "#dc3545"}

    liste = ft.Column(spacing=12)

    if not paiements:
        liste.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.PAYMENT, size=60, color=COULEURS["texte_clair"]),
                        ft.Text("Aucun paiement", size=16, color=COULEURS["texte_clair"]),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.center,
                padding=60,
            )
        )
    else:
        for p in paiements:
            statut = p.get("statut", "")
            liste.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.icons.RECEIPT, color="white", size=22),
                                bgcolor=COULEURS["primaire"],
                                border_radius=10,
                                padding=12,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(p.get("reference", ""), size=15, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                                    ft.Text(CANAL_LABELS.get(p.get("canal", ""), ""), size=12, color=COULEURS["texte_clair"]),
                                    ft.Text(p.get("date_paiement", "")[:10], size=12, color=COULEURS["texte_clair"]),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(f"{int(p.get('montant_xaf', 0)):,} FCFA".replace(",", " "), size=16, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
                                    ft.Container(
                                        content=ft.Text(statut, size=11, color="white"),
                                        bgcolor=STATUT_COULEURS.get(statut, "#6c757d"),
                                        border_radius=20,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=5,
                            ),
                        ],
                        spacing=15,
                    ),
                    bgcolor="white",
                    border_radius=14,
                    padding=16,
                    shadow=ft.BoxShadow(blur_radius=8, color="#0D000000", offset=ft.Offset(0, 2)),
                )
            )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=25),
                ft.Text("Mes paiements", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Text("Historique de vos transactions", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=20),
                liste,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )