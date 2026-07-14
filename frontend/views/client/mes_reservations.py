import flet as ft
from config import COULEURS, API_BASE_URL


STATUT_COULEURS = {
    "EN_ATTENTE": "#fd7e14",
    "VALIDEE": "#28a745",
    "REFUSEE": "#dc3545",
    "ANNULEE": "#6c757d",
    "EXPIREE": "#6c757d",
}

STATUT_LABELS = {
    "EN_ATTENTE": "En attente",
    "VALIDEE": "Validée",
    "REFUSEE": "Refusée",
    "ANNULEE": "Annulée",
    "EXPIREE": "Expirée",
}

TYPE_LABELS = {
    "TEMPORAIRE": "Temporaire (5 ans)",
    "TRENTENAIRE": "Trentenaire (30 ans)",
    "PERPETUELLE": "Perpétuelle",
    "FAMILIALE": "Familiale",
}


def _get_solde_texte(client, reservation_id):
    try:
        solde = client.get_solde_reservation(reservation_id)
        if solde.get("error"):
            return ""
        if solde.get("est_solde"):
            return "✅ Entièrement payé"
        restant = int(solde.get("solde_restant_xaf", 0))
        paye = int(solde.get("total_paye_xaf", 0))
        return f"💳 Payé : {paye:,} FCFA | Restant : {restant:,} FCFA".replace(",", " ")
    except Exception:
        return ""


def vue_mes_reservations(page: ft.Page, client):
    reservations = client.get_reservations()
    liste = ft.Column(spacing=12)

    def snack(msg, couleur=None):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=couleur or COULEURS["success"],
        )
        page.snack_bar.open = True
        page.update()

    def ouvrir_paiement_mobile(reservation_id, montant_total, canal):
        solde = client.get_solde_reservation(reservation_id)
        solde_restant = int(solde.get("solde_restant_xaf", montant_total))

        canal_label = "MTN MoMo" if canal == "MTN_MOMO" else "Airtel Money"
        canal_color = "#FFCC00" if canal == "MTN_MOMO" else "#FF0000"
        canal_text_color = "#000000" if canal == "MTN_MOMO" else "white"

        tel_f = ft.TextField(color="white", 
            label="Numéro de téléphone *",
            hint_text="ex: 06xxxxxxxx",
            prefix_icon=ft.icons.PHONE,
            border_radius=8,
            keyboard_type=ft.KeyboardType.PHONE,
        )
        montant_f = ft.TextField(color="white", 
            label="Montant à payer (FCFA) *",
            value=str(solde_restant),
            prefix_icon=ft.icons.MONEY,
            border_radius=8,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        msg_f = ft.Text("", size=13)

        def confirmer(e):
            if not tel_f.value or not montant_f.value:
                msg_f.value = "Veuillez remplir tous les champs."
                msg_f.color = COULEURS["danger"]
                page.update()
                return
            try:
                montant = float(montant_f.value)
                if montant <= 0:
                    msg_f.value = "Le montant doit être supérieur à 0."
                    msg_f.color = COULEURS["danger"]
                    page.update()
                    return
            except ValueError:
                msg_f.value = "Montant invalide."
                msg_f.color = COULEURS["danger"]
                page.update()
                return

            msg_f.value = f"⏳ Traitement du paiement {canal_label}..."
            msg_f.color = "#fd7e14"
            page.update()

            res = client.simuler_mobile_money(reservation_id, montant, canal, tel_f.value)

            if res.get("reference"):
                msg_f.value = f"✅ {res['message']}"
                msg_f.color = COULEURS["success"]
                page.update()
                dlg.open = False
                page.update()
                snack(f"✅ Paiement {canal_label} confirmé !")
                # Rafraîchir la liste
                nouvelle_vue = vue_mes_reservations(page, client)
                page.update()
            else:
                msg_f.value = res.get("message", "Erreur lors du paiement.")
                msg_f.color = COULEURS["danger"]
                page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Paiement {canal_label}", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=400,
                content=ft.Column(tight=True, spacing=12, controls=[
                    ft.Container(
                        content=ft.Row(spacing=10, controls=[
                            ft.Icon(ft.icons.PHONE_ANDROID, size=30,
                                color=canal_color if canal == "AIRTEL_MONEY" else "#000"),
                            ft.Column(spacing=2, controls=[
                                ft.Text(canal_label, size=16, weight=ft.FontWeight.BOLD),
                                ft.Text("Paiement Mobile Money simulé", size=12, color=COULEURS["texte_clair"]),
                            ]),
                        ]),
                        bgcolor="#F5F5F5",
                        border_radius=8,
                        padding=12,
                    ),
                    ft.Text(
                        f"Solde restant : {solde_restant:,} FCFA".replace(",", " "),
                        size=13,
                        color=COULEURS["texte_clair"],
                    ),
                    tel_f,
                    montant_f,
                    msg_f,
                ]),
            ),
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                ft.ElevatedButton(
                    "Confirmer le paiement",
                    bgcolor=canal_color,
                    color=canal_text_color,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=confirmer,
                ),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def badge(statut):
        return ft.Container(
            content=ft.Text(STATUT_LABELS.get(statut, statut), size=11, color="white", weight=ft.FontWeight.BOLD),
            bgcolor=STATUT_COULEURS.get(statut, "#6c757d"),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=12, vertical=5),
        )

    def carte(r):
        statut = r.get("statut", "")
        defunt = r.get("defunt", {})
        montant = int(r.get("montant_total_xaf", 0))
        rid = r.get("id")

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.icons.BOOK, color="white", size=22),
                                bgcolor=COULEURS["primaire"],
                                border_radius=10,
                                padding=12,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(r.get("numero", ""), size=16, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                                    ft.Text(f"Défunt : {defunt.get('prenom', '')} {defunt.get('nom', '')}", size=13, color=COULEURS["texte"]),
                                    ft.Text(f"Type : {TYPE_LABELS.get(r.get('type_concession', ''), '')}", size=12, color=COULEURS["texte_clair"]),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Column(
                                controls=[
                                    badge(statut),
                                    ft.Container(height=5),
                                    ft.Text(f"{montant:,} FCFA".replace(",", " "), size=14, weight=ft.FontWeight.BOLD, color=COULEURS["texte"]),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=0,
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.Divider(height=1, color="#F0F0F0"),
                    ft.Row(
                        controls=[
                            ft.Icon(ft.icons.CALENDAR_TODAY, size=14, color=COULEURS["texte_clair"]),
                            ft.Text(f"Soumis le {r.get('date_soumission', '')[:10]}", size=12, color=COULEURS["texte_clair"]),
                            ft.Container(expand=True),
                            ft.Text(
                                f"Validé le {r.get('date_validation', '')[:10]}" if r.get("date_validation") else "",
                                size=12,
                                color="#28a745",
                            ),
                        ],
                        spacing=6,
                    ),
                    *([
                        ft.TextButton(
                            "📄 Télécharger la facture",
                            style=ft.ButtonStyle(color=COULEURS["primaire"]),
                            on_click=lambda e, rid=rid: page.launch_url(
                                f"{API_BASE_URL}/reservations/{rid}/facture-pdf"
                            ),
                        ),
                        ft.Container(
                            content=ft.Row(spacing=10, controls=[
                                ft.Icon(ft.icons.ACCOUNT_BALANCE_WALLET, size=16, color="#1565C0"),
                                ft.Text(
                                    _get_solde_texte(client, rid),
                                    size=13,
                                    color="#1565C0",
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ]),
                            bgcolor="#E3F2FD",
                            border_radius=8,
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        ),
                        ft.Row(spacing=10, controls=[
                            ft.ElevatedButton(
                                "📱 Payer MTN MoMo",
                                bgcolor="#FFCC00",
                                color="#000000",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                on_click=lambda e, rid=rid, mont=montant: ouvrir_paiement_mobile(rid, mont, "MTN_MOMO"),
                            ),
                            ft.ElevatedButton(
                                "📱 Payer Airtel Money",
                                bgcolor="#FF0000",
                                color="white",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                on_click=lambda e, rid=rid, mont=montant: ouvrir_paiement_mobile(rid, mont, "AIRTEL_MONEY"),
                            ),
                        ]),
                    ] if statut == "VALIDEE" else [ft.Container()]),
                ],
                spacing=10,
            ),
            bgcolor="white",
            border_radius=14,
            padding=18,
            shadow=ft.BoxShadow(blur_radius=8, color="#0D000000", offset=ft.Offset(0, 2)),
        )

    if not reservations:
        liste.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.INBOX, size=60, color=COULEURS["texte_clair"]),
                        ft.Text("Aucune réservation", size=16, color=COULEURS["texte_clair"]),
                        ft.Text("Vos demandes de réservation apparaîtront ici.", size=13, color=COULEURS["texte_clair"], text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.alignment.center,
                padding=60,
            )
        )
    else:
        for r in reservations:
            liste.controls.append(carte(r))

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=25),
                ft.Text("Mes réservations", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Text("Historique de vos demandes d'inhumation", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=20),
                liste,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )