import flet as ft
from config import COULEURS, APP_NOM

BREAKPOINT_MOBILE = 700
IMAGE_FOND = "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80"


def vue_inscription(page: ft.Page, on_success, on_login):
    mobile = (page.width or 1200) < BREAKPOINT_MOBILE

    def label_section(texte):
        return ft.Text(texte, size=12, weight=ft.FontWeight.W_500, color=COULEURS["primaire"])

    prenom_input = ft.TextField(
        label="Prénom *",
        prefix_icon=ft.icons.PERSON,
        border_radius=4,
        border_color="#CCCCCC",
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )
    nom_input = ft.TextField(
        label="Nom *",
        prefix_icon=ft.icons.PERSON,
        border_radius=4,
        border_color="#CCCCCC",
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )
    email_input = ft.TextField(
        label="Adresse email *",
        prefix_icon=ft.icons.EMAIL,
        border_radius=4,
        border_color="#CCCCCC",
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
        keyboard_type=ft.KeyboardType.EMAIL,
    )
    telephone_input = ft.TextField(
        label="Téléphone *",
        prefix_icon=ft.icons.PHONE,
        border_radius=4,
        border_color="#CCCCCC",
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )
    adresse_input = ft.TextField(
        label="Adresse",
        prefix_icon=ft.icons.LOCATION_ON,
        border_radius=4,
        border_color="#CCCCCC",
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )
    password_input = ft.TextField(
        label="Mot de passe *",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK,
        border_radius=4,
        border_color="#CCCCCC",
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )
    confirm_password_input = ft.TextField(
        label="Confirmer le mot de passe *",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK,
        border_radius=4,
        border_color="#CCCCCC",
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )

    message = ft.Text("", color=COULEURS["danger"], size=13)
    loading = ft.ProgressRing(width=20, height=20, visible=False)

    def on_inscrire(e):
        from api_client import client

        if not all([prenom_input.value, nom_input.value, email_input.value,
                    telephone_input.value, password_input.value, confirm_password_input.value]):
            message.value = "Veuillez remplir tous les champs obligatoires (*)"
            page.update()
            return

        if password_input.value != confirm_password_input.value:
            message.value = "Les mots de passe ne correspondent pas."
            page.update()
            return

        if len(password_input.value) < 8:
            message.value = "Le mot de passe doit contenir au moins 8 caractères."
            page.update()
            return

        loading.visible = True
        btn_inscrire.disabled = True
        message.value = ""
        page.update()

        data = {
            "email": email_input.value,
            "password": password_input.value,
            "nom": nom_input.value,
            "prenom": prenom_input.value,
            "telephone": telephone_input.value,
            "adresse": adresse_input.value or "",
            "role_nom": "CLIENT",
        }

        result = client.inscrire(data)

        loading.visible = False
        btn_inscrire.disabled = False

        if "créé" in result.get("message", ""):
            on_success(email_input.value)
        else:
            message.value = result.get("message", "Erreur lors de l'inscription.")

        page.update()

    btn_inscrire = ft.ElevatedButton(
        text="Créer mon compte",
        width=None if mobile else 400,
        expand=mobile,
        height=48,
        bgcolor=COULEURS["primaire"],
        color="white",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=4)),
        on_click=on_inscrire,
    )

    ligne_noms = (
        ft.Column(controls=[prenom_input, nom_input], spacing=8)
        if mobile else
        ft.Row(controls=[prenom_input, nom_input], spacing=10)
    )
    ligne_contact = (
        ft.Column(controls=[email_input, telephone_input], spacing=8)
        if mobile else
        ft.Row(controls=[email_input, telephone_input], spacing=10)
    )
    ligne_mdp = (
        ft.Column(controls=[password_input, confirm_password_input], spacing=8)
        if mobile else
        ft.Row(controls=[password_input, confirm_password_input], spacing=10)
    )

    panneau_gauche = ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("🦅", size=44 if mobile else 60),
                    ft.Container(height=10),
                    ft.Text(APP_NOM, size=16 if mobile else 20, weight=ft.FontWeight.BOLD, color="white", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=6),
                    ft.Text("SYSTÈME DE GESTION", size=11, weight=ft.FontWeight.W_500, color="#CCCCCC", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=1, bgcolor="#FFFFFF55", width=60, margin=ft.margin.symmetric(vertical=20)),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(controls=[ft.Icon(ft.icons.CHECK_CIRCLE, color="#4CAF50", size=16), ft.Text("Réservez un caveau en ligne", color="white", size=13)], spacing=8),
                                ft.Row(controls=[ft.Icon(ft.icons.CHECK_CIRCLE, color="#4CAF50", size=16), ft.Text("Suivez vos demandes", color="white", size=13)], spacing=8),
                                ft.Row(controls=[ft.Icon(ft.icons.CHECK_CIRCLE, color="#4CAF50", size=16), ft.Text("Payez en toute sécurité", color="white", size=13)], spacing=8),
                                ft.Row(controls=[ft.Icon(ft.icons.CHECK_CIRCLE, color="#4CAF50", size=16), ft.Text("Accédez à la carte interactive", color="white", size=13)], spacing=8),
                            ],
                            spacing=10 if mobile else 12,
                        ),
                        visible=not mobile,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor="#0D2136B3",
            padding=ft.padding.symmetric(horizontal=20, vertical=20) if mobile else 40,
            expand=True,
            alignment=ft.alignment.center,
        ),
        image_src=IMAGE_FOND,
        image_fit=ft.ImageFit.COVER,
        width=None if mobile else 380,
    )

    panneau_formulaire = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=15 if mobile else 20),
                ft.Text("INSCRIPTION", size=13, weight=ft.FontWeight.W_500, color=COULEURS["texte_clair"], text_align=ft.TextAlign.CENTER),
                ft.Container(height=6),
                ft.Text("Créer un compte", size=20 if mobile else 24, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
                ft.Text("Rejoignez le portail du cimetière municipal", size=12 if mobile else 13, color=COULEURS["texte_clair"], text_align=ft.TextAlign.CENTER),
                ft.Container(height=24),

                label_section("INFORMATIONS PERSONNELLES"),
                ft.Container(height=8),
                ligne_noms,
                ft.Container(height=20),

                label_section("COORDONNÉES"),
                ft.Container(height=8),
                ligne_contact,
                ft.Container(height=8),
                adresse_input,
                ft.Container(height=20),

                label_section("SÉCURITÉ"),
                ft.Container(height=8),
                ligne_mdp,

                ft.Container(height=8),
                message,
                ft.Container(height=14),
                btn_inscrire,
                loading,
                ft.Container(height=14),
                ft.Row(
                    controls=[
                        ft.Text("Déjà un compte ?", size=13, color=COULEURS["texte_clair"]),
                        ft.TextButton(
                            "Se connecter",
                            style=ft.ButtonStyle(color=COULEURS["primaire"]),
                            on_click=lambda e: on_login(),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.START if not mobile else ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        expand=True,
        bgcolor="white",
        padding=ft.padding.symmetric(horizontal=20, vertical=10) if mobile else ft.padding.symmetric(horizontal=40, vertical=10),
    )

    if mobile:
        layout = ft.Column(
            controls=[panneau_gauche, panneau_formulaire],
            expand=True,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        )
    else:
        layout = ft.Row(
            controls=[panneau_gauche, panneau_formulaire],
            expand=True,
            spacing=0,
        )

    return ft.Container(content=layout, expand=True)
