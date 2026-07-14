"""Page de gestion des réservations (Admin/Secrétariat)."""
import flet as ft
from utils.api_client import api_get, api_post


def ReservationsPage(page: ft.Page):
    """Page listant et gérant les réservations."""

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("#")),
            ft.DataColumn(ft.Text("Caveau")),
            ft.DataColumn(ft.Text("Client")),
            ft.DataColumn(ft.Text("Type")),
            ft.DataColumn(ft.Text("Statut")),
            ft.DataColumn(ft.Text("Date")),
            ft.DataColumn(ft.Text("Actions")),
        ],
        rows=[],
        border=ft.border.all(1, ft.colors.GREY_300),
        border_radius=8,
        horizontal_lines=ft.BorderSide(1, ft.colors.GREY_200),
    )

    filtre = ft.Dropdown(
        label="Filtrer",
        width=180,
        options=[
            ft.dropdown.Option("", "Toutes"),
            ft.dropdown.Option("en_attente", "En attente"),
            ft.dropdown.Option("validee", "Validées"),
            ft.dropdown.Option("rejetee", "Rejetées"),
        ],
        value="",
    )

    status_msg = ft.Text("", color=ft.colors.GREEN_700)

    COULEURS_STATUT = {
        "en_attente": ft.colors.ORANGE_700,
        "validee": ft.colors.GREEN_700,
        "rejetee": ft.colors.RED_700,
        "annulee": ft.colors.GREY_600,
    }

    def charger(e=None):
        params = {}
        if filtre.value:
            params["statut"] = filtre.value
        ok, data = api_get("/reservations/", params)
        table.rows.clear()
        if ok and isinstance(data, list):
            for r in data:
                statut = r.get("statut", "")
                row = ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r["id"]))),
                    ft.DataCell(ft.Text(r["caveau_reference"])),
                    ft.DataCell(ft.Text(r["client_nom"])),
                    ft.DataCell(ft.Text("Perp." if r["type_concession"] == "perpetuelle" else "15 ans")),
                    ft.DataCell(ft.Text(statut.upper(), color=COULEURS_STATUT.get(statut))),
                    ft.DataCell(ft.Text(r["date_soumission"][:10])),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                ft.icons.CHECK_CIRCLE_OUTLINE,
                                icon_color=ft.colors.GREEN_700,
                                tooltip="Valider",
                                on_click=lambda e, rid=r["id"]: action_valider(rid),
                                visible=statut == "en_attente",
                            ),
                            ft.IconButton(
                                ft.icons.CANCEL_OUTLINED,
                                icon_color=ft.colors.RED_700,
                                tooltip="Rejeter",
                                on_click=lambda e, rid=r["id"]: action_rejeter(rid),
                                visible=statut == "en_attente",
                            ),
                        ], spacing=0)
                    ),
                ])
                table.rows.append(row)
        page.update()

    def action_valider(reservation_id: int):
        ok, data = api_post(f"/reservations/{reservation_id}/valider", {})
        if ok:
            status_msg.value = f"✓ Réservation #{reservation_id} validée. Facture générée et envoyée."
            status_msg.color = ft.colors.GREEN_700
        else:
            status_msg.value = data.get("message", "Erreur.")
            status_msg.color = ft.colors.RED_700
        charger()

    def action_rejeter(reservation_id: int):
        motif_field = ft.TextField(label="Motif du rejet", multiline=True, min_lines=2, width=300)
        msg = ft.Text("", color=ft.colors.RED_600)

        def confirmer_rejet(e):
            ok, data = api_post(f"/reservations/{reservation_id}/rejeter",
                                 {"commentaire": motif_field.value or "Non spécifié"})
            dlg.open = False
            if ok:
                status_msg.value = f"Réservation #{reservation_id} rejetée."
                status_msg.color = ft.colors.ORANGE_700
            else:
                status_msg.value = data.get("message", "Erreur.")
                status_msg.color = ft.colors.RED_700
            charger()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Rejeter la réservation #{reservation_id}"),
            content=ft.Column([motif_field, msg], tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                ft.ElevatedButton("Confirmer le rejet", on_click=confirmer_rejet,
                                   style=ft.ButtonStyle(bgcolor=ft.colors.RED_700, color=ft.colors.WHITE)),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    filtre.on_change = charger
    charger()

    return ft.Container(
        content=ft.Column([
            ft.Text("Gestion des Réservations", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([filtre, ft.IconButton(ft.icons.REFRESH, on_click=charger, tooltip="Actualiser")]),
            status_msg,
            ft.Column([table], scroll=ft.ScrollMode.AUTO),
        ], spacing=12),
        padding=20,
        expand=True,
    )
