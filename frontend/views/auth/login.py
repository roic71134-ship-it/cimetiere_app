import flet as ft
from config import COULEURS, APP_NOM


def vue_login(page: ft.Page, on_success):
    """Page de connexion — Étape 1 : Email + Mot de passe."""

    email_input = ft.TextField(
        label="Adresse email",
        hint_text="exemple@email.com",
        prefix_icon=ft.icons.EMAIL_OUTLINED,
        border_radius=10,
        focused_border_color=COULEURS["primaire"],
        color="black",
        width=380,
    )

    password_input = ft.TextField(
        label="Mot de passe",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK_OUTLINED,
        border_radius=10,
        focused_border_color=COULEURS["primaire"],
        color="black",
        width=380,
    )

    message = ft.Text("", color=COULEURS["danger"], size=13)
    loading = ft.ProgressRing(width=20, height=20, visible=False)

    def on_login(e):
        from api_client import client

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
        width=380,
        height=45,
        bgcolor=COULEURS["primaire"],
        color=COULEURS["blanc"],
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=on_login,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=40),
                ft.Icon(
                    ft.icons.ACCOUNT_BALANCE_OUTLINED,
                    size=60,
                    color=COULEURS["primaire"],
                ),
                ft.Container(height=10),
                ft.Text(
                    APP_NOM,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=COULEURS["primaire"],
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Système de gestion du cimetière",
                    size=13,
                    color=COULEURS["texte_clair"],
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=30),
                ft.Text(
                    "Connexion",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=COULEURS["titre"],
                ),
                ft.Container(height=15),
                email_input,
                ft.Container(height=10),
                password_input,
                ft.Container(height=5),
                message,
                ft.Container(height=15),
                btn_login,
                ft.Container(height=10),
                loading,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.padding.all(30),
        alignment=ft.alignment.center,
        expand=True,
    )