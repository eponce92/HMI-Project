import flet as ft

class ResultsView(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.greedy_results = ft.Column([ft.Text("No results yet.", weight=ft.FontWeight.BOLD)])
        self.knapsack_results = ft.Column([ft.Text("No results yet.", weight=ft.FontWeight.BOLD)])
        self.ratio_results = ft.Column([ft.Text("No results yet.", weight=ft.FontWeight.BOLD)])
        self.greedy_total_text = ft.Text("", weight=ft.FontWeight.BOLD)
        self.knapsack_total_text = ft.Text("", weight=ft.FontWeight.BOLD)
        self.ratio_total_text = ft.Text("", weight=ft.FontWeight.BOLD)
        self.top_3_results = ft.Column([ft.Text("No top 3 results yet.", weight=ft.FontWeight.BOLD)])

    def build(self):
        return ft.Container(
            content=ft.ExpansionPanelList(
                expand_icon_color=ft.colors.BLACK,
                elevation=2,
                divider_color=ft.colors.BLACK,
                controls=[
                    self.create_expansion_panel("Greedy Optimization", self.greedy_total_text, self.greedy_results),
                    self.create_expansion_panel("Knapsack Optimization", self.knapsack_total_text, self.knapsack_results),
                    self.create_expansion_panel("Ratio-based Optimization", self.ratio_total_text, self.ratio_results),
                    self.create_expansion_panel("Top 3 Products by lb/dollar", None, self.top_3_results),
                ],
            ),
            expand=True,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.WHITE,  # Set the container background color here
        )

    def create_expansion_panel(self, title, total_text, results):
        return ft.ExpansionPanel(
            header=ft.ListTile(title=ft.Text(title, weight=ft.FontWeight.BOLD)),
            content=ft.Container(
                content=ft.Column([
                    total_text if total_text else ft.Container(),
                    results
                ], alignment=ft.alignment.center),
                width=800,
                bgcolor=ft.colors.WHITE,  # Set the panel content background color here
            ),
        )

    def update_results(self, greedy_results, knapsack_results, ratio_results):
        self.update_result_section(greedy_results[0], greedy_results[1], self.greedy_results, self.greedy_total_text)
        self.update_result_section(knapsack_results[0], knapsack_results[1], self.knapsack_results, self.knapsack_total_text)
        self.update_result_section(ratio_results[0], ratio_results[1], self.ratio_results, self.ratio_total_text)

        self.update_top_3(greedy_results[2])

        self.update()

    def update_result_section(self, selected_products, total_weight, results_column, total_text):
        results_column.controls.clear()
        if not selected_products:
            results_column.controls.append(ft.Text("No products could be selected within the given budget.", weight=ft.FontWeight.BOLD))
            total_text.value = ""
        else:
            for product in selected_products:
                product_controls = [
                    ft.Text(f"Name: {product['name']}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Price: ${product['effective_price']:.2f}"),
                    ft.Text(f"Weight: {product['weight_lb']:.2f} lbs"),
                    ft.Text(f"Price by Weight: {product['price_by_weight']}"),
                    ft.Text(f"lb/dollar: {product['lb_per_dollar']:.4f}"),
                    ft.ElevatedButton(
                        "View Product",
                        on_click=lambda _: self.open_url(product['link']),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    ),
                ]
                if 'image_url' in product:
                    product_controls.insert(0, ft.Image(src=product['image_url'], width=100, height=100))  # Mostrar imagen del producto si existe

                results_column.controls.append(
                    ft.Container(
                        content=ft.Column(product_controls, alignment=ft.alignment.center),
                        padding=10,
                        border=ft.border.all(1, ft.colors.OUTLINE),
                        border_radius=8,
                        margin=ft.margin.only(bottom=10),
                        bgcolor=ft.colors.WHITE12  # Set the individual result background color here
                    )
                )
            total_price = sum(product['effective_price'] for product in selected_products)
            total_text.value = f"Total Price: ${total_price:.2f}\nTotal Weight: {total_weight:.2f} lbs"

    def update_top_3(self, top_3):
        self.top_3_results.controls.clear()
        for product in top_3:
            product_controls = [
                ft.Text(f"Name: {product['name']}", weight=ft.FontWeight.BOLD),
                ft.Text(f"Price: ${product['effective_price']:.2f}"),
                ft.Text(f"Weight: {product['weight_lb']:.2f} lbs"),
                ft.Text(f"Price by Weight: {product['price_by_weight']}"),
                ft.Text(f"lb/dollar: {product['lb_per_dollar']:.4f}"),
                ft.ElevatedButton(
                    "View Product",
                    on_click=lambda _: self.open_url(product['link']),
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                ),
            ]
            if 'image_url' in product:
                product_controls.insert(0, ft.Image(src=product['image_url'], width=100, height=100))  # Mostrar imagen del producto si existe

            self.top_3_results.controls.append(
                ft.Container(
                    content=ft.Column(product_controls, alignment=ft.alignment.center),
                    padding=10,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=8,
                    margin=ft.margin.only(bottom=10),
                    bgcolor=ft.colors.LIGHT_BLUE_50  # Set the individual result background color here
                )
            )

    def open_url(self, url):
        self.page.launch_url(url)
