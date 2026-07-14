import flet as ft
from config import COULEURS


def vue_formulaire_paiement(page: ft.Page, on_success, on_cancel):
    from api_client import client

    # Récupérer toutes les réservations validées et en attente
    reservations_validees = client.get_reservations(statut="VALIDEE") or []
    reservations_attente = client.get_reservations(statut="EN_ATTENTE") or []
    reservations = reservations_validees + reservations_attente
    
    reservation_options = [
        ft.dropdown.Option(
            key=str(r.get("id")),
            text=f"{r.get('numero')} — {r.get('defunt', {}).get('prenom', '')} {r.get('defunt', {}).get('nom', '')}",
        )
        for r in reservations
    ]
    reservation_options.insert(0, ft.dropdown.Option(key="", text="— Aucune réservation —"))

    reservation_dropdown = ft.Dropdown(
        label="Réservation associée (optionnel)",
        options=reservation_options,
        border_radius=8,
        focused_border_color=COULEURS["primaire"],
        expand=True,
    )

    montant_input = ft.TextField(
        label="Montant (FCFA)",
        prefix_icon=ft.icons.MONEY,
        border_radius=8,
        focused_border_color=COULEURS["primaire"],
        color="black",
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
    )

    canal_dropdown = ft.Dropdown(
        label="Canal de paiement",
        options=[
            ft.dropdown.Option("ESPECES", "Espèces"),
            ft.dropdown.Option("AIRTEL_MONEY", "Airtel Money"),
            ft.dropdown.Option("MTN_MOMO", "MTN Mobile Money"),
            ft.dropdown.Option("VIREMENT", "Virement bancaire"),
            ft.dropdown.Option("CHEQUE", "Chèque"),
        ],
        border_radius=8,
        focused_border_color=COULEURS["primaire"],
        expand=True,
    )

    numero_transaction_input = ft.TextField(
        label="Numéro de transaction (optionnel)",
        prefix_icon=ft.icons.RECEIPT,
        border_radius=8,
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )

    notes_input = ft.TextField(
        label="Notes (optionnel)",
        multiline=True,
        min_lines=2,
        border_radius=8,
        focused_border_color=COULEURS["primaire"],
        color="black",
        expand=True,
    )

    message = ft.Text("", color=COULEURS["danger"], size=13)
    loading = ft.ProgressRing(width=20, height=20, visible=False)

    def on_soumettre(e):
        if not montant_input.value or not canal_dropdown.value:
            message.value = "Veuillez remplir le montant et le canal de paiement."
            page.update()
            return

        try:
            montant = float(montant_input.value)
            if montant <= 0:
                message.value = "Le montant doit être supérieur à 0."
                page.update()
                return
        except ValueError:
            message.value = "Montant invalide."
            page.update()
            return

        loading.visible = True
        btn_soumettre.disabled = True
        message.value = ""
        page.update()

        data = {
            "montant_xaf": montant,
            "canal": canal_dropdown.value,
            "numero_transaction": numero_transaction_input.value or "",
            "notes": notes_input.value or "",
        }

        if reservation_dropdown.value:
            data["reservation_id"] = int(reservation_dropdown.value)

        result = client.enregistrer_paiement(data)

        loading.visible = False
        btn_soumettre.disabled = False

        if result.get("reference"):
            on_success(result)
        else:
            message.value = result.get("message", "Erreur lors de l'enregistrement.")

        page.update()

    btn_soumettre = ft.ElevatedButton(
        text="Enregistrer le paiement",
        icon=ft.icons.SAVE,
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

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Row(
                    controls=[
                        ft.Icon(ft.icons.PAYMENT, color=COULEURS["primaire"], size=28),
                        ft.Text(
                            "Enregistrer un paiement",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=COULEURS["titre"],
                        ),
                    ],
                    spacing=10,
                ),
                ft.Text(
                    "Enregistrez un paiement reçu en espèces ou via Mobile Money.",
                    size=13,
                    color=COULEURS["texte_clair"],
                ),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Informations du paiement", size=15, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                            ft.Container(height=10),
                            ft.Row(controls=[reservation_dropdown]),
                            ft.Row(controls=[montant_input, canal_dropdown], spacing=10),
                            ft.Row(controls=[numero_transaction_input]),
                            ft.Row(controls=[notes_input]),
                        ],
                        spacing=10,
                    ),
                    bgcolor=COULEURS["blanc"],
                    border_radius=12,
                    padding=20,
                    shadow=ft.BoxShadow(blur_radius=6, color="#1A000000", offset=ft.Offset(0, 2)),
                ),
                ft.Container(height=15),
                message,
                loading,
                ft.Row(
                    controls=[btn_annuler, btn_soumettre],
                    spacing=15,
                ),
                ft.Container(height=20),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )