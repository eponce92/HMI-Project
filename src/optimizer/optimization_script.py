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

def calculate_value_to_weight_ratio(row):
    return row['weight_lb'] / row['effective_price'] if row['effective_price'] > 0 else 0

def preprocess_data(products, exclude_words, budget):
    df = pd.DataFrame(products)

    # Apply exclusion filter if there are any exclude words
    if exclude_words:
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

    # Filter out products that exceed the budget
    df = df[df['effective_price'] <= budget]

    df = df.dropna(subset=['effective_price', 'weight_lb', 'lb_per_dollar'])
    return df

def get_top_3(df):
    return df.sort_values('lb_per_dollar', ascending=False).head(3).to_dict('records')

def optimize_purchase_greedy(products, budget, exclude_words):
    df = preprocess_data(products, exclude_words, budget)
    df = df.sort_values('lb_per_dollar', ascending=False).reset_index(drop=True)
    
    selected_products = []
    total_weight = 0
    total_price = 0

    for _, product in df.iterrows():
        quantity = int((budget - total_price) // product['effective_price'])
        if quantity > 0:
            for _ in range(quantity):
                if total_price + product['effective_price'] <= budget:
                    selected_products.append(product.to_dict())
                    total_weight += product['weight_lb']
                    total_price += product['effective_price']
                else:
                    break

    top_3 = get_top_3(df)
    return selected_products, total_weight, top_3

def optimize_purchase_knapsack(products, budget, exclude_words):
    df = preprocess_data(products, exclude_words, budget)
    n = len(df)
    weights = df['effective_price'].tolist()
    values = df['weight_lb'].tolist()
    
    # Create a 2D array to store the maximum value at each step
    dp = [[0 for _ in range(int(budget) + 1)] for _ in range(n + 1)]
    
    # Fill the dp array
    for i in range(1, n + 1):
        for w in range(int(budget) + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(values[i-1] + dp[i-1][int(w-weights[i-1])], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]
    
    # Backtrack to find the selected items
    selected_products = []
    total_weight = 0
    w = int(budget)
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            quantity = int(w // weights[i-1])
            for _ in range(quantity):
                selected_products.append(df.iloc[i-1].to_dict())
                total_weight += values[i-1]
                w -= int(weights[i-1])
    
    top_3 = get_top_3(df)
    return selected_products, total_weight, top_3

def optimize_purchase_ratio(products, budget, exclude_words):
    df = preprocess_data(products, exclude_words, budget)
    df['value_to_weight_ratio'] = df.apply(calculate_value_to_weight_ratio, axis=1)
    df = df.sort_values('value_to_weight_ratio', ascending=False).reset_index(drop=True)
    
    selected_products = []
    total_weight = 0
    total_price = 0

    for _, product in df.iterrows():
        quantity = int((budget - total_price) // product['effective_price'])
        if quantity > 0:
            for _ in range(quantity):
                if total_price + product['effective_price'] <= budget:
                    selected_products.append(product.to_dict())
                    total_weight += product['weight_lb']
                    total_price += product['effective_price']
                else:
                    break

    top_3 = get_top_3(df)
    return selected_products, total_weight, top_3
