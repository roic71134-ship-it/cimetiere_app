import flet as ft
from config import COULEURS, APP_NOM
from views.auth.login import vue_login
from views.auth.mfa import vue_mfa
from views.auth.inscription import vue_inscription

BREAKPOINT_MOBILE = 700
IMAGE_FOND = "F.jpg"


def main(page: ft.Page):
    page.title = APP_NOM
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#F0F1F3"
    page.padding = 0

    email_temp = {"value": ""}

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

    def bandeau_officiel():
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("🦅", size=18),
                    ft.Container(width=8),
                    ft.Text("État de France", size=13, weight=ft.FontWeight.W_500, color="white"),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            bgcolor="#0D2136",
            padding=ft.padding.symmetric(horizontal=24, vertical=10),
            width=float("inf"),
        )

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
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("🦅", size=48 if mobile else 64),
                            ft.Container(height=20),
                            ft.Text(APP_NOM, size=20 if mobile else 24, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
                            ft.Container(height=6),
                            ft.Text("SYSTÈME DE GESTION", size=11, weight=ft.FontWeight.W_500, color="#CCCCCC", text_align=ft.TextAlign.CENTER),
                            ft.Container(height=1, bgcolor="#FFFFFF55", width=60, margin=ft.margin.symmetric(vertical=24)),
                            ft.Text(
                                "Accès réservé aux personnels\nautorisés et aux usagers enregistrés.",
                                size=13,
                                color="#DDDDDD",
                                text_align=ft.TextAlign.CENTER,
                                visible=not mobile,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor="#0D2136B3",
                    padding=ft.padding.symmetric(horizontal=20, vertical=30) if mobile else 50,
                    expand=True,
                    alignment=ft.alignment.center,
                ),
                image_src=IMAGE_FOND,
                image_fit=ft.ImageFit.COVER,
                width=None if mobile else 420,
            )

            panneau_formulaire = ft.Container(
                content=ft.Column(
                    controls=[
                        bandeau_officiel(),
                        ft.Container(
                            content=_vue_login_avec_inscription(page, on_login_success, aller_inscription, mobile),
                            expand=True,
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
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
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.icons.SECURITY, size=48 if mobile else 64, color="white"),
                            ft.Container(height=20),
                            ft.Text("Vérification de sécurité", size=18 if mobile else 22, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
                            ft.Container(height=1, bgcolor="#FFFFFF55", width=60, margin=ft.margin.symmetric(vertical=24)),
                            ft.Text(
                                "Votre compte est protégé par\nune double authentification.",
                                size=13, color="#DDDDDD", text_align=ft.TextAlign.CENTER,
                                visible=not mobile,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    bgcolor="#0D2136B3",
                    padding=ft.padding.symmetric(horizontal=20, vertical=30) if mobile else 50,
                    expand=True,
                    alignment=ft.alignment.center,
                ),
                image_src=IMAGE_FOND,
                image_fit=ft.ImageFit.COVER,
                width=None if mobile else 420,
            )

            panneau_formulaire = ft.Container(
                content=ft.Column(
                    controls=[
                        bandeau_officiel(),
                        ft.Container(
                            content=vue_mfa(page, email, on_mfa_success),
                            expand=True,
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
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
            from views.dashboard.dashboard import vue_dashboard
            page.controls.append(vue_dashboard(page, afficher_login))

        page.update()

    afficher_login()


def _vue_login_avec_inscription(page, on_success, aller_inscription, mobile=False):
    from api_client import client

    largeur_champ = None if mobile else 360

    email_input = ft.TextField(
        label="Adresse email",
        hint_text="exemple@email.com",
        prefix_icon=ft.icons.EMAIL_OUTLINED,
        border_radius=4,
        border_color="#CCCCCC",
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
        border_radius=4,
        border_color="#CCCCCC",
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
        height=46,
        bgcolor=COULEURS["primaire"],
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=4)),
        on_click=on_login,
    )

    btn_inscription = ft.ElevatedButton(
        text="Créer un compte",
        width=largeur_champ,
        expand=mobile,
        height=44,
        bgcolor=COULEURS["primaire"],
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=4)),
        on_click=lambda e: aller_inscription(),
    )

    contenu_colonne = [
        ft.Container(height=40 if mobile else 60),
        ft.Text("CONNEXION", size=13, weight=ft.FontWeight.W_500, color=COULEURS["texte_clair"], text_align=ft.TextAlign.CENTER),
        ft.Container(height=6),
        ft.Text("Accédez à votre espace", size=22 if mobile else 24, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
        ft.Container(height=28),
        email_input,
        ft.Container(height=14),
        password_input,
        ft.Container(height=6),
        message,
        ft.Container(height=18),
        btn_login,
        loading,
        ft.Container(height=20),
        ft.Divider(color="#E0E0E0"),
        ft.Container(height=14),
        ft.Text("Pas encore de compte ?", size=13, color=COULEURS["texte_clair"], text_align=ft.TextAlign.CENTER),
        ft.Container(height=8),
        btn_inscription,
        ft.Container(height=30),
    ]

    return ft.Container(
        content=ft.Column(
            controls=contenu_colonne,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=10) if mobile else ft.padding.symmetric(horizontal=50),
        alignment=ft.alignment.center,
        expand=True,
    )


import os

ft.app(
    target=main,
    view=ft.AppView.WEB_BROWSER,
    port=int(os.environ.get("PORT", 8550)),
    host="0.0.0.0",
)
