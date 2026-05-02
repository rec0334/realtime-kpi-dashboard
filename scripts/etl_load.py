"""
ETL Pipeline: Load Superstore CSV → Star Schema (MySQL)
Author: Revanth Reddy Chitti
Project: Real-Time KPI Dashboard

Steps:
  1. Extract  — read raw CSV
  2. Transform — build dimension & fact records
  3. Load      — insert into MySQL star schema

Usage:
  pip install pandas sqlalchemy pymysql
  python scripts/etl_load.py
"""

import pandas as pd
from sqlalchemy import create_engine, text
import logging
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────
DB_USER     = "root"
DB_PASSWORD = "your_password"
DB_HOST     = "localhost"
DB_PORT     = 3306
DB_NAME     = "retail_kpi_db"
CSV_PATH    = "data/superstore_sales.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ── Connect ─────────────────────────────────────────────────────────────────
def get_engine():
    url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url, echo=False)

# ── Extract ─────────────────────────────────────────────────────────────────
def extract(path: str) -> pd.DataFrame:
    log.info(f"Reading CSV: {path}")
    df = pd.read_csv(path, parse_dates=["order_date", "ship_date"])
    log.info(f"Extracted {len(df):,} rows | columns: {list(df.columns)}")
    return df

# ── Transform: dim_date ─────────────────────────────────────────────────────
def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    all_dates = pd.concat([df["order_date"], df["ship_date"]]).drop_duplicates()
    records = []
    for d in all_dates:
        records.append({
            "date_key":     int(d.strftime("%Y%m%d")),
            "full_date":    d.date(),
            "day_of_week":  d.strftime("%A"),
            "day_num":      d.day,
            "week_num":     d.isocalendar()[1],
            "month_num":    d.month,
            "month_name":   d.strftime("%B"),
            "quarter":      (d.month - 1) // 3 + 1,
            "year":         d.year,
            "is_weekend":   d.weekday() >= 5,
            "is_month_end": d.is_month_end
        })
    dim = pd.DataFrame(records).drop_duplicates("date_key")
    log.info(f"dim_date: {len(dim)} rows")
    return dim

# ── Transform: dim_customer ─────────────────────────────────────────────────
def build_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    dim = df[["customer_id","customer_name","segment","city","state","region"]] \
            .drop_duplicates("customer_id") \
            .reset_index(drop=True)
    log.info(f"dim_customer: {len(dim)} rows")
    return dim

# ── Transform: dim_product ──────────────────────────────────────────────────
def build_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    dim = df[["product_id","product_name","category","sub_category"]] \
            .drop_duplicates("product_id") \
            .reset_index(drop=True)
    log.info(f"dim_product: {len(dim)} rows")
    return dim

# ── Transform: dim_shipment ─────────────────────────────────────────────────
def build_dim_shipment(df: pd.DataFrame) -> pd.DataFrame:
    dim = pd.DataFrame({"ship_mode": df["ship_mode"].unique()})
    log.info(f"dim_shipment: {len(dim)} rows")
    return dim

# ── Transform: fact_sales ───────────────────────────────────────────────────
def build_fact_sales(df, dim_customer, dim_product, dim_shipment):
    fact = df.copy()

    # Map keys
    cust_map  = dim_customer.set_index("customer_id")["customer_key"].to_dict()  if "customer_key" in dim_customer.columns else {}
    prod_map  = dim_product.set_index("product_id")["product_key"].to_dict()    if "product_key"  in dim_product.columns  else {}
    ship_map  = dim_shipment.set_index("ship_mode")["shipment_key"].to_dict()   if "shipment_key" in dim_shipment.columns  else {}

    fact["order_date_key"] = fact["order_date"].dt.strftime("%Y%m%d").astype(int)
    fact["ship_date_key"]  = fact["ship_date"].dt.strftime("%Y%m%d").astype(int)
    fact["ship_days"]      = (fact["ship_date"] - fact["order_date"]).dt.days

    if cust_map:
        fact["customer_key"] = fact["customer_id"].map(cust_map)
        fact["product_key"]  = fact["product_id"].map(prod_map)
        fact["shipment_key"] = fact["ship_mode"].map(ship_map)

    cols = ["order_id","order_date_key","ship_date_key","customer_key",
            "product_key","shipment_key","quantity","unit_price","discount",
            "sales","profit","ship_days"]
    log.info(f"fact_sales: {len(fact):,} rows")
    return fact[cols] if cust_map else fact

# ── Load ────────────────────────────────────────────────────────────────────
def load_table(df, table, engine, if_exists="append"):
    df.to_sql(table, engine, if_exists=if_exists, index=False, chunksize=500)
    log.info(f"Loaded → {table}: {len(df):,} rows")

# ── Main ETL ────────────────────────────────────────────────────────────────
def run_etl():
    start = datetime.now()
    log.info("=" * 55)
    log.info("ETL START")
    log.info("=" * 55)

    engine = get_engine()
    df     = extract(CSV_PATH)

    # Build dimensions
    dim_date     = build_dim_date(df)
    dim_customer = build_dim_customer(df)
    dim_product  = build_dim_product(df)
    dim_shipment = build_dim_shipment(df)

    # Load dimensions first (FK deps)
    load_table(dim_date,     "dim_date",     engine, if_exists="replace")
    load_table(dim_customer, "dim_customer", engine, if_exists="replace")
    load_table(dim_product,  "dim_product",  engine, if_exists="replace")
    load_table(dim_shipment, "dim_shipment", engine, if_exists="replace")

    # Re-fetch with auto keys for fact mapping
    dim_customer_db = pd.read_sql("SELECT customer_key, customer_id FROM dim_customer", engine)
    dim_product_db  = pd.read_sql("SELECT product_key, product_id FROM dim_product",   engine)
    dim_shipment_db = pd.read_sql("SELECT shipment_key, ship_mode FROM dim_shipment",  engine)

    # Build + load fact
    fact = build_fact_sales(df, dim_customer_db, dim_product_db, dim_shipment_db)
    load_table(fact, "fact_sales", engine, if_exists="replace")

    elapsed = (datetime.now() - start).seconds
    log.info(f"ETL COMPLETE in {elapsed}s ✓")
    log.info("=" * 55)

if __name__ == "__main__":
    run_etl()
