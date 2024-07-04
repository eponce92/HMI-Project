import flet as ft
from ui.results_view import ResultsView
from ui.search_view import SearchView
from optimizer.optimization_script import optimize_purchase_greedy, optimize_purchase_knapsack, optimize_purchase_ratio

class MainView(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.search_view = SearchView(self.handle_search)
        self.results_view = ResultsView()
        
        self.input_height = 50
        
        self.exclude_term = ft.TextField(
            label="Exclude Words",
            expand=True,
            prefix_icon=ft.icons.BLOCK,
            hint_text="e.g., sugar, soda",
            height=self.input_height,
        )
        self.budget = ft.TextField(
            label="Budget ($)",
            expand=True,
            prefix_icon=ft.icons.ATTACH_MONEY,
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="Enter your budget",
            height=self.input_height,
        )
        self.optimize_button = ft.ElevatedButton(
            "Optimize",
            on_click=self.handle_optimize,
            icon=ft.icons.SHOPPING_CART,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            height=self.input_height,
        )
        self.optimize_progress = ft.ProgressRing(visible=False, width=24, height=24)

    def build(self):
        return ft.Container(
            content=ft.Column([
                self.create_section("Supermarket Product Optimizer", [
                    ft.Text("Scrape Website", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=self.search_view,
                        padding=ft.padding.only(top=10, bottom=10)
                    ),
                ], is_title=True),
                self.create_section("Filter Products", [
                    ft.Container(
                        content=ft.Row(
                            [
                                self.exclude_term,
                                ft.Container(width=10),
                                self.budget,
                                ft.Container(width=10),
                                self.optimize_button,
                                ft.Container(width=10),
                                self.optimize_progress
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=ft.padding.only(top=10, bottom=10)
                    ),
                ]),
                self.create_section("Optimization Results", [self.results_view]),
            ], alignment=ft.MainAxisAlignment.START, spacing=20),
            padding=20,
            expand=True
        )

    def create_section(self, title, content, is_title=False):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [ft.Text(title, size=24 if is_title else 20, weight=ft.FontWeight.BOLD)] +
                    ([ft.Divider(height=30)] if is_title else []) +
                    content
                ),
                padding=20
            ),
            elevation=4,
            expand=True
        )

    def handle_search(self, products):
        self.products = products
        self.update()

    def handle_optimize(self, e):
        if self.exclude_term.value and self.budget.value and hasattr(self, 'products'):
            try:
                self.optimize_progress.visible = True
                self.update()

                budget = float(self.budget.value)
                exclude_words = [word.strip().lower() for word in self.exclude_term.value.split(',')]
                
                greedy_results = optimize_purchase_greedy(self.products, budget, exclude_words)
                knapsack_results = optimize_purchase_knapsack(self.products, budget, exclude_words)
                ratio_results = optimize_purchase_ratio(self.products, budget, exclude_words)
                
                self.results_view.update_results(greedy_results, knapsack_results, ratio_results)
                
                self.optimize_progress.visible = False
                self.update()
            except ValueError:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("Invalid budget value"))
                self.page.snack_bar.open = True
                self.optimize_progress.visible = False
                self.update()
        else:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Please fill in all fields and scrape products first"))
            self.page.snack_bar.open = True
            self.update()