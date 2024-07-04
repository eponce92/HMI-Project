import flet as ft

class ResultsView(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.results_text = ft.Text("No results yet.")
        self.total_text = ft.Text("")

    def build(self):
        return ft.Column([
            ft.Text("Optimized Results:", size=20, weight=ft.FontWeight.BOLD),
            self.total_text,
            self.results_text
        ])

    def update_results(self, results, total_price, total_weight):
        if not results:
            self.results_text.value = "No products could be selected within the given budget."
            self.total_text.value = ""
        else:
            result_strings = []
            for product in results:
                result_strings.append(
                    f"Name: {product['name']}\nPrice: ${product['price']:.2f}\nLink: {product['link']}\n"
                )
            self.results_text.value = "\n".join(result_strings)
            self.total_text.value = f"Total Price: ${total_price:.2f}\nTotal Weight: {total_weight:.2f} lbs"
        self.update()