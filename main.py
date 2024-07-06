import flet as ft
from src.ui.main_view import MainView

def main(page: ft.Page):
    page.title = "Supermarket Product Optimizer"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 800
    page.window.height = 1000
    page.window.resizable = True
    page.padding = 20
    page.window_icon = "icon.png"
    
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