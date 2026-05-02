# Data Model — Star Schema

## ERD Overview

```
                        ┌─────────────────┐
                        │   dim_date      │
                        │─────────────────│
                        │ date_key (PK)   │
                        │ full_date       │
                        │ day_of_week     │
                        │ month_name      │
                        │ quarter         │
                        │ year            │
                        │ is_weekend      │
                        └────────┬────────┘
                    order_date_key│  ship_date_key
                                  │
┌─────────────────┐   ┌──────────┴──────────┐   ┌─────────────────┐
│  dim_customer   │   │     fact_sales       │   │  dim_product    │
│─────────────────│   │─────────────────────│   │─────────────────│
│ customer_key(PK)├───│ sale_id (PK)        ├───│ product_key(PK) │
│ customer_id     │   │ order_id            │   │ product_id      │
│ customer_name   │   │ order_date_key (FK) │   │ product_name    │
│ segment         │   │ ship_date_key  (FK) │   │ category        │
│ city            │   │ customer_key   (FK) │   │ sub_category    │
│ state           │   │ product_key    (FK) │   └─────────────────┘
│ region          │   │ shipment_key   (FK) │
└─────────────────┘   │ quantity            │   ┌─────────────────┐
                       │ unit_price          │   │ dim_shipment    │
                       │ discount            │   │─────────────────│
                       │ sales               ├───│ shipment_key(PK)│
                       │ profit              │   │ ship_mode       │
                       │ ship_days           │   └─────────────────┘
                       └─────────────────────┘
```

## Table Descriptions

| Table | Type | Rows | Description |
|-------|------|------|-------------|
| `dim_date` | Dimension | ~1,460 | All dates 2021–2024, pre-calculated attributes |
| `dim_customer` | Dimension | ~1,839 | Unique customers with segment + location |
| `dim_product` | Dimension | ~500 | Product catalogue with category hierarchy |
| `dim_shipment` | Dimension | 4 | Ship mode lookup |
| `fact_sales` | Fact | 5,000 | Grain: one row per order-line-item |

## Key Design Decisions

1. **Grain**: Order-line level (not order header) — enables product-level analysis
2. **Date dimension**: Pre-calculated `is_weekend`, `quarter` — avoids runtime date functions
3. **Surrogate keys**: Auto-increment PKs on all dims — decoupled from source system IDs
4. **Indexes**: Composite indexes on `(order_date_key, customer_key)` and `(product_key, order_date_key)` for fast BI rollups
5. **Views**: 6 pre-built reporting views eliminate repeated complex JOINs in BI tools
