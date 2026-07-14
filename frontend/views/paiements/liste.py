import flet as ft
from config import COULEURS


CANAL_LABELS = {
    "ESPECES": "Espèces",
    "AIRTEL_MONEY": "Airtel Money",
    "MTN_MOMO": "MTN MoMo",
    "VIREMENT": "Virement",
    "CHEQUE": "Chèque",
}

CANAL_ICONES = {
    "ESPECES": ft.icons.MONEY,
    "AIRTEL_MONEY": ft.icons.PHONE_ANDROID,
    "MTN_MOMO": ft.icons.PHONE_ANDROID,
    "VIREMENT": ft.icons.ACCOUNT_BALANCE,
    "CHEQUE": ft.icons.RECEIPT,
}

STATUT_COULEURS = {
    "EN_ATTENTE": "#fd7e14",
    "CONFIRME": "#28a745",
    "ECHEC": "#dc3545",
    "REMBOURSE": "#6c757d",
}


def vue_paiements(page: ft.Page):
    from api_client import client

    liste = ft.Column(spacing=10)
    zone_contenu = ft.Column(controls=[liste], expand=True, scroll=ft.ScrollMode.AUTO)

    def carte_paiement(p):
        canal = p.get("canal", "")
        statut = p.get("statut", "")
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            CANAL_ICONES.get(canal, ft.icons.PAYMENT),
                            color="white",
                            size=24,
                        ),
                        bgcolor=COULEURS["primaire"],
                        border_radius=10,
                        padding=12,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                p.get("reference", ""),
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=COULEURS["primaire"],
                            ),
                            ft.Text(
                                f"Canal : {CANAL_LABELS.get(canal, canal)}",
                                size=12,
                                color=COULEURS["texte_clair"],
                            ),
                            ft.Text(
                                f"Date : {p.get('date_paiement', '')[:10]}",
                                size=12,
                                color=COULEURS["texte_clair"],
                            ),
                        ],
                        spacing=3,
                        expand=True,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                f"{int(p.get('montant_xaf', 0)):,} FCFA".replace(",", " "),
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=COULEURS["texte"],
                            ),
                            ft.Container(
                                content=ft.Text(
                                    statut,
                                    size=11,
                                    color="white",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=STATUT_COULEURS.get(statut, "#6c757d"),
                                border_radius=20,
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            ),
                            *([
                                ft.Text(
                                    f"Solde restant : {solde.get('solde_restant_xaf', 0):,} FCFA".replace(",", " "),
                                    size=11,
                                    color="#dc3545" if not solde.get("est_solde") else "#28a745",
                                    weight=ft.FontWeight.BOLD,
                                )
                            ] if (rid := p.get("reservation_id")) and (solde := client.get_solde_reservation(rid)) and not solde.get("error") else []),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=5,
                    ),
                ],
                spacing=15,
            ),
            bgcolor=COULEURS["blanc"],
            border_radius=12,
            padding=15,
            shadow=ft.BoxShadow(blur_radius=6, color="#1A000000", offset=ft.Offset(0, 2)),
        )

    def charger_liste(statut=None):
        data = client.get_paiements(statut=statut)
        liste.controls.clear()
        if not data:
            liste.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.icons.PAYMENT, size=50, color=COULEURS["texte_clair"]),
                            ft.Text("Aucun paiement trouvé", size=15, color=COULEURS["texte_clair"]),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    padding=50,
                )
            )
        else:
            for p in data:
                liste.controls.append(carte_paiement(p))

    def afficher_formulaire(e):
        from views.paiements.formulaire import vue_formulaire_paiement

        def on_success(result):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(result.get("message", "Paiement enregistré !"), color="white"),
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

        formulaire = vue_formulaire_paiement(page, on_success, on_cancel)
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
                        ft.Text("Paiements", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "Enregistrer un paiement",
                            icon=ft.icons.ADD,
                            bgcolor=COULEURS["success"],
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=afficher_formulaire,
                        ),
                    ],
                ),
                ft.Text("Historique des transactions", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=15),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Tous",
                            bgcolor=COULEURS["primaire"],
                            color="white",
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=lambda e: [charger_liste(None), page.update()],
                        ),
                        ft.OutlinedButton(
                            "Confirmés",
                            style=ft.ButtonStyle(color="#28a745"),
                            on_click=lambda e: [charger_liste("CONFIRME"), page.update()],
                        ),
                        ft.OutlinedButton(
                            "En attente",
                            style=ft.ButtonStyle(color="#fd7e14"),
                            on_click=lambda e: [charger_liste("EN_ATTENTE"), page.update()],
                        ),
                    ],
                    spacing=10,
                ),
                ft.Container(height=10),
                zone_contenu,
            ],
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )