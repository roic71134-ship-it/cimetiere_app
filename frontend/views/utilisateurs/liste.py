import flet as ft
from config import COULEURS


ROLE_COULEURS = {
    "ADMIN":       "#1B4F72",
    "SECRETARIAT": "#2E86C1",
    "AGENT":       "#28a745",
    "CLIENT":      "#6c757d",
}

ROLE_LABELS = {
    "ADMIN":       "Administrateur",
    "SECRETARIAT": "Secrétariat",
    "AGENT":       "Agent terrain",
    "CLIENT":      "Client",
}


def vue_utilisateurs(page: ft.Page):
    from api_client import client

    liste = ft.Column(spacing=10)
    zone_contenu = ft.Column(controls=[liste], expand=True, scroll=ft.ScrollMode.AUTO)

    def badge_role(role_nom):
        return ft.Container(
            content=ft.Text(ROLE_LABELS.get(role_nom, role_nom), size=11, color="white", weight=ft.FontWeight.BOLD),
            bgcolor=ROLE_COULEURS.get(role_nom, "#6c757d"),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
        )

    def snack(msg, couleur=None):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=couleur or COULEURS["success"],
        )
        page.snack_bar.open = True
        page.update()

    def carte_utilisateur(u):
        uid = u.get("id")
        role_nom = u.get("role_nom", "")
        est_actif = u.get("est_actif", True)

        def ouvrir_modification(e):
            nom_f = ft.TextField(color="white", label="Nom", value=u.get("nom", ""), border_radius=8, expand=True)
            prenom_f = ft.TextField(color="white", label="Prénom", value=u.get("prenom", ""), border_radius=8, expand=True)
            tel_f = ft.TextField(color="white", label="Téléphone", value=u.get("telephone", ""), border_radius=8, expand=True)
            role_f = ft.Dropdown(
                label="Rôle",
                value=role_nom,
                border_radius=8,
                expand=True,
                options=[
                    ft.dropdown.Option("ADMIN", "Administrateur"),
                    ft.dropdown.Option("SECRETARIAT", "Secrétariat"),
                    ft.dropdown.Option("AGENT", "Agent terrain"),
                    ft.dropdown.Option("CLIENT", "Client"),
                ],
            )
            actif_f = ft.Checkbox(label="Compte actif", value=est_actif)

            def confirmer(e):
                dlg.open = False
                page.update()
                res = client.modifier_utilisateur(uid, {
                    "nom": nom_f.value,
                    "prenom": prenom_f.value,
                    "telephone": tel_f.value,
                    "role_nom": role_f.value,
                    "est_actif": actif_f.value,
                })
                snack(res.get("message", "Modifié !"))
                charger_liste()
                page.update()

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Modifier l'utilisateur", weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    width=450,
                    content=ft.Column(tight=True, spacing=10, controls=[
                        ft.Row(controls=[prenom_f, nom_f], spacing=10),
                        tel_f,
                        role_f,
                        actif_f,
                    ]),
                ),
                actions_alignment=ft.MainAxisAlignment.END,
                actions=[
                    ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                    ft.ElevatedButton(
                        "Enregistrer",
                        bgcolor=COULEURS["primaire"], color="white",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=confirmer,
                    ),
                ],
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        def ouvrir_suppression(e):
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Désactiver le compte", weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    f"Voulez-vous désactiver le compte de {u.get('prenom', '')} {u.get('nom', '')} ?",
                    size=14,
                ),
                actions_alignment=ft.MainAxisAlignment.END,
                actions=[
                    ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                    ft.ElevatedButton(
                        "Désactiver",
                        bgcolor=COULEURS["danger"], color="white",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=lambda e: confirmer_suppression(dlg),
                    ),
                ],
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        def confirmer_suppression(dlg):
            dlg.open = False
            page.update()
            res = client.supprimer_utilisateur(uid)
            snack(res.get("message", "Compte désactivé."))
            charger_liste()
            page.update()

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text(u.get("prenom", "U")[0].upper(), color=COULEURS["primaire"], weight=ft.FontWeight.BOLD, size=18),
                        bgcolor="#E8F4FD",
                        radius=25,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(f"{u.get('prenom', '')} {u.get('nom', '')}", size=15, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                            ft.Text(u.get("email", ""), size=12, color=COULEURS["texte_clair"]),
                            ft.Text(u.get("telephone", "") or "—", size=12, color=COULEURS["texte_clair"]),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Column(
                        controls=[
                            badge_role(role_nom),
                            ft.Container(height=5),
                            ft.Container(
                                content=ft.Text("Actif" if est_actif else "Inactif", size=11, color="white"),
                                bgcolor="#28a745" if est_actif else "#dc3545",
                                border_radius=20,
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=0,
                    ),
                    ft.Column(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                icon_color=COULEURS["primaire"],
                                tooltip="Modifier",
                                on_click=ouvrir_modification,
                            ),
                            ft.IconButton(
                                icon=ft.icons.PERSON_OFF,
                                icon_color=COULEURS["danger"],
                                tooltip="Désactiver",
                                on_click=ouvrir_suppression,
                            ),
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=15,
            ),
            bgcolor=COULEURS["blanc"],
            border_radius=12,
            padding=15,
            shadow=ft.BoxShadow(blur_radius=6, color="#1A000000", offset=ft.Offset(0, 2)),
            opacity=1.0 if est_actif else 0.6,
        )

    def charger_liste():
        data = client.get_utilisateurs()
        liste.controls.clear()
        if not data:
            liste.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.icons.PEOPLE, size=50, color=COULEURS["texte_clair"]),
                            ft.Text("Aucun utilisateur trouvé", size=15, color=COULEURS["texte_clair"]),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    padding=50,
                )
            )
        else:
            for u in data:
                liste.controls.append(carte_utilisateur(u))

    def afficher_formulaire(e):
        from views.utilisateurs.formulaire import vue_formulaire_utilisateur

        def on_success(result):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(result.get("message", "Utilisateur créé !"), color="white"),
                bgcolor=COULEURS["success"],
            )
            page.snack_bar.open = True
            charger_liste()
            zone_contenu.controls.clear()
            zone_contenu.controls.append(liste)
            page.update()

        def on_cancel():
            zone_contenu.controls.clear()
            zone_contenu.controls.append(liste)
            page.update()

        formulaire = vue_formulaire_utilisateur(page, on_success, on_cancel)
        zone_contenu.controls.clear()
        zone_contenu.controls.append(formulaire)
        page.update()

    charger_liste()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Row(
                    controls=[
                        ft.Text("Utilisateurs", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Nouvel utilisateur",
                            icon=ft.icons.PERSON_ADD,
                            bgcolor=COULEURS["success"],
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=afficher_formulaire,
                        ),
                    ],
                ),
                ft.Text("Gestion des comptes utilisateurs", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=15),
                zone_contenu,
            ],
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )