import flet as ft
from src.ui.results_view import ResultsView
from src.ui.search_view import SearchView
from src.optimizer.optimization_script import optimize_purchase_greedy, optimize_purchase_knapsack, optimize_purchase_ratio

class MainView(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.search_view = SearchView(self.handle_search)
        self.results_view = ResultsView()
        
        # Define a consistent height for all input fields and buttons
        self.input_height = 50
        
        self.search_query = ft.TextField(
            label="Search Query",
            expand=True,
            prefix_icon=ft.icons.SEARCH,
            hint_text="Enter your search query",
            height=self.input_height,
        )
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
        self.similarity_threshold = ft.Slider(
            min=0,
            max=1,
            divisions=20,
            label="Similarity Threshold: {value}",
            value=0.3,
            on_change=self.update_threshold_label
        )
        self.threshold_label = ft.Text(f"Similarity Threshold: {self.similarity_threshold.value:.2f}")
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
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Supermarket Product Optimizer", size=24, weight=ft.FontWeight.BOLD),
                            ft.Divider(height=30),
                            ft.Text("Scrape Website", size=20, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=self.search_view,
                                padding=ft.padding.only(top=10, bottom=10)
                            ),
                        ]),
                        padding=20
                    ),
                    elevation=4
                ),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Filter and Search Products", size=20, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Column([
                                    ft.Row(
                                        [
                                            self.search_query,
                                            ft.Container(width=10),
                                            self.budget,
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Container(height=10),  # Add vertical spacing
                                    ft.Row(
                                        [
                                            self.exclude_term,
                                            ft.Container(width=10),
                                            self.optimize_button,
                                            ft.Container(width=10),
                                            self.optimize_progress
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Container(height=10),  # Add vertical spacing
                                    self.similarity_threshold,
                                    self.threshold_label,
                                ]),
                                padding=ft.padding.only(top=10, bottom=10)
                            ),
                        ]),
                        padding=20
                    ),
                    elevation=4
                ),
                ft.Card(
                    content=ft.Container(
                        content=self.results_view,
                        padding=20
                    ),
                    elevation=4
                )
            ], alignment=ft.MainAxisAlignment.START, spacing=20),
            padding=20
        )

    def update_threshold_label(self, e):
        self.threshold_label.value = f"Similarity Threshold: {self.similarity_threshold.value:.2f}"
        self.update()

    async def handle_search(self, products):
        self.products = products
        self.update()

    async def handle_optimize(self, e):
        if self.budget.value and self.search_query.value and hasattr(self, 'products'):
            try:
                self.optimize_progress.visible = True
                self.update()

                budget = float(self.budget.value)
                exclude_words = [word.strip().lower() for word in self.exclude_term.value.split(',')] if self.exclude_term.value else []
                search_query = self.search_query.value
                similarity_threshold = self.similarity_threshold.value

                greedy_results = optimize_purchase_greedy(self.products, budget, exclude_words, search_query, similarity_threshold)
                knapsack_results = optimize_purchase_knapsack(self.products, budget, exclude_words, search_query, similarity_threshold)
                ratio_results = optimize_purchase_ratio(self.products, budget, exclude_words, search_query, similarity_threshold)

                print("Greedy Results:", greedy_results)  # Debugging line
                print("Knapsack Results:", knapsack_results)  # Debugging line
                print("Ratio Results:", ratio_results)  # Debugging line

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