import flet as ft
from config import COULEURS

BREAKPOINT_MOBILE = 700


def vue_formulaire_utilisateur(page: ft.Page, on_success, on_cancel):
    from api_client import client

    mobile = (page.width or 1200) < BREAKPOINT_MOBILE

    email_input = ft.TextField(
        label="Email",
        prefix_icon=ft.icons.EMAIL,
        border_radius=8,
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )
    password_input = ft.TextField(
        label="Mot de passe",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.icons.LOCK,
        border_radius=8,
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )
    nom_input = ft.TextField(
        label="Nom",
        prefix_icon=ft.icons.PERSON,
        border_radius=8,
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )
    prenom_input = ft.TextField(
        label="Prénom",
        prefix_icon=ft.icons.PERSON,
        border_radius=8,
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )
    telephone_input = ft.TextField(
        label="Téléphone",
        prefix_icon=ft.icons.PHONE,
        border_radius=8,
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )
    role_dropdown = ft.Dropdown(
        label="Rôle",
        options=[
            ft.dropdown.Option("ADMIN", "Administrateur"),
            ft.dropdown.Option("SECRETARIAT", "Secrétariat"),
            ft.dropdown.Option("AGENT", "Agent terrain"),
            ft.dropdown.Option("CLIENT", "Client"),
        ],
        value="CLIENT",
        border_radius=8,
        focused_border_color=COULEURS["primaire"],
        expand=True,
    )

    message = ft.Text("", color=COULEURS["danger"], size=13)
    loading = ft.ProgressRing(width=20, height=20, visible=False)

    def on_soumettre(e):
        if not all([email_input.value, password_input.value, nom_input.value, prenom_input.value]):
            message.value = "Veuillez remplir tous les champs obligatoires."
            page.update()
            return

        loading.visible = True
        btn_soumettre.disabled = True
        message.value = ""
        page.update()

        data = {
            "email": email_input.value,
            "password": password_input.value,
            "nom": nom_input.value,
            "prenom": prenom_input.value,
            "telephone": telephone_input.value or "",
            "role_nom": role_dropdown.value,
        }

        result = client.creer_utilisateur(data)

        loading.visible = False
        btn_soumettre.disabled = False

        if "créé" in result.get("message", ""):
            on_success(result)
        else:
            message.value = result.get("message", "Erreur lors de la création.")

        page.update()

    btn_soumettre = ft.ElevatedButton(
        text="Créer l'utilisateur",
        icon=ft.icons.PERSON_ADD,
        bgcolor=COULEURS["primaire"],
        color="white",
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=on_soumettre,
        expand=True,
    )

    btn_annuler = ft.OutlinedButton(
        text="Annuler",
        height=45,
        style=ft.ButtonStyle(
            color=COULEURS["danger"],
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=lambda e: on_cancel(),
        expand=True,
    )

    def paire(champ_a, champ_b):
        """Sur mobile, empile les champs. Sur desktop, les met côte à côte."""
        if mobile:
            return ft.Column(controls=[champ_a, champ_b], spacing=10)
        return ft.Row(controls=[champ_a, champ_b], spacing=10)

    actions_boutons = (
        ft.Column(controls=[btn_soumettre, btn_annuler], spacing=10)
        if mobile else
        ft.Row(controls=[btn_annuler, btn_soumettre], spacing=15)
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Row(
                    controls=[
                        ft.Icon(ft.icons.PERSON_ADD, color=COULEURS["primaire"], size=28),
                        ft.Text(
                            "Nouvel utilisateur",
                            size=20 if mobile else 24,
                            weight=ft.FontWeight.BOLD,
                            color=COULEURS["titre"],
                        ),
                    ],
                    spacing=10,
                ),
                ft.Text(
                    "Créer un nouveau compte utilisateur.",
                    size=13,
                    color=COULEURS["texte_clair"],
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Informations du compte", size=15, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                            ft.Container(height=10),
                            paire(nom_input, prenom_input),
                            ft.Container(height=10),
                            paire(email_input, telephone_input),
                            ft.Container(height=10),
                            paire(password_input, role_dropdown),
                        ],
                        spacing=0,
                    ),
                    bgcolor=COULEURS["blanc"],
                    border_radius=12,
                    padding=20 if not mobile else 15,
                    shadow=ft.BoxShadow(blur_radius=6, color="#1A000000", offset=ft.Offset(0, 2)),
                ),
                ft.Container(height=15),
                message,
                loading,
                actions_boutons,
                ft.Container(height=20),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        padding=ft.padding.all(15) if mobile else ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )