import flet as ft

class ResultsView(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.optimized_results_text = ft.Text("No results yet.")
        self.top_3_text = ft.Text("No top 3 results yet.")
        self.total_text = ft.Text("")

    def build(self):
        return ft.Column([
            ft.Text("Optimized Results:", size=20, weight=ft.FontWeight.BOLD),
            self.total_text,
            self.optimized_results_text,
            ft.Text("Top 3 Products by lb/dollar:", size=20, weight=ft.FontWeight.BOLD),
            self.top_3_text
        ])

    def update_results(self, results, total_price, total_weight, top_3):
        if not results:
            self.optimized_results_text.value = "No products could be selected within the given budget."
            self.total_text.value = ""
        else:
            result_strings = []
            for product in results:
                result_strings.append(
                    f"Name: {product['name']}\n"
                    f"Price: ${product['effective_price']:.2f}\n"
                    f"Weight: {product['weight_lb']:.2f} lbs\n"
                    f"Price by Weight: {product['price_by_weight']}\n"
                    f"lb/dollar: {product['lb_per_dollar']:.4f}\n"
                    f"Link: {product['link']}\n"
                )
            self.optimized_results_text.value = "\n".join(result_strings)
            self.total_text.value = f"Total Price: ${total_price:.2f}\nTotal Weight: {total_weight:.2f} lbs"

        top_3_strings = []
        for product in top_3:
            top_3_strings.append(
                f"Name: {product['name']}\n"
                f"Price: ${product['effective_price']:.2f}\n"
                f"Weight: {product['weight_lb']:.2f} lbs\n"
                f"Price by Weight: {product['price_by_weight']}\n"
                f"lb/dollar: {product['lb_per_dollar']:.4f}\n"
                f"Link: {product['link']}\n"
            )
        self.top_3_text.value = "\n".join(top_3_strings)
        
        self.update()