import flet as ft
from config import COULEURS
from config import API_BASE_URL

STATUT_COULEURS = {
    "EN_ATTENTE": "#fd7e14",
    "VALIDEE":    "#28a745",
    "REFUSEE":    "#dc3545",
    "EFFECTUEE":  "#1B4F72",
    "ANNULEE":    "#6c757d",
}

STATUT_LABELS = {
    "EN_ATTENTE": "En attente",
    "VALIDEE":    "Validée",
    "REFUSEE":    "Refusée",
    "EFFECTUEE":  "Effectuée",
    "ANNULEE":    "Annulée",
}

MOTIF_LABELS = {
    "TRANSFERT":  "Transfert",
    "RENOVATION": "Rénovation",
    "FAMILIAL":   "Regroupement familial",
    "JUDICIAIRE": "Ordonnance judiciaire",
    "AUTRE":      "Autre",
}


def vue_exhumations(page: ft.Page):
    from api_client import client

    liste = ft.Column(spacing=10)
    zone_contenu = ft.Column(controls=[liste], expand=True, scroll=ft.ScrollMode.AUTO)

    user = client.get_me()
    role_nom = user.get("role", {}).get("nom", "") if user.get("role") else ""
    peut_valider = role_nom in ["ADMIN", "SECRETARIAT"]
    peut_creer = role_nom in ["ADMIN", "SECRETARIAT", "AGENT"]
    peut_effectuer = role_nom in ["ADMIN", "SECRETARIAT", "AGENT"]

    def snack(msg, couleur=None):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=couleur or COULEURS["success"],
        )
        page.snack_bar.open = True
        page.update()

    def badge_statut(statut):
        return ft.Container(
            content=ft.Text(STATUT_LABELS.get(statut, statut), size=11, color="white", weight=ft.FontWeight.BOLD),
            bgcolor=STATUT_COULEURS.get(statut, "#6c757d"),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
        )

    def carte_exhumation(ex):
        eid = ex.get("id")
        statut = ex.get("statut", "")
        en_attente = statut == "EN_ATTENTE"

        def ouvrir_validation(e):
            notes_f = ft.TextField(color="white", label="Notes (optionnel)", multiline=True, min_lines=2, border_radius=8)

            def confirmer(e):
                dlg.open = False
                page.update()
                res = client.valider_exhumation(eid, notes_f.value.strip())
                msg = res.get("message", "")
                if "validée" in msg.lower():
                    snack(f"✅ {msg}")
                else:
                    snack(msg or "Erreur", COULEURS["danger"])
                charger_liste()
                page.update()

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Valider l'exhumation", weight=ft.FontWeight.BOLD),
                content=ft.Container(width=400, content=ft.Column(tight=True, spacing=10, controls=[
                    ft.Text(f"N° {ex.get('numero', '')}", size=13, color=COULEURS["texte_clair"]),
                    ft.Text(f"Motif : {MOTIF_LABELS.get(ex.get('motif', ''), '')}", size=13),
                    ft.Container(height=5),
                    notes_f,
                ])),
                actions_alignment=ft.MainAxisAlignment.END,
                actions=[
                    ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                    ft.ElevatedButton("✅ Valider", bgcolor=COULEURS["success"], color="white",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=confirmer),
                ],
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        def ouvrir_refus(e):
            motif_f = ft.TextField(color="white", label="Motif du refus *", multiline=True, min_lines=2, border_radius=8)

            def confirmer(e):
                if not motif_f.value.strip():
                    motif_f.error_text = "Obligatoire"
                    page.update()
                    return
                dlg.open = False
                page.update()
                res = client.refuser_exhumation(eid, motif_f.value.strip())
                msg = res.get("message", "")
                if "refusée" in msg.lower():
                    snack(f"✅ {msg}")
                else:
                    snack(msg or "Erreur", COULEURS["danger"])
                charger_liste()
                page.update()

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Refuser l'exhumation", weight=ft.FontWeight.BOLD),
                content=ft.Container(width=400, content=ft.Column(tight=True, spacing=10, controls=[
                    ft.Text(f"N° {ex.get('numero', '')}", size=13, color=COULEURS["texte_clair"]),
                    ft.Container(height=5),
                    motif_f,
                ])),
                actions_alignment=ft.MainAxisAlignment.END,
                actions=[
                    ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                    ft.ElevatedButton("❌ Refuser", bgcolor=COULEURS["danger"], color="white",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=confirmer),
                ],
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        def marquer_effectuee(exhumation_id):
            res = client.effectuer_exhumation(exhumation_id)
            msg = res.get("message", "")
            if "effectuée" in msg.lower():
                snack(f"✅ {msg}")
            else:
                snack(msg or "Erreur", COULEURS["danger"])
            charger_liste()
            page.update()

        def ouvrir_autorisation(exhumation_id):
            page.launch_url(f"{API_BASE_URL}/exhumations/{exhumation_id}/autorisation-pdf")

        actions = ft.Row(spacing=10, controls=[
            ft.ElevatedButton("✅ Valider", bgcolor=COULEURS["success"], color="white",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=ouvrir_validation),
            ft.OutlinedButton("❌ Refuser",
                style=ft.ButtonStyle(color=COULEURS["danger"], side=ft.BorderSide(color=COULEURS["danger"], width=1)),
                on_click=ouvrir_refus),
        ]) if (en_attente and peut_valider) else ft.Container()

        controls = [
            ft.Row(controls=[
                ft.Column(expand=True, spacing=3, controls=[
                    ft.Text(ex.get("numero", ""), size=16, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                    ft.Text(f"Motif : {MOTIF_LABELS.get(ex.get('motif', ''), '')}", size=13, color=COULEURS["texte"]),
                    ft.Text(f"Caveau ID : {ex.get('caveau_id', '')}", size=12, color=COULEURS["texte_clair"]),
                ]),
                ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0, controls=[
                    badge_statut(statut),
                    ft.Container(height=5),
                    ft.Text(f"Prévu : {ex.get('date_exhumation_prevue', '—')}", size=11, color=COULEURS["texte_clair"]),
                ]),
            ]),
            ft.Divider(height=1, color="#E0E0E0"),
            ft.Text(f"Demande le {ex.get('date_demande', '')[:10]}", size=11, color=COULEURS["texte_clair"]),
        ]

        if en_attente and peut_valider:
            controls.append(ft.Container(height=5))
            controls.append(actions)

        if statut == "VALIDEE":
            controls.append(ft.Container(height=5))
            controls.append(
                ft.Row(spacing=10, controls=[
                    ft.TextButton(
                        "📄 Télécharger l'autorisation",
                        style=ft.ButtonStyle(color=COULEURS["primaire"]),
                        on_click=lambda e, eid=eid: ouvrir_autorisation(eid),
                    ),
                    ft.ElevatedButton(
                        "✔ Marquer comme effectuée",
                        bgcolor="#1B4F72", color="white",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=lambda e, eid=eid: marquer_effectuee(eid),
                        visible=peut_effectuer,
                    ),
                ])
            )

        if statut == "EFFECTUEE":
            controls.append(ft.Container(height=5))
            controls.append(
                ft.TextButton(
                    "📋 Télécharger le procès-verbal",
                    style=ft.ButtonStyle(color="#1B4F72"),
                    on_click=lambda e, eid=eid: page.launch_url(
                       f"{API_BASE_URL}/exhumations/{eid}/proces-verbal-pdf"
                    ),
                )
            )

        return ft.Container(
            content=ft.Column(controls=controls, spacing=8),
            bgcolor=COULEURS["blanc"], border_radius=12, padding=15,
            shadow=ft.BoxShadow(blur_radius=6, color="#1A000000", offset=ft.Offset(0, 2)),
        )

    def charger_liste(statut=None):
        data = client.get_exhumations(statut=statut)
        liste.controls.clear()
        if not data:
            liste.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.icons.INVENTORY, size=50, color=COULEURS["texte_clair"]),
                            ft.Text("Aucune exhumation trouvée", size=15, color=COULEURS["texte_clair"]),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center, padding=50,
                )
            )
        else:
            for ex in data:
                liste.controls.append(carte_exhumation(ex))

    def afficher_formulaire(e):
        reservations = client.get_reservations(statut="VALIDEE")

        if not reservations:
            snack("Aucune réservation validée disponible pour une exhumation.", COULEURS["danger"])
            return

        defunt_options = []
        defunts_map = {}
        for r in reservations:
            defunt = r.get("defunt", {})
            did = defunt.get("id")
            caveau_id = r.get("caveau_id")
            nom_complet = f"{defunt.get('prenom', '')} {defunt.get('nom', '')} — Caveau {r.get('caveau_id', '')}"
            defunt_options.append(ft.dropdown.Option(str(did), nom_complet))
            defunts_map[str(did)] = {"caveau_id": caveau_id, "reservation": r}

        defunt_dd = ft.Dropdown(
            label="Défunt concerné *",
            border_radius=8, expand=True,
            options=defunt_options,
        )
        motif_dd = ft.Dropdown(
            label="Motif *",
            border_radius=8, expand=True,
            options=[
                ft.dropdown.Option("TRANSFERT", "Transfert"),
                ft.dropdown.Option("RENOVATION", "Rénovation"),
                ft.dropdown.Option("FAMILIAL", "Regroupement familial"),
                ft.dropdown.Option("JUDICIAIRE", "Ordonnance judiciaire"),
                ft.dropdown.Option("AUTRE", "Autre"),
            ],
        )
        detail_f = ft.TextField(color="white", label="Détails (optionnel)", multiline=True, min_lines=2, border_radius=8, expand=True)
        date_f = ft.TextField(color="white", label="Date prévue (AAAA-MM-JJ) *", hint_text="ex: 2026-07-15", border_radius=8, expand=True)
        msg_f = ft.Text("", color=COULEURS["danger"], size=13)

        def soumettre(e):
            if not defunt_dd.value or not motif_dd.value or not date_f.value:
                msg_f.value = "Veuillez remplir tous les champs obligatoires."
                page.update()
                return

            caveau_id = defunts_map[defunt_dd.value]["caveau_id"]

            dlg.open = False
            page.update()
            res = client.creer_exhumation({
                "caveau_id": caveau_id,
                "defunt_id": int(defunt_dd.value),
                "motif": motif_dd.value,
                "motif_detail": detail_f.value or "",
                "date_exhumation_prevue": date_f.value,
                "notes": "",
            })
            msg = res.get("message", "")
            if "soumise" in msg.lower():
                snack(f"✅ {msg}")
            else:
                snack(str(res), COULEURS["danger"])
            charger_liste()
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nouvelle demande d'exhumation", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=450,
                content=ft.Column(tight=True, spacing=10, controls=[
                    defunt_dd, motif_dd, detail_f, date_f, msg_f,
                ]),
            ),
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, "open", False) or page.update()),
                ft.ElevatedButton("Soumettre", bgcolor=COULEURS["primaire"], color="white",
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    on_click=soumettre),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    charger_liste()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Row(controls=[
                    ft.Text("Exhumations", size=24, weight=ft.FontWeight.BOLD, color=COULEURS["primaire"]),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        "Nouvelle demande",
                        icon=ft.icons.ADD,
                        bgcolor=COULEURS["primaire"], color="white",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=afficher_formulaire,
                        visible=peut_creer,
                    ),
                ]),
                ft.Text("Gestion des demandes d'exhumation", size=14, color=COULEURS["texte_clair"]),
                ft.Container(height=15),
                ft.Row(spacing=10, controls=[
                    ft.ElevatedButton("Toutes", bgcolor=COULEURS["primaire"], color="white",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=lambda e: [charger_liste(None), page.update()]),
                    ft.OutlinedButton("En attente", style=ft.ButtonStyle(color="#fd7e14"),
                        on_click=lambda e: [charger_liste("EN_ATTENTE"), page.update()]),
                    ft.OutlinedButton("Validées", style=ft.ButtonStyle(color="#28a745"),
                        on_click=lambda e: [charger_liste("VALIDEE"), page.update()]),
                    ft.OutlinedButton("Effectuées", style=ft.ButtonStyle(color="#1B4F72"),
                        on_click=lambda e: [charger_liste("EFFECTUEE"), page.update()]),
                ]),
                ft.Container(height=10),
                zone_contenu,
            ],
        ),
        padding=ft.padding.all(25),
        expand=True,
        bgcolor=COULEURS["fond"],
    )