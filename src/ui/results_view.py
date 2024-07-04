import flet as ft

class ResultsView(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.greedy_results = ft.Column([ft.Text("No results yet.")])
        self.knapsack_results = ft.Column([ft.Text("No results yet.")])
        self.ratio_results = ft.Column([ft.Text("No results yet.")])
        self.greedy_total_text = ft.Text("")
        self.knapsack_total_text = ft.Text("")
        self.ratio_total_text = ft.Text("")
        self.top_3_results = ft.Column([ft.Text("No top 3 results yet.")])

    def build(self):
        return ft.Column([
            ft.Text("Optimization Results:", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Greedy Optimization:", size=16, weight=ft.FontWeight.BOLD),
            self.greedy_total_text,
            self.greedy_results,
            ft.Text("Knapsack Optimization:", size=16, weight=ft.FontWeight.BOLD),
            self.knapsack_total_text,
            self.knapsack_results,
            ft.Text("Ratio-based Optimization:", size=16, weight=ft.FontWeight.BOLD),
            self.ratio_total_text,
            self.ratio_results,
            ft.Text("Top 3 Products by lb/dollar (respecting exclusions and budget):", size=16, weight=ft.FontWeight.BOLD),
            self.top_3_results,
        ])

    def update_results(self, greedy_results, knapsack_results, ratio_results):
        self.update_result_section(greedy_results[0], greedy_results[1], self.greedy_results, self.greedy_total_text)
        self.update_result_section(knapsack_results[0], knapsack_results[1], self.knapsack_results, self.knapsack_total_text)
        self.update_result_section(ratio_results[0], ratio_results[1], self.ratio_results, self.ratio_total_text)
        
        # Update top 3 products (using the top 3 from the greedy method, as they should be the same for all methods)
        self.update_top_3(greedy_results[2])
        
        self.update()

    def update_result_section(self, selected_products, total_weight, results_column, total_text):
        results_column.controls.clear()
        if not selected_products:
            results_column.controls.append(ft.Text("No products could be selected within the given budget."))
            total_text.value = ""
        else:
            for product in selected_products:
                results_column.controls.append(
                    ft.Column([
                        ft.Text(f"Name: {product['name']}"),
                        ft.Text(f"Price: ${product['effective_price']:.2f}"),
                        ft.Text(f"Weight: {product['weight_lb']:.2f} lbs"),
                        ft.Text(f"Price by Weight: {product['price_by_weight']}"),
                        ft.Text(f"lb/dollar: {product['lb_per_dollar']:.4f}"),
                        ft.TextButton("View Product", on_click=lambda _: self.open_url(product['link'])),
                        ft.Divider(),
                    ])
                )
            total_price = sum(product['effective_price'] for product in selected_products)
            total_text.value = f"Total Price: ${total_price:.2f}\nTotal Weight: {total_weight:.2f} lbs"

    def update_top_3(self, top_3):
        self.top_3_results.controls.clear()
        for product in top_3:
            self.top_3_results.controls.append(
                ft.Column([
                    ft.Text(f"Name: {product['name']}"),
                    ft.Text(f"Price: ${product['effective_price']:.2f}"),
                    ft.Text(f"Weight: {product['weight_lb']:.2f} lbs"),
                    ft.Text(f"lb/dollar: {product['lb_per_dollar']:.4f}"),
                    ft.TextButton("View Product", on_click=lambda _: self.open_url(product['link'])),
                    ft.Divider(),
                ])
            )

    def open_url(self, url):
        self.page.launch_url(url)