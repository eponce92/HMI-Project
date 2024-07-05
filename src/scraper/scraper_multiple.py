from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import csv
import os
import requests

def scrape_products(search_term):
    # Configurar el servicio del navegador y la instancia del controlador
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')  # Use the new headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')  # Disable GPU acceleration (optional)
    options.add_argument('start-maximized')  # Open browser in maximized mode (optional)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Solicitar la entrada del usuario
        url = f'https://www.supermarket23.com/en/buscar?q={search_term}'
        driver.get(url)

        # Espera dinámica hasta que los elementos se carguen (máximo 10 segundos)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'single_product')))

        # Obtener el texto del total de resultados
        total_results_element = driver.find_element(By.XPATH, '//p[contains(text(),"Showing")]')
        total_results_text = total_results_element.text
        total_results = int(total_results_text.split()[-2])  # Obtener el número total de resultados
        results_per_page = 20  # Ajusta según sea necesario
        total_pages = (total_results // results_per_page) + 1

        products = []

        # Iterar sobre cada página
        for page in range(1, total_pages + 1):
            if page > 1:
                page_url = f"{url}&pagina={page}"
                driver.get(page_url)
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'single_product')))
            
            product_elements = driver.find_elements(By.CLASS_NAME, 'single_product')

            for product in product_elements:
                name_element = WebDriverWait(product, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h3 > a')))
                price_element = product.find_elements(By.CSS_SELECTOR, 'span.current_price')
                if not price_element:
                    price_element = product.find_elements(By.CSS_SELECTOR, 'span.regular_price')
                old_price_element = product.find_elements(By.CSS_SELECTOR, 'span.old_price')
                price_by_weight_element = product.find_elements(By.CSS_SELECTOR, 'span.price-by-weight')
                
                # Obtener el texto de los elementos
                name = name_element.get_attribute('innerText').strip() if name_element else "No name found"
                price = price_element[0].get_attribute('innerText').strip() if price_element else "No price found"
                old_price = old_price_element[0].get_attribute('innerText').strip() if old_price_element else "No old price found"
                price_by_weight = price_by_weight_element[0].get_attribute('innerText').strip() if price_by_weight_element else "No price by weight found"
                link = product.find_element(By.CSS_SELECTOR, 'div.product_thumb > a').get_attribute('href')
                
                # Extraer el número del producto de la URL
                product_number = link.split('/')[-1]
                image_url = f"https://medias.treew.com/imgproducts/middle/{product_number}.jpg"
                
                # Verify the image URL
                try:
                    response = requests.head(image_url)
                    if response.status_code != 200:
                        image_url = ""
                except Exception as e:
                    image_url = ""
                    print(f"Error verifying image URL: {e}")
                
                print(f"Product: {name}, Image URL: {image_url}")  # Mensaje de depuración
                
                product_info = {
                    'name': name,
                    'price': float(price.replace('$', '').replace(',', '')),
                    'old_price': float(old_price.replace('$', '').replace(',', '')) if old_price != "No old price found" else None,
                    'price_by_weight': price_by_weight,
                    'link': link,
                    'image_url': image_url  # Agregar la URL de la imagen
                }
                products.append(product_info)
    finally:
        driver.quit()

    # Guardar los datos en un archivo CSV
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
