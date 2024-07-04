import flet as ft
from ui.search_view import SearchView
from ui.results_view import ResultsView
from optimizer.optimization_script import optimize_purchase

class MainView(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.search_view = SearchView(self.handle_search)
        self.results_view = ResultsView()

    def build(self):
        return ft.Column([
            ft.Text("Supermarket Product Optimizer", size=24, weight=ft.FontWeight.BOLD),
            self.search_view,
            self.results_view
        ])

    def handle_search(self, products, budget):
        # Perform optimization
        selected_indices, max_weight = optimize_purchase(products, budget)
        
        # Prepare results
        if not selected_indices:
            results = []
            total_price = 0
            total_weight = 0
        else:
            results = [products[i] for i in selected_indices]
            total_price = sum(product['price'] for product in results)
            total_weight = max_weight

        # Update results view
        self.results_view.update_results(results, total_price, total_weight)
        self.update()