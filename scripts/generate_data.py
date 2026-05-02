"""
Data Generator — Retail Superstore KPI Dataset
Mimics Kaggle 'Sample Superstore' dataset structure
Generates synthetic data for portfolio use (no IP issues)
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)
np.random.seed(42)

# Config
N_ORDERS = 5000
START_DATE = datetime(2021, 1, 1)
END_DATE = datetime(2024, 12, 31)

CATEGORIES = {
    "Technology": ["Phones", "Accessories", "Machines", "Copiers"],
    "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
    "Office Supplies": ["Binders", "Paper", "Storage", "Art", "Labels", "Fasteners"]
}

REGIONS = ["North", "South", "East", "West"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

rows = []
for i in range(N_ORDERS):
    order_date = random_date(START_DATE, END_DATE)
    ship_days = {"Standard Class": 5, "Second Class": 3, "First Class": 2, "Same Day": 0}
    ship_mode = random.choice(SHIP_MODES)
    ship_date = order_date + timedelta(days=ship_days[ship_mode] + random.randint(0, 2))

    category = random.choice(list(CATEGORIES.keys()))
    sub_category = random.choice(CATEGORIES[category])

    # Realistic pricing
    base_price = {"Technology": 400, "Furniture": 250, "Office Supplies": 50}[category]
    unit_price = round(random.uniform(base_price * 0.3, base_price * 2.5), 2)
    quantity = random.randint(1, 10)
    discount = random.choice([0, 0, 0, 0.1, 0.2, 0.3, 0.5])  # mostly no discount
    sales = round(unit_price * quantity * (1 - discount), 2)
    profit_margin = random.uniform(-0.1, 0.4)
    profit = round(sales * profit_margin, 2)

    rows.append({
        "order_id": f"ORD-{2021 + i // 1500}-{str(i).zfill(5)}",
        "order_date": order_date.strftime("%Y-%m-%d"),
        "ship_date": ship_date.strftime("%Y-%m-%d"),
        "ship_mode": ship_mode,
        "customer_id": f"CUST-{random.randint(1000, 3000):04d}",
        "customer_name": fake.name(),
        "segment": random.choice(SEGMENTS),
        "city": fake.city(),
        "state": fake.state(),
        "region": random.choice(REGIONS),
        "product_id": f"PROD-{sub_category[:3].upper()}-{random.randint(100, 999)}",
        "category": category,
        "sub_category": sub_category,
        "product_name": f"{fake.word().capitalize()} {sub_category} {random.choice(['Pro','Elite','Standard','Plus'])}",
        "sales": sales,
        "quantity": quantity,
        "discount": discount,
        "profit": profit,
        "unit_price": unit_price
    })

df = pd.DataFrame(rows)
df.to_csv("/home/claude/realtime-kpi-dashboard/data/superstore_sales.csv", index=False)
print(f"Generated {len(df)} rows")
print(df.head(3))
print(f"\nTotal Sales: £{df['sales'].sum():,.0f}")
print(f"Total Profit: £{df['profit'].sum():,.0f}")
print(f"Date range: {df['order_date'].min()} → {df['order_date'].max()}")
