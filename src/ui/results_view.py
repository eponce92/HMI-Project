import flet as ft
from collections import Counter

class ResultsView(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.optimization_results = {
            "Greedy Optimization": {"results": None, "total_price": 0, "total_weight": 0, "bgcolor": ft.colors.WHITE},
            "Knapsack Optimization": {"results": None, "total_price": 0, "total_weight": 0, "bgcolor": ft.colors.WHITE},
            "Ratio-based Optimization": {"results": None, "total_price": 0, "total_weight": 0, "bgcolor": ft.colors.WHITE}
        }
        self.top_3_results = ft.Column([ft.Text("No top 3 results yet.", weight=ft.FontWeight.BOLD)], alignment=ft.alignment.center)
        self.expansion_panel_list = None

    def build(self):
        self.expansion_panel_list = ft.ExpansionPanelList(
            expand_icon_color=ft.colors.BLACK,
            elevation=2,
            divider_color=ft.colors.BLACK,
            controls=[
                self.create_expansion_panel(title, data["results"], data["total_price"], data["total_weight"], data["bgcolor"])
                for title, data in self.optimization_results.items()
            ] + [self.create_expansion_panel("Top 3 Products by lb/dollar", self.top_3_results, None, None, ft.colors.WHITE)]
        )
        return ft.Container(
            content=self.expansion_panel_list,
            expand=True,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.WHITE,
        )

    def create_expansion_panel(self, title, results, total_price, total_weight, bgcolor):
        total_text = ft.Text(
            f"Total Price: ${total_price:.2f}\nTotal Weight: {total_weight:.2f} lbs" if total_price is not None else "",
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.LEFT,
            style=ft.TextStyle(size=16)
        )
        return ft.ExpansionPanel(
            bgcolor=bgcolor,
            header=ft.ListTile(title=ft.Text(title, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.LEFT)),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=total_text,
                        alignment=ft.alignment.center_left,
                        padding=ft.padding.only(left=0, right=0, top=10, bottom=10),
                    ),
                    results if results else ft.Text("No results yet.", weight=ft.FontWeight.BOLD)
                ], alignment=ft.alignment.center, spacing=0),
                width=800,
                bgcolor=bgcolor,
                alignment=ft.alignment.center,
                padding=ft.padding.all(20),
            ),
        )

    def update_results(self, greedy_results, knapsack_results, ratio_results):
        print("Update Results Called")

        self.update_optimization_results("Greedy Optimization", greedy_results)
        self.update_optimization_results("Knapsack Optimization", knapsack_results)
        self.update_optimization_results("Ratio-based Optimization", ratio_results)

        self.update_top_3(greedy_results[2])
        self.highlight_best_performance()

        self.expansion_panel_list.controls = [
            self.create_expansion_panel(title, data["results"], data["total_price"], data["total_weight"], data["bgcolor"])
            for title, data in self.optimization_results.items()
        ] + [self.create_expansion_panel("Top 3 Products by lb/dollar", self.top_3_results, None, None, ft.colors.WHITE)]

        self.update()

    def update_optimization_results(self, optimization_type, results):
        selected_products, total_weight, _ = results
        results_column = ft.Column(alignment=ft.alignment.center)
        total_price = self.update_result_section(selected_products, total_weight, results_column)
        
        self.optimization_results[optimization_type].update({
            "results": results_column,
            "total_price": total_price,
            "total_weight": total_weight
        })

    def update_result_section(self, selected_products, total_weight, results_column):
        if not selected_products:
            results_column.controls.append(ft.Text("No products could be selected within the given budget.", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.LEFT))
            return 0
        
        product_counter = Counter([product['name'] for product in selected_products])
        unique_products = list({product['name']: product for product in selected_products}.values())
        total_price = 0

        for product in unique_products:
            quantity = product_counter[product['name']]
            total_price += product['effective_price'] * quantity
            
            quantity_container = ft.Container(
                content=ft.Text(f"{quantity}X", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, size=32),
                width=60,
                alignment=ft.alignment.center,
            )

            product_info_container = ft.Container(
                content=ft.Column([
                    ft.Text(f"Name: {product['name']}", weight=ft.FontWeight.BOLD, size=14, text_align=ft.TextAlign.LEFT),
                    ft.Text(f"Price: ${product['effective_price']:.2f}", size=14, text_align=ft.TextAlign.LEFT),
                    ft.Text(f"Weight: {product['weight_lb']:.2f} lbs", size=14, text_align=ft.TextAlign.LEFT),
                    ft.Text(f"Price by Weight: {product['price_by_weight']}", size=14, text_align=ft.TextAlign.LEFT),
                    ft.Text(f"lb/dollar: {product['lb_per_dollar']:.4f}", size=14, text_align=ft.TextAlign.LEFT),
                    ft.Container(height=10),  # Spacer
                    ft.ElevatedButton(
                        "View Product",
                        on_click=lambda e, link=product['link']: self.open_url(link),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=5),
                padding=ft.padding.all(10),
                expand=True,
            )

            image_container = ft.Container(
                content=ft.Image(
                    src=product.get('image_url', ''),
                    width=120,
                    height=None,
                    fit=ft.ImageFit.CONTAIN
                ) if 'image_url' in product else ft.Container(width=120),
                alignment=ft.alignment.center,
                width=120,
                expand=True,
            )

            outer_container = ft.Container(
                content=ft.Row([
                    quantity_container, 
                    ft.VerticalDivider(width=1, color=ft.colors.OUTLINE),
                    product_info_container,
                    ft.VerticalDivider(width=1, color=ft.colors.OUTLINE),
                    image_container
                ], 
                spacing=0, 
                alignment=ft.CrossAxisAlignment.STRETCH),
                border=ft.border.all(2, ft.colors.OUTLINE),
                border_radius=8,
                padding=ft.padding.all(10),
                margin=ft.margin.only(bottom=15),
                bgcolor=ft.colors.WHITE12
            )

            results_column.controls.append(outer_container)

        return total_price

    def update_top_3(self, top_3):
        self.top_3_results.controls.clear()
        for product in top_3:
            product_info_container = ft.Container(
                content=ft.Column([
                    ft.Text(f"Name: {product['name']}", weight=ft.FontWeight.BOLD, size=14, text_align=ft.TextAlign.LEFT),
                    ft.Text(f"Price: ${product['effective_price']:.2f}", size=14, text_align=ft.TextAlign.LEFT),
                    ft.Text(f"Weight: {product['weight_lb']:.2f} lbs", size=14, text_align=ft.TextAlign.LEFT),
                    ft.Text(f"Price by Weight: {product['price_by_weight']}", size=14, text_align=ft.TextAlign.LEFT),
                    ft.Text(f"lb/dollar: {product['lb_per_dollar']:.4f}", size=14, text_align=ft.TextAlign.LEFT),
                    ft.Container(height=10),  # Spacer
                    ft.ElevatedButton(
                        "View Product",
                        on_click=lambda e, link=product['link']: self.open_url(link),
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=5),
                padding=ft.padding.all(10),
                expand=True,
            )

            image_container = ft.Container(
                content=ft.Image(
                    src=product.get('image_url', ''),
                    width=120,
                    height=None,
                    fit=ft.ImageFit.CONTAIN
                ) if 'image_url' in product else ft.Container(width=120),
                alignment=ft.alignment.center,
                width=120,
                expand=True,
            )

            outer_container = ft.Container(
                content=ft.Row([
                    product_info_container,
                    ft.VerticalDivider(width=1, color=ft.colors.OUTLINE),
                    image_container
                ], 
                spacing=0, 
                alignment=ft.CrossAxisAlignment.STRETCH),
                border=ft.border.all(2, ft.colors.OUTLINE),
                border_radius=8,
                padding=ft.padding.all(10),
                margin=ft.margin.only(bottom=15),
                bgcolor=ft.colors.WHITE12
            )

            self.top_3_results.controls.append(outer_container)

    def highlight_best_performance(self):
        best_performance = max(
            self.optimization_results.items(),
            key=lambda x: x[1]["total_weight"] / x[1]["total_price"] if x[1]["total_price"] > 0 else 0
        )
        for title, data in self.optimization_results.items():
            if title == best_performance[0]:
                data["bgcolor"] = ft.colors.GREY_200
            else:
                data["bgcolor"] = ft.colors.WHITE

    def open_url(self, url):
        self.page.launch_url(url)