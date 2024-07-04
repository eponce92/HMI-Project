import flet as ft
from ui.main_view import MainView

def main(page: ft.Page):
    page.title = "Supermarket Product Optimizer"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 800  # Updated to use the new property
    page.window.height = 800  # Updated to use the new property
    page.window.resizable = True  # Updated to use the new property
    page.padding = 20

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Column(
                        [
                            MainView(page)
                        ],
                        scroll=ft.ScrollMode.ALWAYS,  # Enable scrolling for the column
                        expand=True
                    )
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        page.update()

    page.on_route_change = route_change
    page.go('/')

ft.app(target=main)