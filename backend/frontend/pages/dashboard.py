"""Dashboard principal avec carte interactive des caveaux."""
import flet as ft
from utils.api_client import api_get, get_user_info


COULEURS = {
    "disponible":     "#22c55e",
    "reserve":        "#f97316",
    "occupe":         "#ef4444",
    "non_exploitable":"#9ca3af",
}

LABELS_ETAT = {
    "disponible":     "Disponible",
    "reserve":        "Réservé",
    "occupe":         "Occupé",
    "non_exploitable":"Non exploitable",
}


def DashboardPage(page: ft.Page, on_logout):
    user = get_user_info()
    role = user.get("role", "client")
    nom = user.get("nom_complet", "Utilisateur")

    # ── Statistiques ──────────────────────────────────────────────────────────
    stat_total = ft.Text("—", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_800)
    stat_dispo = ft.Text("—", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_700)
    stat_ress  = ft.Text("—", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_700)
    stat_occ   = ft.Text("—", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.RED_700)
    stat_taux  = ft.Text("—%", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_GREY_700)

    def carte_stat(label, valeur_ctrl, couleur):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([valeur_ctrl, ft.Text(label, size=12, color=ft.colors.GREY_600)],
                                  horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                padding=16,
                alignment=ft.alignment.center,
            ),
            elevation=2,
        )

    # ── Carte interactive (grille de caveaux) ─────────────────────────────────
    grille_caveaux = ft.GridView(
        expand=True,
        runs_count=10,
        max_extent=50,
        child_aspect_ratio=1.0,
        spacing=3,
        run_spacing=3,
    )

    detail_panel = ft.Container(
        content=ft.Text("Cliquez sur un caveau pour voir les détails", italic=True,
                        color=ft.colors.GREY_500),
        padding=16,
        border=ft.border.all(1, ft.colors.GREY_300),
        border_radius=8,
    )

    filtre_etat = ft.Dropdown(
        label="Filtrer par état",
        width=200,
        options=[
            ft.dropdown.Option("", "Tous"),
            ft.dropdown.Option("disponible", "Disponible"),
            ft.dropdown.Option("reserve", "Réservé"),
            ft.dropdown.Option("occupe", "Occupé"),
        ],
        value="",
    )

    caveaux_data = []

    def charger_donnees(e=None):
        # Statistiques
        ok_s, stats = api_get("/terrain/statistiques")
        if ok_s:
            stat_total.value = str(stats.get("total_caveaux", "—"))
            stat_dispo.value = str(stats.get("disponibles", "—"))
            stat_ress.value  = str(stats.get("reserves", "—"))
            stat_occ.value   = str(stats.get("occupes", "—"))
            stat_taux.value  = f"{stats.get('taux_occupation', 0):.1f}%"

        # Caveaux
        params = {}
        if filtre_etat.value:
            params["etat"] = filtre_etat.value

        ok_c, data = api_get("/terrain/caveaux", params)
        if ok_c and isinstance(data, list):
            caveaux_data.clear()
            caveaux_data.extend(data)
            afficher_caveaux()
        page.update()

    def afficher_caveaux():
        grille_caveaux.controls.clear()
        for c in caveaux_data:
            etat = c.get("etat", "non_exploitable")
            couleur = COULEURS.get(etat, "#9ca3af")
            ref = c.get("reference", "?")

            cell = ft.Container(
                content=ft.Text(ref[:3], size=7, color=ft.colors.WHITE,
                                text_align=ft.TextAlign.CENTER),
                bgcolor=couleur,
                border_radius=4,
                tooltip=f"{ref} — {LABELS_ETAT.get(etat, etat)}",
                on_click=lambda e, caveau=c: afficher_detail(caveau),
                alignment=ft.alignment.center,
            )
            grille_caveaux.controls.append(cell)

    def afficher_detail(caveau):
        etat = caveau.get("etat", "")
        peut_reserver = etat == "disponible" and role == "client"

        btn_reserver = ft.ElevatedButton(
            "Réserver ce caveau",
            icon=ft.icons.ADD_CIRCLE_OUTLINE,
            on_click=lambda e: ouvrir_formulaire_reservation(caveau),
            visible=peut_reserver,
            style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE),
        )

        detail_panel.content = ft.Column([
            ft.Text(f"Caveau : {caveau.get('reference')}", weight=ft.FontWeight.BOLD, size=16),
            ft.Text(f"Zone : {caveau.get('zone_nom', '—')}"),
            ft.Text(f"État : {LABELS_ETAT.get(etat, etat)}",
                    color=COULEURS.get(etat, "#000")),
            ft.Text(f"Rangée {caveau.get('rangee')} / Colonne {caveau.get('colonne')}"),
            ft.Text(f"GPS : {caveau.get('latitude', 0):.4f}, {caveau.get('longitude', 0):.4f}",
                    size=11, color=ft.colors.GREY_600),
            btn_reserver,
        ], spacing=6)
        page.update()

    def ouvrir_formulaire_reservation(caveau):
        nom_d = ft.TextField(label="Nom du défunt", width=280)
        prenom_d = ft.TextField(label="Prénom du défunt", width=280)
        deces_d = ft.TextField(label="Date de décès (AAAA-MM-JJ)", width=280)
        type_c = ft.Dropdown(
            label="Type de concession",
            width=280,
            options=[
                ft.dropdown.Option("temporaire", "Temporaire (15 ans)"),
                ft.dropdown.Option("perpetuelle", "Perpétuelle"),
            ],
            value="temporaire",
        )
        msg = ft.Text("", color=ft.colors.RED_600)

        def soumettre(e):
            if not all([nom_d.value, prenom_d.value, deces_d.value]):
                msg.value = "Tous les champs sont obligatoires."
                page.update()
                return

            from utils.api_client import api_post
            ok, data = api_post("/reservations/", {
                "caveau_id": caveau["id"],
                "type_concession": type_c.value,
                "defunt": {
                    "nom": nom_d.value,
                    "prenom": prenom_d.value,
                    "date_deces": deces_d.value,
                }
            })
            if ok:
                dlg.open = False
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"✓ Réservation #{data['id']} soumise avec succès !"),
                    bgcolor=ft.colors.GREEN_700
                )
                page.snack_bar.open = True
                charger_donnees()
            else:
                msg.value = data.get("message", "Erreur lors de la réservation.")
            page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Réserver — Caveau {caveau['reference']}"),
            content=ft.Column([nom_d, prenom_d, deces_d, type_c, msg],
                              tight=True, spacing=10),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                ft.ElevatedButton("Soumettre", on_click=soumettre,
                                   style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_800, color=ft.colors.WHITE)),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    filtre_etat.on_change = charger_donnees

    # ── Légende ──────────────────────────────────────────────────────────────
    legende = ft.Row([
        ft.Row([ft.Container(width=14, height=14, bgcolor=c, border_radius=3),
                ft.Text(l, size=12)], spacing=5)
        for c, l in [("#22c55e", "Disponible"), ("#f97316", "Réservé"),
                     ("#ef4444", "Occupé"), ("#9ca3af", "Non exploitable")]
    ], spacing=16)

    # ── AppBar ────────────────────────────────────────────────────────────────
    appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.CHURCH, color=ft.colors.WHITE),
        title=ft.Text("Gestion de Cimetière — GI2 2026", color=ft.colors.WHITE),
        bgcolor=ft.colors.BLUE_900,
        actions=[
            ft.Text(f"{nom} ({role})", color=ft.colors.WHITE70, size=12),
            ft.IconButton(ft.icons.REFRESH, icon_color=ft.colors.WHITE, on_click=charger_donnees,
                          tooltip="Actualiser"),
            ft.IconButton(ft.icons.LOGOUT, icon_color=ft.colors.WHITE, on_click=lambda e: on_logout(),
                          tooltip="Déconnexion"),
        ],
    )

    # ── Contenu principal ─────────────────────────────────────────────────────
    contenu = ft.Column([
        # Stats
        ft.Row([
            carte_stat("Total caveaux", stat_total, ft.colors.BLUE_800),
            carte_stat("Disponibles", stat_dispo, ft.colors.GREEN_700),
            carte_stat("Réservés", stat_ress, ft.colors.ORANGE_700),
            carte_stat("Occupés", stat_occ, ft.colors.RED_700),
            carte_stat("Taux d'occupation", stat_taux, ft.colors.BLUE_GREY_700),
        ], wrap=True, spacing=12),

        ft.Divider(),

        # Filtre + légende
        ft.Row([filtre_etat, ft.Container(expand=True), legende]),

        # Carte + détail
        ft.Row([
            ft.Container(
                content=grille_caveaux,
                expand=3,
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=8,
                padding=8,
                height=400,
            ),
            ft.Container(
                content=detail_panel,
                expand=1,
                padding=8,
            ),
        ], expand=True),
    ], expand=True, spacing=12)

    # Charger au démarrage
    charger_donnees()

    return appbar, ft.Container(content=contenu, padding=20, expand=True)
