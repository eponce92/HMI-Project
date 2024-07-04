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

def optimize_purchase(products, budget):
    df = pd.DataFrame(products)

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

    top_3 = df.sort_values('lb_per_dollar', ascending=False).head(3)

    df = df.sort_values('lb_per_dollar', ascending=False).reset_index(drop=True)
    n = len(df)
    budget = float(budget)

    dp = [[0 for _ in range(int(budget * 100) + 1)] for _ in range(n + 1)]
    selected = [[[] for _ in range(int(budget * 100) + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(int(budget * 100) + 1):
            price = int(df.iloc[i-1]['effective_price'] * 100)
            weight = df.iloc[i-1]['weight_lb']
            
            if price <= w:
                if dp[i-1][w] < dp[i-1][w-price] + weight:
                    dp[i][w] = dp[i-1][w-price] + weight
                    selected[i][w] = selected[i-1][w-price] + [i-1]
                else:
                    dp[i][w] = dp[i-1][w]
                    selected[i][w] = selected[i-1][w]
            else:
                dp[i][w] = dp[i-1][w]
                selected[i][w] = selected[i-1][w]

    selected_indices = selected[n][int(budget * 100)]
    total_weight = dp[n][int(budget * 100)]
    selected_products = df.iloc[selected_indices].to_dict('records')

    return selected_products, total_weight, top_3.to_dict('records')