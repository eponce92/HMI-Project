import pandas as pd
import numpy as np
import re

def clean_price(price):
    if isinstance(price, str):
        return float(price.replace('$', '').strip())
    elif isinstance(price, (int, float)):
        return float(price)
    else:
        return np.nan

def extract_weight_lb(name):
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|lb)', name, re.IGNORECASE)
    if match:
        value = float(match.group(1))
        unit = match.group().lower()
        if 'kg' in unit:
            return value * 2.20462  # Convert kg to lb
        else:
            return value  # Already in pounds
    return np.nan

def extract_price_per_lb(price_by_weight):
    match = re.search(r'\$(\d+(?:\.\d+)?)/lb', price_by_weight, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return np.nan

def optimize_purchase(products, budget):
    df = pd.DataFrame(products)
    
    df['price'] = df['price'].apply(clean_price)
    df['weight_lb'] = df['name'].apply(extract_weight_lb)
    df['lb_per_dollar'] = df['weight_lb'] / df['price']
    df['price_per_lb'] = df['price_by_weight'].apply(extract_price_per_lb)
    
    df = df.dropna(subset=['price', 'weight_lb', 'lb_per_dollar'])
    
    n = len(df)
    dp = [[0 for _ in range(int(budget) + 1)] for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        for w in range(1, int(budget) + 1):
            if df.iloc[i-1]['price'] <= w:
                dp[i][w] = max(dp[i-1][w], 
                               dp[i-1][int(w - df.iloc[i-1]['price'])] + df.iloc[i-1]['weight_lb'])
            else:
                dp[i][w] = dp[i-1][w]
    
    # Reconstruct the solution
    w = int(budget)
    selected_items = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected_items.append(i-1)
            w = int(w - df.iloc[i-1]['price'])
    
    selected_items.reverse()
    
    return selected_items, dp[n][int(budget)]

# Example usage (can be removed in production)
if __name__ == "__main__":
    # Sample data
    products = [
        {"name": "Apple 1lb", "price": 2.0, "old_price": 2.5, "price_by_weight": "$2.0/lb", "link": "http://example.com/apple"},
        {"name": "Banana 2kg", "price": 3.0, "old_price": 3.5, "price_by_weight": "$0.68/lb", "link": "http://example.com/banana"},
        {"name": "Orange Juice 64 oz", "price": 4.0, "old_price": 4.5, "price_by_weight": "$0.0625/oz", "link": "http://example.com/orange-juice"},
    ]
    budget = 10.0
    
    selected_indices, max_weight = optimize_purchase(products, budget)
    selected = [products[i] for i in selected_indices]
    print(f"Selected items: {selected}")
    print(f"Total weight: {max_weight} lbs")
    print(f"Total price: ${sum(item['price'] for item in selected)}")