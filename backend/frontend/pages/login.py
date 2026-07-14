"""Page de connexion avec MFA en 2 étapes."""
import flet as ft
from utils.api_client import api_post, set_token


def LoginPage(page: ft.Page, on_login_success):
    """Retourne le contenu de la page de connexion."""

    # Étape 1 : email/password
    email_field = ft.TextField(
        label="Adresse email",
        prefix_icon=ft.icons.EMAIL_OUTLINED,
        width=350,
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    password_field = ft.TextField(
        label="Mot de passe",
        prefix_icon=ft.icons.LOCK_OUTLINED,
        password=True,
        can_reveal_password=True,
        width=350,
    )

    # Étape 2 : code MFA
    mfa_field = ft.TextField(
        label="Code MFA (reçu par email)",
        prefix_icon=ft.icons.VERIFIED_USER_OUTLINED,
        width=350,
        max_length=6,
        keyboard_type=ft.KeyboardType.NUMBER,
        visible=False,
    )

    status_text = ft.Text("", color=ft.colors.RED_600, size=13)
    loading = ft.ProgressRing(visible=False, width=24, height=24)

    etape = [1]  # Utiliser une liste pour mutabilité dans closure

    def show_loading(val: bool):
        loading.visible = val
        page.update()

    def etape1_submit(e):
        if not email_field.value or not password_field.value:
            status_text.value = "Veuillez remplir tous les champs."
            page.update()
            return

        show_loading(True)
        ok, data = api_post("/auth/login", {
            "email": email_field.value,
            "password": password_field.value
        }, auth=False)
        show_loading(False)

        if ok:
            status_text.color = ft.colors.GREEN_700
            status_text.value = data.get("message", "Code envoyé.")
            # Passer à l'étape 2
            email_field.visible = False
            password_field.visible = False
            btn_login.text = "Vérifier le code"
            btn_login.on_click = etape2_submit
            mfa_field.visible = True
            etape[0] = 2
        else:
            status_text.color = ft.colors.RED_600
            status_text.value = data.get("message", "Erreur de connexion.")
        page.update()

    def etape2_submit(e):
        if not mfa_field.value:
            status_text.value = "Entrez le code MFA."
            page.update()
            return

        show_loading(True)
        ok, data = api_post("/auth/verify-mfa", {
            "email": email_field.value,
            "code": mfa_field.value,
        }, auth=False)
        show_loading(False)

        if ok:
            set_token(data["access_token"], {
                "user_id": data["user_id"],
                "role": data["role"],
                "nom_complet": data["nom_complet"],
            })
            on_login_success(data["role"])
        else:
            status_text.color = ft.colors.RED_600
            status_text.value = data.get("message", "Code incorrect.")
        page.update()

    btn_login = ft.ElevatedButton(
        text="Se connecter",
        on_click=etape1_submit,
        width=350,
        height=45,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_800,
        ),
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.icons.CHURCH, size=64, color=ft.colors.BLUE_800),
                ft.Text("Gestion de Cimetière", size=24, weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE_900),
                ft.Text("GI2 — 2026", size=13, color=ft.colors.GREY_600),
                ft.Divider(height=20),
                email_field,
                password_field,
                mfa_field,
                status_text,
                loading,
                btn_login,
                ft.TextButton(
                    "Créer un compte client",
                    on_click=lambda e: page.go("/register"),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        alignment=ft.alignment.center,
        expand=True,
        padding=40,
    )
