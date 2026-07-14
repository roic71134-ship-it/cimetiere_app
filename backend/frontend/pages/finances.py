"""Page de gestion financière."""
import flet as ft
from utils.api_client import api_get, api_post


def FinancesPage(page: ft.Page):
    """Dashboard financier avec factures et paiements."""

    # Métriques
    lbl_total = ft.Text("—", size=26, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_800)
    lbl_encaisse = ft.Text("—", size=26, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_700)
    lbl_restant = ft.Text("—", size=26, weight=ft.FontWeight.BOLD, color=ft.colors.RED_700)

    def carte_metrique(label, ctrl):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([ctrl, ft.Text(label, size=11, color=ft.colors.GREY_600)],
                                  horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                padding=ft.padding.symmetric(vertical=14, horizontal=20),
                alignment=ft.alignment.center,
            ), elevation=2,
        )

    # Tableau factures
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("N° Facture")),
            ft.DataColumn(ft.Text("Client")),
            ft.DataColumn(ft.Text("Total (FCFA)")),
            ft.DataColumn(ft.Text("Payé (FCFA)")),
            ft.DataColumn(ft.Text("Restant")),
            ft.DataColumn(ft.Text("Statut")),
            ft.DataColumn(ft.Text("Action")),
        ],
        rows=[],
        border=ft.border.all(1, ft.colors.GREY_300),
        border_radius=8,
        horizontal_lines=ft.BorderSide(1, ft.colors.GREY_200),
    )

    statut_msg = ft.Text("", color=ft.colors.GREEN_700)

    COULEURS_STATUT = {
        "en_attente": ft.colors.ORANGE_700,
        "partiellement_payee": ft.colors.BLUE_700,
        "payee": ft.colors.GREEN_700,
        "annulee": ft.colors.GREY_600,
    }

    def fmt(v): return f"{v:,.0f}"

    def charger(e=None):
        # Revenus
        ok_r, rev = api_get("/finances/revenus")
        if ok_r:
            lbl_total.value = fmt(rev.get("total_factures", 0)) + " FCFA"
            lbl_encaisse.value = fmt(rev.get("total_encaisse", 0)) + " FCFA"
            lbl_restant.value = fmt(rev.get("total_restant", 0)) + " FCFA"

        # Factures
        ok_f, factures = api_get("/finances/factures")
        table.rows.clear()
        if ok_f and isinstance(factures, list):
            for f in factures:
                statut = f.get("statut", "")
                row = ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f["numero"], weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(f["client_nom"])),
                    ft.DataCell(ft.Text(fmt(f["montant_total"]))),
                    ft.DataCell(ft.Text(fmt(f["montant_paye"]), color=ft.colors.GREEN_700)),
                    ft.DataCell(ft.Text(fmt(f["montant_restant"]),
                                        color=ft.colors.RED_600 if f["montant_restant"] > 0 else ft.colors.GREY_400)),
                    ft.DataCell(ft.Text(statut.upper(), color=COULEURS_STATUT.get(statut))),
                    ft.DataCell(
                        ft.ElevatedButton(
                            "Paiement",
                            icon=ft.icons.PAYMENTS_OUTLINED,
                            on_click=lambda e, fid=f["id"], fnum=f["numero"],
                                           frest=f["montant_restant"]: ouvrir_paiement(fid, fnum, frest),
                            visible=statut != "payee",
                            style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_800, color=ft.colors.WHITE),
                        )
                    ),
                ])
                table.rows.append(row)
        page.update()

    def ouvrir_paiement(facture_id: int, numero: str, restant: float):
        montant_field = ft.TextField(
            label=f"Montant (restant : {fmt(restant)} FCFA)",
            width=280,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        canal_field = ft.Dropdown(
            label="Canal de paiement",
            width=280,
            options=[
                ft.dropdown.Option("mobile_money", "Mobile Money"),
                ft.dropdown.Option("airtel_money", "Airtel Money"),
                ft.dropdown.Option("especes", "Espèces"),
                ft.dropdown.Option("virement", "Virement bancaire"),
            ],
            value="especes",
        )
        ref_field = ft.TextField(label="Référence transaction (optionnel)", width=280)
        msg = ft.Text("", color=ft.colors.RED_600)

        def enregistrer(e):
            try:
                montant = float(montant_field.value or 0)
            except ValueError:
                msg.value = "Montant invalide."
                page.update()
                return

            ok, data = api_post("/finances/paiements", {
                "facture_id": facture_id,
                "montant": montant,
                "canal": canal_field.value,
                "reference_transaction": ref_field.value or "",
            })
            dlg.open = False
            if ok:
                statut_msg.value = f"✓ Paiement de {fmt(montant)} FCFA enregistré pour la facture {numero}."
                statut_msg.color = ft.colors.GREEN_700
            else:
                statut_msg.value = data.get("message", "Erreur.")
                statut_msg.color = ft.colors.RED_700
            charger()

        dlg = ft.AlertDialog(
            title=ft.Text(f"Enregistrer un paiement — {numero}"),
            content=ft.Column([montant_field, canal_field, ref_field, msg], tight=True, spacing=10),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                ft.ElevatedButton("Enregistrer", on_click=enregistrer,
                                   style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE)),
            ],
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    charger()

    return ft.Container(
        content=ft.Column([
            ft.Text("Gestion Financière", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                carte_metrique("Total facturé", lbl_total),
                carte_metrique("Total encaissé", lbl_encaisse),
                carte_metrique("Restant à encaisser", lbl_restant),
            ]),
            ft.Divider(),
            ft.Row([
                ft.Text("Factures", size=16, weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.icons.REFRESH, on_click=charger, tooltip="Actualiser"),
            ]),
            statut_msg,
            ft.Column([table], scroll=ft.ScrollMode.AUTO),
        ], spacing=12),
        padding=20,
        expand=True,
    )
