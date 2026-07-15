import flet as ft
from config import COULEURS, APP_NOM


def vue_mfa(page: ft.Page, email: str, on_success):
    """Page MFA — Étape 2 : Confirmation d'identité."""

    code_input = ft.TextField(
        label="Code de vérification",
        hint_text="000000",
        prefix_icon=ft.icons.SECURITY_OUTLINED,
        border_radius=10,
        focused_border_color=COULEURS["primaire"],
        color="black",
        width=380,
        max_length=6,
        text_align=ft.TextAlign.CENTER,
        text_size=24,
    )

    message = ft.Text("", color=COULEURS["danger"], size=13)
    loading = ft.ProgressRing(width=20, height=20, visible=False)

    def on_verify(e):
        from api_client import client

        if not code_input.value or len(code_input.value) < 6:
            message.value = "Veuillez entrer le code à 6 chiffres."
            page.update()
            return

        loading.visible = True
        btn_verify.disabled = True
        message.value = ""
        page.update()

        result = client.verify_mfa(email, code_input.value)

        loading.visible = False
        btn_verify.disabled = False

        if result.get("access"):
            on_success(result)
        else:
            message.value = result.get("error", "Code invalide ou expiré.")

        page.update()

    def on_retour(e):
        page.go("/login")
        page.update()

    btn_verify = ft.ElevatedButton(
        text="Confirmer le code",
        width=380,
        height=45,
        bgcolor=COULEURS["primaire"],
        color=COULEURS["blanc"],
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=on_verify,
    )

    btn_retour = ft.IconButton(
        icon=ft.icons.ARROW_BACK,
        icon_color=COULEURS["secondaire"],
        on_click=on_retour,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[btn_retour],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Container(height=20),
                ft.Text("🦅", size=60, text_align=ft.TextAlign.CENTER),
                ft.Container(height=10),
                ft.Text(
                    "Confirmation d'identité",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=COULEURS["primaire"],
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=10),
                ft.Text(
                    email,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=COULEURS["texte"],
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=30),
                code_input,
                ft.Container(height=5),
                message,
                ft.Container(height=15),
                btn_verify,
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
