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


def vue_reservations(page: ft.Page):
    from api_client import client

    def badge_statut(statut):
        return ft.Container(
            content=ft.Text(
                STATUT_LABELS.get(statut, statut),
                size=11, color="white", weight=ft.FontWeight.BOLD,
            ),
            bgcolor=STATUT_COULEURS.get(statut, "#6c757d"),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
        )

    def snack(msg, couleur=None):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=couleur or COULEURS["success"],
        )
        page.snack_bar.open = True
        page.update()

    def carte_reservation(r):
        rid = r.get("id")
        statut = r.get("statut", "")
        en_attente = statut == "EN_ATTENTE"

        motif_field = ft.TextField(color="white", 
            label="Motif du refus",
            hint_text="Précisez la raison du refus...",
            multiline=True, min_lines=2, max_lines=4, border_radius=8,
        )
        notes_field = ft.TextField(color="white", 
            label="Notes admin (optionnel)",
            hint_text="Remarques pour le client...",
            multiline=True, min_lines=2, max_lines=3, border_radius=8,
        )

        def ouvrir_facture(reservation_id):
            page.launch_url(f"{API_BASE_URL}/reservations/{reservation_id}/facture-pdf")

        def ouvrir_validation(e):
            notes_field.value = ""
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Valider la réservation", weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    width=400,
                    content=ft.Column(tight=True, controls=[
                        ft.Text(f"Réservation : {r.get('numero', '')}", size=13, color=COULEURS["texte_clair"]),
                        ft.Text(
                            f"Défunt : {r.get('defunt', {}).get('prenom', '')} {r.get('defunt', {}).get('nom', '')}",
                            size=13,
                        ),
                        ft.Container(height=10),
                        notes_field,
                    ]),
                ),
                actions_alignment=ft.MainAxisAlignment.END,
                actions=[
                    ft.TextButton("Annuler", on_click=lambda e: close_dlg()),
                    ft.ElevatedButton(
                        "✅ Valider",
                        bgcolor=COULEURS["success"], color="white",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=lambda e: faire_validation(),
                    ),
                ],
            )

            def close_dlg():
                dlg.open = False
                page.update()

            def faire_validation():
                dlg.open = False
                page.update()
                res = client.valider_reservation(rid, notes_field.value.strip())
                msg = res.get("message", "")
                if "validée" in msg.lower():
                    snack(f"✅ {msg}")
                else:
                    snack(msg or "Erreur lors de la validation", COULEURS["danger"])
                charger_liste()
                page.update()

            page.dialog = dlg
            dlg.open = True
            page.update()

        def ouvrir_refus(e):
            motif_field.value = ""
            motif_field.error_text = None
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Refuser la réservation", weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    width=400,
                    content=ft.Column(tight=True, controls=[
                        ft.Text(f"Réservation : {r.get('numero', '')}", size=13, color=COULEURS["texte_clair"]),
                        ft.Container(height=10),
                        motif_field,
                    ]),
                ),
                actions_alignment=ft.MainAxisAlignment.END,
                actions=[
                    ft.TextButton("Annuler", on_click=lambda e: close_dlg()),
                    ft.ElevatedButton(
                        "❌ Confirmer le refus",
                        bgcolor=COULEURS["danger"], color="white",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=lambda e: faire_refus(),
                    ),
                ],
            )

            def close_dlg():
                dlg.open = False
                page.update()

            def faire_refus():
                motif = motif_field.value.strip()
                if not motif:
                    motif_field.error_text = "Le motif est obligatoire"
                    page.update()
                    return
                dlg.open = False
                page.update()
                res = client.refuser_reservation(rid, motif)
                msg = res.get("message", "")
                if "refusée" in msg.lower():
                    snack(f"✅ {msg}")
                else:
                    snack(msg or "Erreur lors du refus", COULEURS["danger"])
                charger_liste()
                page.update()

            page.dialog = dlg
            dlg.open = True
            page.update()

        actions = ft.Row(spacing=10, controls=[
            ft.ElevatedButton(
                "✅ Valider",
                bgcolor=COULEURS["success"], color="white",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=ouvrir_validation,
            ),
            ft.OutlinedButton(
                "❌ Refuser",
                style=ft.ButtonStyle(
                    color=COULEURS["danger"],
                    side=ft.BorderSide(color=COULEURS["danger"], width=1),
                ),
                on_click=ouvrir_refus,
            ),
        ]) if en_attente else ft.Container()

        btn_facture = ft.TextButton(
            "📄 Télécharger la facture",
            style=ft.ButtonStyle(color=COULEURS["primaire"]),
            on_click=lambda e, rid=rid: ouvrir_facture(rid),
        )

        controls = [
            ft.Row(controls=[
                ft.Column(expand=True, spacing=3, controls=[
                    ft.Text(r.get("numero", ""), size=16, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                    ft.Text(
                        f"Défunt : {r.get('defunt', {}).get('prenom', '')} {r.get('defunt', {}).get('nom', '')}",
                        size=13, color=COULEURS["texte"],
                    ),
                    ft.Text(f"Type : {r.get('type_concession', '')}", size=12, color=COULEURS["texte_clair"]),
                ]),
                ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0, controls=[
                    badge_statut(statut),
                    ft.Container(height=5),
                    ft.Text(
                        f"{int(r.get('montant_total_xaf', 0)):,} FCFA".replace(",", " "),
                        size=14, weight=ft.FontWeight.BOLD, color=COULEURS["texte"],
                    ),
                ]),
            ]),
            ft.Divider(height=1, color="#E0E0E0"),
            ft.Text(f"Soumis le {r.get('date_soumission', '')[:10]}", size=11, color=COULEURS["texte_clair"]),
        ]

        if en_attente:
            controls.append(ft.Container(height=5))
            controls.append(actions)

        controls.append(ft.Container(height=5))
        controls.append(btn_facture)

        return ft.Container(
            content=ft.Column(controls=controls, spacing=8),
            bgcolor=COULEURS["blanc"], border_radius=12, padding=15,
            shadow=ft.BoxShadow(blur_radius=6, color="#1A000000", offset=ft.Offset(0, 2)),
        )

    liste = ft.Column(spacing=10)
    zone_contenu = ft.Column(controls=[liste], expand=True, scroll=ft.ScrollMode.AUTO)

    def charger_liste(statut=None):
        data = client.get_reservations(statut=statut)
        liste.controls.clear()
        if not data:
            liste.controls.append(
                ft.Container(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.icons.INBOX, size=50, color=COULEURS["texte_clair"]),
                            ft.Text("Aucune réservation", size=15, color=COULEURS["texte_clair"]),
                        ],
                    ),
                    alignment=ft.alignment.center, padding=50,
                )
            )
        else:
            for r in data:
                liste.controls.append(carte_reservation(r))

    def afficher_formulaire(e):
        from views.reservations.formulaire import vue_formulaire_reservation

        def on_success(result):
            charger_liste()
            zone_contenu.controls.clear()
            zone_contenu.controls.append(liste)
            page.update()

        def on_cancel():
            zone_contenu.controls.clear()
            zone_contenu.controls.append(liste)
            page.update()

        formulaire = vue_formulaire_reservation(page, on_success, on_cancel)
        zone_contenu.controls.clear()
        zone_contenu.controls.append(formulaire)
        page.update()

    charger_liste()

    return ft.Container(
        expand=True,
        bgcolor=COULEURS["fond"],
        padding=ft.padding.all(25),
        content=ft.Column(controls=[
            ft.Container(height=20),
            ft.Row(controls=[
                ft.Text("Réservations", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["titre"]),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Nouvelle réservation", icon=ft.icons.ADD,
                    bgcolor=COULEURS["success"], color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=afficher_formulaire,
                ),
            ]),
            ft.Text("Gestion des demandes d'inhumation", size=14, color=COULEURS["texte_clair"]),
            ft.Container(height=15),
            ft.Row(spacing=10, controls=[
                ft.ElevatedButton(
                    "Toutes", bgcolor=COULEURS["primaire"], color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=lambda e: [charger_liste(None), page.update()],
                ),
                ft.OutlinedButton("En attente", style=ft.ButtonStyle(color="#fd7e14"),
                    on_click=lambda e: [charger_liste("EN_ATTENTE"), page.update()]),
                ft.OutlinedButton("Validées", style=ft.ButtonStyle(color="#28a745"),
                    on_click=lambda e: [charger_liste("VALIDEE"), page.update()]),
                ft.OutlinedButton("Refusées", style=ft.ButtonStyle(color="#dc3545"),
                    on_click=lambda e: [charger_liste("REFUSEE"), page.update()]),
            ]),
            ft.Container(height=10),
            zone_contenu,
        ]),
    )