import flet as ft
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os

class SearchView(ft.UserControl):
    def __init__(self, search_callback):
        super().__init__()
        self.search_callback = search_callback
        self.input_height = 50  # Match the height used in MainView
        self.search_term = ft.TextField(
            label="Product Search Term",
            expand=True,
            height=self.input_height,
        )
        self.search_button = ft.ElevatedButton(
            "Scrape",
            on_click=self.handle_search,
            height=self.input_height,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )
        self.progress_bar = ft.ProgressBar(visible=False)

    def build(self):
        return ft.Column([
            ft.Row([
                self.search_term,
                ft.Container(width=10),  # Add spacing between field and button
                self.search_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.progress_bar
        ], alignment=ft.MainAxisAlignment.START, spacing=10)

    def handle_search(self, e):
        if self.search_term.value:
            self.progress_bar.visible = True
            self.update()
            products = self.scrape_products(self.search_term.value)
            self.search_callback(products)
            self.progress_bar.visible = False
            self.update()
        else:
            print("Please enter a search term")

    def scrape_products(self, search_term):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        driver = webdriver.Chrome(service=service, options=options)

        url = f'https://www.supermarket23.com/en/buscar?q={search_term}'
        driver.get(url)

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'single_product')))

        total_results_element = driver.find_element(By.XPATH, '//p[contains(text(),"Showing")]')
        total_results_text = total_results_element.text
        total_results = int(total_results_text.split()[-2])
        results_per_page = 20
        total_pages = (total_results // results_per_page) + 1

        products = []
        for page in range(1, total_pages + 1):
            if page > 1:
                page_url = f"{url}&pagina={page}"
                driver.get(page_url)
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'single_product')))
            
            product_elements = driver.find_elements(By.CLASS_NAME, 'single_product')

            for product in product_elements:
                try:
                    name_element = WebDriverWait(product, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h3 > a')))
                    price_element = product.find_elements(By.CSS_SELECTOR, 'span.current_price')
                    if not price_element:
                        price_element = product.find_elements(By.CSS_SELECTOR, 'span.regular_price')
                    old_price_element = product.find_elements(By.CSS_SELECTOR, 'span.old_price')
                    price_by_weight_element = product.find_elements(By.CSS_SELECTOR, 'span.price-by-weight')
                    
                    name = name_element.get_attribute('innerText').strip() if name_element else "No name found"
                    price = price_element[0].get_attribute('innerText').strip() if price_element else "No price found"
                    old_price = old_price_element[0].get_attribute('innerText').strip() if old_price_element else "No old price found"
                    price_by_weight = price_by_weight_element[0].get_attribute('innerText').strip() if price_by_weight_element else "No price by weight found"
                    link = product.find_element(By.CSS_SELECTOR, 'div.product_thumb > a').get_attribute('href')
                    
                    product_number = link.split('/')[-1]
                    image_url = f"https://medias.treew.com/imgproducts/middle/{product_number}.jpg"
                    print(f"Product: {name}, Image URL: {image_url}")  # Debug message
                    
                    product_info = {
                        'name': name,
                        'price': float(price.replace('$', '').replace(',', '')),
                        'old_price': float(old_price.replace('$', '').replace(',', '')) if old_price != "No old price found" else None,
                        'price_by_weight': price_by_weight,
                        'link': link,
                        'image_url': image_url
                    }
                    products.append(product_info)
                except Exception as e:
                    print(f"Error processing product: {e}")

        driver.quit()

        # Save the data in a CSV file
        keys = products[0].keys()
        file_path = 'products.csv'
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(products)
            print(f"File saved successfully at {os.path.abspath(file_path)}")
        except Exception as e:
            print(f"Error saving file: {e}")

        return products
