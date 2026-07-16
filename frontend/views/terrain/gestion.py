import flet as ft
from config import COULEURS


def vue_gestion_terrain(page: ft.Page):
    from api_client import client


    def snack(msg, couleur=None):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=couleur or COULEURS["success"],
        )
        page.snack_bar.open = True
        page.update()

    # ─── Onglets ─────────────────────────────────────────────────────────────
    onglet_actif = {"index": 0}
    contenu_onglets = ft.Container(expand=True)

    def afficher_onglet(index):
        onglet_actif["index"] = index
        for i, btn in enumerate(onglet_buttons):
            btn.bgcolor = COULEURS["primaire"] if i == index else "transparent"
            btn.content.color = "white" if i == index else COULEURS["texte_clair"]
        if index == 0:
            contenu_onglets.content = _vue_zones(page, client, snack)
        elif index == 1:
            contenu_onglets.content = _vue_blocs(page, client, snack)
        elif index == 2:
            contenu_onglets.content = _vue_caveaux(page, client, snack)
        elif index == 3:
            contenu_onglets.content = _vue_configuration(page, client, snack)
        page.update()

    onglet_labels = ["Zones", "Blocs", "Caveaux", "Configuration"]
    onglet_buttons = []
    for i, label in enumerate(onglet_labels):
        btn = ft.Container(
            content=ft.Text(label, color="white" if i == 0 else COULEURS["texte_clair"], size=14, weight=ft.FontWeight.W_500),
            bgcolor=COULEURS["primaire"] if i == 0 else "transparent",
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            on_click=lambda e, idx=i: afficher_onglet(idx),
            ink=True,
        )
        onglet_buttons.append(btn)

    afficher_onglet(0)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Text("Gestion du terrain", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Text("Zones, blocs et caveaux du cimetière", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=15),
                ft.Row(controls=onglet_buttons, spacing=5),
                ft.Divider(height=1, color="#E0E0E0"),
                ft.Container(height=10),
                contenu_onglets,
            ],
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )


def _vue_zones(page, client, snack):
    zones = client.get_zones()
    liste = ft.Column(spacing=10)

    TYPE_LABELS = {
        "INHUMATION": "Inhumation",
        "ALLEE": "Allée/Chemin",
        "NON_EXPLOITABLE": "Non exploitable",
        "TECHNIQUE": "Technique",
        "ENTREE": "Entrée/Accueil",
    }

    def charger():
        z = client.get_zones()
        liste.controls.clear()
        if not z:
            liste.controls.append(ft.Text("Aucune zone", color=COULEURS["texte_clair"]))
        else:
            for zone in z:
                liste.controls.append(
                    ft.Container(
                        content=ft.Row(controls=[
                            ft.Container(width=14, height=14, bgcolor=zone.get("couleur_carte", "#90EE90"), border_radius=7),
                            ft.Column(expand=True, spacing=2, controls=[
                                ft.Text(f"Zone {zone.get('code', '')} — {zone.get('nom', '')}", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                                ft.Text(TYPE_LABELS.get(zone.get("type_zone", ""), ""), size=12, color=ft.colors.GREY),
                            ]),
                        ], spacing=12),
                        bgcolor="white", border_radius=10, padding=14,
                        shadow=ft.BoxShadow(blur_radius=4, color="#0D000000", offset=ft.Offset(0, 1)),
                    )
                )
        page.update()

    def ajouter_zone(e):
        nom_f = ft.TextField(color="white", label="Nom *", border_radius=8, expand=True)
        code_f = ft.TextField(color="white", label="Code * (ex: A, B, C)", border_radius=8, expand=True)
        type_f = ft.Dropdown(
            label="Type *", border_radius=8, expand=True,
            options=[
                ft.dropdown.Option("INHUMATION", "Inhumation"),
                ft.dropdown.Option("ALLEE", "Allée/Chemin"),
                ft.dropdown.Option("NON_EXPLOITABLE", "Non exploitable"),
                ft.dropdown.Option("TECHNIQUE", "Technique"),
                ft.dropdown.Option("ENTREE", "Entrée/Accueil"),
            ],
            value="INHUMATION",
        )
        msg_f = ft.Text("", color=COULEURS["danger"], size=12)

        def confirmer(e):
            if not nom_f.value or not code_f.value:
                msg_f.value = "Nom et Code sont obligatoires."
                page.update()
                return
            dlg.open = False
            page.update()
            res = client.creer_zone({
                "nom": nom_f.value,
                "code": code_f.value.upper(),
                "type_zone": type_f.value,
            })
            if "créée" in res.get("message", "").lower():
                snack(f"✅ {res['message']}")
            else:
                snack(res.get("message", "Erreur"), COULEURS["danger"])
            charger()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nouvelle zone", weight=ft.FontWeight.BOLD),
            content=ft.Container(width=400, content=ft.Column(tight=True, spacing=10, controls=[nom_f, code_f, type_f, msg_f])),
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                ft.ElevatedButton("Créer", bgcolor=COULEURS["primaire"], color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=confirmer),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    charger()

    return ft.Column(
        controls=[
            ft.Row(controls=[
                ft.Text("Zones", size=18, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Container(expand=True),
                ft.ElevatedButton("+ Nouvelle zone", bgcolor=COULEURS["success"], color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=ajouter_zone),
            ]),
            ft.Container(height=10),
            liste,
        ],
        scroll=ft.ScrollMode.AUTO,
    )


def _vue_blocs(page, client, snack):
    liste = ft.Column(spacing=10)

    def charger():
        blocs = client.get_blocs()
        liste.controls.clear()
        if not blocs:
            liste.controls.append(ft.Text("Aucun bloc", color=COULEURS["texte_clair"]))
        else:
            for b in blocs:
                liste.controls.append(
                    ft.Container(
                        content=ft.Row(controls=[
                            ft.Column(expand=True, spacing=2, controls=[
                                ft.Text(f"{b.get('zone_nom', '')} — Bloc {b.get('code', '')}", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                                ft.Text(f"Capacité : {b.get('capacite_theorique', 0)} caveaux", size=12, color=ft.colors.GREY),
                            ]),
                        ], spacing=12),
                        bgcolor="white", border_radius=10, padding=14,
                        shadow=ft.BoxShadow(blur_radius=4, color="#0D000000", offset=ft.Offset(0, 1)),
                    )
                )
        page.update()

    def ajouter_bloc(e):
        zones = client.get_zones()
        if not zones:
            snack("Créez d'abord une zone.", COULEURS["danger"])
            return

        zone_f = ft.Dropdown(
            label="Zone *", border_radius=8, expand=True,
            options=[ft.dropdown.Option(str(z.get("id")), f"Zone {z.get('code')} — {z.get('nom')}") for z in zones],
        )
        code_f = ft.TextField(color="white", label="Code bloc * (ex: 01, 02)", border_radius=8, expand=True)
        nom_f = ft.TextField(color="white", label="Nom (ex: Bloc 01)", border_radius=8, expand=True)
        cap_f = ft.TextField(color="white", label="Capacité théorique", value="10", border_radius=8, expand=True)
        msg_f = ft.Text("", color=COULEURS["danger"], size=12)

        def confirmer(e):
            if not zone_f.value or not code_f.value or not nom_f.value:
                msg_f.value = "Tous les champs sont obligatoires."
                page.update()
                return
            dlg.open = False
            page.update()
            res = client.creer_bloc({
                "zone_id": int(zone_f.value),
                "nom": nom_f.value,
                "code": code_f.value,
                "capacite_theorique": int(cap_f.value or 0),
            })
            if "créé" in res.get("message", "").lower():
                snack(f"✅ {res['message']}")
            else:
                snack(res.get("message", "Erreur"), COULEURS["danger"])
            charger()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nouveau bloc", weight=ft.FontWeight.BOLD),
            content=ft.Container(width=400, content=ft.Column(tight=True, spacing=10, controls=[zone_f, code_f, nom_f, cap_f, msg_f])),
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                ft.ElevatedButton("Créer", bgcolor=COULEURS["primaire"], color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=confirmer),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    charger()

    return ft.Column(
        controls=[
            ft.Row(controls=[
                ft.Text("Blocs", size=18, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Container(expand=True),
                ft.ElevatedButton("+ Nouveau bloc", bgcolor=COULEURS["success"], color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=ajouter_bloc),
            ]),
            ft.Container(height=10),
            liste,
        ],
        scroll=ft.ScrollMode.AUTO,
    )


def _vue_caveaux(page, client, snack):
    liste = ft.Column(spacing=10)

    STATUT_COULEURS = {
        "DISPONIBLE": "#28a745", "RESERVE": "#fd7e14",
        "OCCUPE": "#dc3545", "NON_EXPLOITABLE": "#6c757d", "MAINTENANCE": "#ffc107",
    }

    def charger():
        geojson = client.get_caveaux_geojson()
        features = geojson.get("features", [])
        liste.controls.clear()
        if not features:
            liste.controls.append(ft.Text("Aucun caveau", color=COULEURS["texte_clair"]))
        else:
            for f in features:
                props = f["properties"]
                statut = props.get("statut", "")
                liste.controls.append(
                    ft.Container(
                        content=ft.Row(controls=[
                            ft.Container(width=12, height=12, bgcolor=STATUT_COULEURS.get(statut, "#6c757d"), border_radius=6),
                            ft.Text(props.get("reference", ""), size=14, weight=ft.FontWeight.BOLD, color=ft.colors.BLACK),
                            ft.Container(expand=True),
                            ft.Text(props.get("bloc", ""), size=12, color=ft.colors.GREY),
                            ft.Container(
                                content=ft.Text(statut, size=11, color="white"),
                                bgcolor=STATUT_COULEURS.get(statut, "#6c757d"),
                                border_radius=20,
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            ),
                        ], spacing=10),
                        bgcolor="white", border_radius=10, padding=14,
                        shadow=ft.BoxShadow(blur_radius=4, color="#0D000000", offset=ft.Offset(0, 1)),
                    )
                )
        page.update()

    def ajouter_caveau(e):
        blocs = client.get_blocs()
        if not blocs:
            snack("Créez d'abord un bloc.", COULEURS["danger"])
            return

        bloc_f = ft.Dropdown(
            label="Bloc *", border_radius=8, expand=True,
            options=[ft.dropdown.Option(str(b.get("id")), f"{b.get('zone_nom', '')} — Bloc {b.get('code', '')}") for b in blocs],
        )
        num_f = ft.TextField(color="white", label="Numéro * (ex: 6)", border_radius=8, expand=True)
        lat_f = ft.TextField(color="white", label="Latitude * (ex: -4.7692)", border_radius=8, expand=True)
        lng_f = ft.TextField(color="white", label="Longitude * (ex: 11.8635)", border_radius=8, expand=True)
        prix_temp_f = ft.TextField(color="white", label="Prix temporaire (FCFA)", value="150000", border_radius=8, expand=True)
        prix_perp_f = ft.TextField(color="white", label="Prix perpétuel (FCFA)", value="500000", border_radius=8, expand=True)
        type_f = ft.Dropdown(
            label="Type concession", border_radius=8, expand=True,
            value="TEMPORAIRE",
            options=[
                ft.dropdown.Option("TEMPORAIRE", "Temporaire"),
                ft.dropdown.Option("TRENTENAIRE", "Trentenaire"),
                ft.dropdown.Option("PERPETUELLE", "Perpétuelle"),
                ft.dropdown.Option("FAMILIALE", "Familiale"),
            ],
        )
        msg_f = ft.Text("", color=COULEURS["danger"], size=12)

        def confirmer(e):
            if not bloc_f.value or not num_f.value or not lat_f.value or not lng_f.value:
                msg_f.value = "Bloc, numéro, latitude et longitude sont obligatoires."
                page.update()
                return
            try:
                lat = float(lat_f.value)
                lng = float(lng_f.value)
            except ValueError:
                msg_f.value = "Latitude et longitude doivent être des nombres."
                page.update()
                return

            dlg.open = False
            page.update()
            res = client.creer_caveau({
                "bloc_id": int(bloc_f.value),
                "numero": int(num_f.value),
                "latitude": lat,
                "longitude": lng,
                "type_concession": type_f.value,
                "prix_temporaire_xaf": int(prix_temp_f.value or 150000),
                "prix_perpetuelle_xaf": int(prix_perp_f.value or 500000),
                "capacite_corps": 1,
            })
            if "créé" in res.get("message", "").lower():
                snack(f"✅ {res['message']}")
            else:
                snack(res.get("message", "Erreur"), COULEURS["danger"])
            charger()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nouveau caveau", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=450,
                content=ft.Column(tight=True, spacing=10, controls=[
                    bloc_f, num_f,
                    ft.Row(controls=[lat_f, lng_f], spacing=10),
                    type_f,
                    ft.Row(controls=[prix_temp_f, prix_perp_f], spacing=10),
                    msg_f,
                ]),
            ),
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                ft.ElevatedButton("Créer", bgcolor=COULEURS["primaire"], color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=confirmer),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    charger()

    return ft.Column(
        controls=[
            ft.Row(controls=[
                ft.Text("Caveaux", size=18, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Container(expand=True),
                ft.ElevatedButton("+ Nouveau caveau", bgcolor=COULEURS["success"], color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=ajouter_caveau),
            ]),
            ft.Container(height=10),
            liste,
        ],
        scroll=ft.ScrollMode.AUTO,
    )
def _vue_configuration(page, client, snack):
    stats = client.get_statistiques_terrain()

    superficie_f = ft.TextField(color="black", 
        label="Superficie totale (m²)",
        value=str(stats.get("superficie_m2", 0)),
        border_radius=8, expand=True,
    )
    longueur_f = ft.TextField(color="black", 
        label="Longueur standard caveau (m)",
        value=str(stats.get("taille_std_longueur", 2.5)),
        border_radius=8, expand=True,
    )
    largeur_f = ft.TextField(color="black", 
        label="Largeur standard caveau (m)",
        value=str(stats.get("taille_std_largeur", 1.2)),
        border_radius=8, expand=True,
    )

    resultat = ft.Column(spacing=8)

    def calculer(e):
        try:
            superficie = float(superficie_f.value or 0)
            longueur = float(longueur_f.value or 2.5)
            largeur = float(largeur_f.value or 1.2)
            surface_caveau = longueur * largeur
            exploitable = superficie * 0.70
            places = int(exploitable / surface_caveau) if surface_caveau > 0 else 0

            resultat.controls.clear()
            resultat.controls.append(
                ft.Container(
                    content=ft.Column(spacing=8, controls=[
                        ft.Text("Résultat du calcul", size=15, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                        ft.Text(f"Zones non exploitables détectées → % exploitable réel : {stats.get('pct_exploitable', 70)}%", size=13, color=COULEURS["texte_clair"]),
                        ft.Text(f"Superficie exploitable : {stats.get('superficie_exploitable_m2', 0)} m²", size=13, color=COULEURS["texte"]),
                        ft.Text(f"Surface par caveau : {round(surface_caveau, 2)} m²", size=13, color=COULEURS["texte"]),
                        ft.Text(f"Places théoriques : {places}", size=16, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                        ft.Text(f"Places actuelles : {stats.get('places_actuelles', 0)}", size=13, color=COULEURS["texte"]),
                        ft.Text(f"Places à créer : {max(0, places - stats.get('places_actuelles', 0))}", size=13, color=COULEURS["success"]),
                    ]),
                    bgcolor=COULEURS["blanc"], border_radius=12, padding=20,
                    shadow=ft.BoxShadow(blur_radius=6, color="#1A000000", offset=ft.Offset(0, 2)),
                )
            )
            page.update()
        except Exception as ex:
            snack(f"Erreur : {ex}", COULEURS["danger"])

    def enregistrer(e):
        try:
            res = client.configurer_cimetiere({
                "superficie_m2": float(superficie_f.value or 0),
                "taille_std_longueur": float(longueur_f.value or 2.5),
                "taille_std_largeur": float(largeur_f.value or 1.2),
            })
            snack(res.get("message", "Configuration enregistrée !"))
            calculer(None)
        except Exception as ex:
            snack(f"Erreur : {ex}", COULEURS["danger"])

    calculer(None)

    return ft.Column(
        controls=[
            ft.Row(controls=[
                ft.Text("Configuration du cimetière", size=18, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
            ]),
            ft.Container(height=15),
            ft.Container(
                content=ft.Column(spacing=10, controls=[
                    ft.Text("Paramètres spatiaux", size=14, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                    ft.Container(height=5),
                    superficie_f,
                    ft.Row(controls=[longueur_f, largeur_f], spacing=10),
                    ft.Row(spacing=10, controls=[
                        ft.ElevatedButton(
                            "Calculer les places",
                            icon=ft.icons.CALCULATE,
                            bgcolor=COULEURS["primaire"], color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=calculer,
                        ),
                        ft.ElevatedButton(
                            "Enregistrer",
                            icon=ft.icons.SAVE,
                            bgcolor=COULEURS["success"], color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=enregistrer,
                        ),
                    ]),
                ]),
                bgcolor=COULEURS["blanc"], border_radius=12, padding=20,
                shadow=ft.BoxShadow(blur_radius=6, color="#1A000000", offset=ft.Offset(0, 2)),
            ),
            ft.Container(height=15),
            resultat,
        ],
        scroll=ft.ScrollMode.AUTO,
    )    
