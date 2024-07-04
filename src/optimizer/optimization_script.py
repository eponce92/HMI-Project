import pandas as pd
import numpy as np
import re

def clean_price(price):
    if isinstance(price, str):
        return float(price.replace('$', '').replace(',', '').strip())
    elif isinstance(price, (int, float)):
        return float(price)
    else:
        return np.nan

def extract_weight_lb(name):
    kg_match = re.search(r'(\d+(?:\.\d+)?)\s*kg', name, re.IGNORECASE)
    lb_match = re.search(r'(\d+(?:\.\d+)?)\s*lb', name, re.IGNORECASE)
    
    if kg_match:
        return float(kg_match.group(1)) * 2.20462  # Convert kg to lb
    elif lb_match:
        return float(lb_match.group(1))
    else:
        return np.nan

def extract_price_per_lb(price_by_weight):
    match = re.search(r'\$(\d+(?:\.\d+)?)/lb', price_by_weight, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return np.nan

def get_effective_price(row):
    if pd.notna(row['old_price']) and row['old_price'] < row['price']:
        return row['old_price']
    return row['price']

def optimize_purchase(products, budget, exclude_words):
    df = pd.DataFrame(products)

    # Apply exclusion filter
    exclude_pattern = '|'.join(map(re.escape, exclude_words))
    df = df[~df['name'].str.lower().str.contains(exclude_pattern, case=False, na=False)]

    df['price'] = df['price'].apply(clean_price)
    df['old_price'] = df['old_price'].apply(lambda x: clean_price(x) if pd.notna(x) else np.nan)
    df['effective_price'] = df.apply(get_effective_price, axis=1)
    df['weight_lb'] = df['name'].apply(extract_weight_lb)
    df['price_per_lb'] = df['price_by_weight'].apply(extract_price_per_lb)

    df['lb_per_dollar'] = np.where(
        df['price_per_lb'].notna(),
        1 / df['price_per_lb'],
        df['weight_lb'] / df['effective_price']
    )

    df = df.dropna(subset=['effective_price', 'weight_lb', 'lb_per_dollar'])

    top_3 = df.sort_values('lb_per_dollar', ascending=False).head(3).to_dict('records')

    df = df.sort_values('lb_per_dollar', ascending=False).reset_index(drop=True)
    budget = float(budget)

    selected_products = []
    total_weight = 0
    total_price = 0

    for _, product in df.iterrows():
        if total_price + product['effective_price'] <= budget:
            selected_products.append(product.to_dict())
            total_weight += product['weight_lb']
            total_price += product['effective_price']
        else:
            # Try to fit smaller items if there's remaining budget
            remaining_budget = budget - total_price
            smaller_products = df[(df['effective_price'] <= remaining_budget) & 
                                  (~df.index.isin([p['name'] for p in selected_products]))]
            if not smaller_products.empty:
                best_smaller_product = smaller_products.iloc[0]
                selected_products.append(best_smaller_product.to_dict())
                total_weight += best_smaller_product['weight_lb']
                total_price += best_smaller_product['effective_price']
            else:
                break

    return selected_products, total_weight, top_3