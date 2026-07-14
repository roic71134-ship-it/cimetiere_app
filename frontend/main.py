import flet as ft
from config import COULEURS, APP_NOM
from views.auth.login import vue_login
from views.auth.mfa import vue_mfa
from views.auth.inscription import vue_inscription

BREAKPOINT_MOBILE = 700


def main(page: ft.Page):
    page.title = APP_NOM
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COULEURS["fond"]
    page.padding = 0

    email_temp = {"value": ""}

    # Vérifier si on vient de la carte avec un caveau pré-sélectionné
    caveau_id = None
    caveau_ref = None
    try:
        if page.query and 'caveau_id' in page.query:
            caveau_id = page.query['caveau_id']
            caveau_ref = page.query.get('reference', '')
    except Exception:
        pass

    def est_mobile():
        return (page.width or 1200) < BREAKPOINT_MOBILE

    def afficher_login():
        def on_login_success(email):
            email_temp["value"] = email
            afficher_mfa(email)

        def aller_inscription():
            afficher_inscription()

        def construire():
            page.controls.clear()
            mobile = est_mobile()

            panneau_marque = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.HOME_WORK, size=60 if mobile else 80, color="white"),
                        ft.Container(height=15),
                        ft.Text(APP_NOM, size=18 if mobile else 22, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
                        ft.Container(height=8),
                        ft.Text("République du Congo", size=13, color="#FFFFFFB3", text_align=ft.TextAlign.CENTER),
                        ft.Container(height=15 if mobile else 40),
                        ft.Text(
                            "Gestion moderne\ndu patrimoine funéraire",
                            size=14 if mobile else 16,
                            color="#FFFFFFB3",
                            text_align=ft.TextAlign.CENTER,
                            visible=not mobile,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                bgcolor=COULEURS["primaire"],
                width=None if mobile else 400,
                padding=ft.padding.symmetric(horizontal=20, vertical=25) if mobile else 40,
            )

            panneau_formulaire = ft.Container(
                content=_vue_login_avec_inscription(page, on_login_success, aller_inscription, mobile),
                expand=True,
                bgcolor="white",
            )

            if mobile:
                layout = ft.Column(
                    controls=[panneau_marque, panneau_formulaire],
                    expand=True,
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                )
            else:
                layout = ft.Row(
                    controls=[panneau_marque, panneau_formulaire],
                    expand=True,
                    spacing=0,
                )

            page.controls.append(layout)
            page.update()

        construire()
        page.on_resize = lambda e: construire()

    def afficher_inscription():
        def on_inscription_success(email):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Compte créé avec succès ! Connectez-vous.", color="white"),
                bgcolor=COULEURS["success"],
            )
            page.snack_bar.open = True
            afficher_login()

        def aller_login():
            afficher_login()

        page.on_resize = None
        page.controls.clear()
        page.controls.append(
            ft.Container(
                content=vue_inscription(page, on_inscription_success, aller_login),
                expand=True,
            )
        )
        page.update()

    def afficher_mfa(email):
        def on_mfa_success(token_data):
            router_par_role()

        def construire():
            page.controls.clear()
            mobile = est_mobile()

            panneau_marque = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.SECURITY, size=60 if mobile else 80, color="white"),
                        ft.Container(height=15),
                        ft.Text("Vérification\nde sécurité", size=18 if mobile else 22, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
                        ft.Container(height=8),
                        ft.Text(
                            "Votre compte est protégé\npar une double authentification",
                            size=13, color="#FFFFFFB3", text_align=ft.TextAlign.CENTER,
                            visible=not mobile,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                bgcolor=COULEURS["primaire"],
                width=None if mobile else 400,
                padding=ft.padding.symmetric(horizontal=20, vertical=25) if mobile else 40,
            )

            panneau_formulaire = ft.Container(
                content=vue_mfa(page, email, on_mfa_success),
                expand=True,
                bgcolor="white",
            )

            if mobile:
                layout = ft.Column(
                    controls=[panneau_marque, panneau_formulaire],
                    expand=True,
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                )
            else:
                layout = ft.Row(
                    controls=[panneau_marque, panneau_formulaire],
                    expand=True,
                    spacing=0,
                )

            page.controls.append(layout)
            page.update()

        construire()
        page.on_resize = lambda e: construire()

    def router_par_role():
        from api_client import client
        user = client.get_me()
        role = user.get("role", {})
        role_nom = role.get("nom", "") if role else ""

        page.on_resize = None
        page.controls.clear()

        if role_nom in ["ADMIN", "SECRETARIAT"]:
            from views.dashboard.dashboard import vue_dashboard
            page.controls.append(vue_dashboard(page, afficher_login))

        elif role_nom == "AGENT":
            from views.agent.dashboard import vue_dashboard_agent
            page.controls.append(vue_dashboard_agent(page, afficher_login))

        elif role_nom == "CLIENT":
            from views.client.dashboard import vue_dashboard_client
            page.controls.append(vue_dashboard_client(page, afficher_login, caveau_id=caveau_id))
        else:
            # Rôle inconnu — dashboard admin par défaut
            from views.dashboard.dashboard import vue_dashboard
            page.controls.append(vue_dashboard(page, afficher_login))

        page.update()

    afficher_login()


def _vue_login_avec_inscription(page, on_success, aller_inscription, mobile=False):
    from api_client import client

    largeur_champ = None if mobile else 380

    email_input = ft.TextField(
        label="Adresse email",
        hint_text="exemple@email.com",
        prefix_icon=ft.icons.EMAIL_OUTLINED,
        border_radius=10,
        focused_border_color=COULEURS["primaire"],
        color="black",
        width=largeur_champ,
        expand=mobile,
    )
    password_input = ft.TextField(
        label="Mot de passe",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK_OUTLINED,
        border_radius=10,
        focused_border_color=COULEURS["primaire"],
        color="black",
        width=largeur_champ,
        expand=mobile,
    )
    message = ft.Text("", color=COULEURS["danger"], size=13)
    loading = ft.ProgressRing(width=20, height=20, visible=False)

    def on_login(e):
        if not email_input.value or not password_input.value:
            message.value = "Veuillez remplir tous les champs."
            page.update()
            return

        loading.visible = True
        btn_login.disabled = True
        message.value = ""
        page.update()

        result = client.login(email_input.value, password_input.value)

        loading.visible = False
        btn_login.disabled = False

        if result.get("message") == "Code MFA envoyé à votre adresse email.":
            on_success(email_input.value)
        else:
            message.value = result.get("message", "Erreur de connexion.")

        page.update()

    btn_login = ft.ElevatedButton(
        text="Se connecter",
        width=largeur_champ,
        expand=mobile,
        height=48,
        bgcolor=COULEURS["primaire"],
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=on_login,
    )

    btn_inscription = ft.OutlinedButton(
        text="Créer un compte citoyen",
        width=largeur_champ,
        expand=mobile,
        height=45,
        style=ft.ButtonStyle(
            color=COULEURS["primaire"],
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=lambda e: aller_inscription(),
    )

    contenu_colonne = [
        ft.Container(height=25 if mobile else 40),
        ft.Icon(ft.icons.HOME_WORK, size=40 if mobile else 50, color=COULEURS["primaire"]),
        ft.Container(height=10),
        ft.Text(APP_NOM, size=16 if mobile else 18, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"], text_align=ft.TextAlign.CENTER),
        ft.Text("Système de gestion du cimetière", size=12 if mobile else 13, color=COULEURS["texte_clair"], text_align=ft.TextAlign.CENTER),
        ft.Container(height=20 if mobile else 30),
        ft.Text("Connexion", size=20 if mobile else 22, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
        ft.Container(height=15),
        email_input,
        ft.Container(height=10),
        password_input,
        ft.Container(height=5),
        message,
        ft.Container(height=15),
        btn_login,
        loading,
        ft.Container(height=15),
        ft.Divider(color="#E0E0E0"),
        ft.Container(height=10),
        ft.Text("Pas encore de compte ?", size=13, color=COULEURS["texte_clair"], text_align=ft.TextAlign.CENTER),
        ft.Container(height=5),
        btn_inscription,
        ft.Container(height=20),
    ]

    return ft.Container(
        content=ft.Column(
            controls=contenu_colonne,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=20) if mobile else ft.padding.all(30),
        alignment=ft.alignment.center,
        expand=True,
    )


ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)