import flet as ft
import re 
from ui.search_view import SearchView
from ui.results_view import ResultsView
from optimizer.optimization_script import optimize_purchase

class MainView(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.search_view = SearchView(self.handle_search)
        self.results_view = ResultsView()
        self.exclude_term = ft.TextField(label="Exclude Words", expand=True)
        self.budget = ft.TextField(label="Budget ($)", expand=True)
        self.optimize_button = ft.ElevatedButton("Optimize", on_click=self.handle_optimize)
        self.optimize_progress = ft.ProgressBar(visible=False)

    def build(self):
        return ft.Column([
            ft.Text("Supermarket Product Optimizer", size=24, weight=ft.FontWeight.BOLD),
            
            # Scrape Website Section
            ft.Text("Scrape Website", size=20, weight=ft.FontWeight.BOLD),
            self.search_view,
            ft.Divider(),
            
            # Filter Products Section
            ft.Text("Filter Products", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([self.exclude_term, self.budget, self.optimize_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.optimize_progress,
            self.results_view
        ], alignment=ft.MainAxisAlignment.START, spacing=10)

    def handle_search(self, products):
        # Store products for optimization
        self.products = products
        self.update()

    def handle_optimize(self, e):
        if self.exclude_term.value and self.budget.value and hasattr(self, 'products'):
            try:
                self.optimize_progress.visible = True
                self.update()

                budget = float(self.budget.value)
                exclude_words = [word.strip().lower() for word in re.split(r'[,\s]+', self.exclude_term.value)]
                
                # Perform optimization
                selected_products, total_weight, top_3 = optimize_purchase(self.products, budget, exclude_words)
                
                # Prepare results
                if not selected_products:
                    results = []
                    total_price = 0
                    total_weight = 0
                else:
                    results = selected_products
                    total_price = sum(product['effective_price'] for product in results)

                # Update results view
                self.results_view.update_results(results, total_price, total_weight, top_3)
                
                self.optimize_progress.visible = False
                self.update()
            except ValueError:
                print("Invalid budget value")
                self.optimize_progress.visible = False
                self.update()
        else:
            print("Please fill in all fields and scrape products first")