"""Point d'entrée principal de l'application Flet."""
import flet as ft
from pages.login import LoginPage
from pages.dashboard import DashboardPage
from pages.reservations import ReservationsPage
from pages.finances import FinancesPage
from utils.api_client import get_user_info


def main(page: ft.Page):
    page.title = "Gestion de Cimetière — GI2 2026"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE_800)
    page.window_width = 1200
    page.window_height = 800
    page.padding = 0

    # ── Navigation après connexion ────────────────────────────────────────────
    def on_login_success(role: str):
        afficher_app(role)

    def on_logout():
        page.controls.clear()
        page.appbar = None
        page.navigation_bar = None
        page.controls.append(LoginPage(page, on_login_success))
        page.update()

    def afficher_app(role: str):
        page.controls.clear()
        page.appbar = None

        # Construire la navigation selon le rôle
        tabs_accessibles = ["dashboard"]
        if role in ["admin", "secretariat", "agent"]:
            tabs_accessibles.append("reservations")
        if role in ["admin", "secretariat"]:
            tabs_accessibles.append("finances")

        contenu_actuel = [None]

        def changer_page(index: int):
            page.controls.clear()
            onglet = tabs_accessibles[index]

            if onglet == "dashboard":
                appbar, corps = DashboardPage(page, on_logout)
                page.appbar = appbar
                page.controls.append(corps)
            elif onglet == "reservations":
                page.appbar = ft.AppBar(
                    leading=ft.Icon(ft.icons.CHURCH, color=ft.colors.WHITE),
                    title=ft.Text("Gestion des Réservations", color=ft.colors.WHITE),
                    bgcolor=ft.colors.BLUE_900,
                    actions=[
                        ft.IconButton(ft.icons.LOGOUT, icon_color=ft.colors.WHITE,
                                      on_click=lambda e: on_logout(), tooltip="Déconnexion"),
                    ],
                )
                page.controls.append(ReservationsPage(page))
            elif onglet == "finances":
                page.appbar = ft.AppBar(
                    leading=ft.Icon(ft.icons.CHURCH, color=ft.colors.WHITE),
                    title=ft.Text("Gestion Financière", color=ft.colors.WHITE),
                    bgcolor=ft.colors.BLUE_900,
                    actions=[
                        ft.IconButton(ft.icons.LOGOUT, icon_color=ft.colors.WHITE,
                                      on_click=lambda e: on_logout(), tooltip="Déconnexion"),
                    ],
                )
                page.controls.append(FinancesPage(page))

            page.update()

        # Barre de navigation
        nav_destinations = [
            ft.NavigationBarDestination(icon=ft.icons.MAP_OUTLINED,
                                         selected_icon=ft.icons.MAP, label="Carte"),
        ]
        if "reservations" in tabs_accessibles:
            nav_destinations.append(
                ft.NavigationBarDestination(icon=ft.icons.BOOK_OUTLINED,
                                             selected_icon=ft.icons.BOOK, label="Réservations")
            )
        if "finances" in tabs_accessibles:
            nav_destinations.append(
                ft.NavigationBarDestination(icon=ft.icons.ACCOUNT_BALANCE_OUTLINED,
                                             selected_icon=ft.icons.ACCOUNT_BALANCE, label="Finances")
            )

        page.navigation_bar = ft.NavigationBar(
            destinations=nav_destinations,
            on_change=lambda e: changer_page(e.control.selected_index),
            bgcolor=ft.colors.BLUE_900,
            indicator_color=ft.colors.BLUE_700,
            label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        )

        changer_page(0)

    # ── Démarrage ─────────────────────────────────────────────────────────────
    page.controls.append(LoginPage(page, on_login_success))
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
