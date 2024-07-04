import flet as ft
from ui.main_view import MainView

def main(page: ft.Page):
    page.title = "Supermarket Product Optimizer"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 800
    page.window_height = 600
    page.window_resizable = True
    page.padding = 20

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    MainView(page)
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        page.update()

    page.on_route_change = route_change
    page.go('/')

ft.app(target=main)