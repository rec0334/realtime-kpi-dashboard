# Tableau — Connection & Dashboard Setup

## Connect to MySQL

1. Open Tableau Desktop
2. **Connect** → **MySQL**
3. Server: `localhost` | Port: `3306`
4. Database: `retail_kpi_db`
5. Connect to views (not raw tables) for best performance

## Recommended Views to Use

| Tableau Sheet | Source View | Chart Type |
|---------------|-------------|------------|
| Revenue Trend | vw_monthly_kpi | Dual-axis line + bar |
| Region Map | vw_region_kpi | Filled map or bar |
| Category Split | vw_category_kpi | Treemap |
| Segment Donut | vw_segment_kpi | Pie / Donut |
| YoY Growth | vw_yoy_growth | Line with reference line |
| Sub-Cat Margin | vw_category_kpi | Horizontal bar (sorted) |

## Calculated Fields

```
// Profit Margin %
SUM([profit]) / SUM([sales]) * 100

// Revenue per Customer
SUM([total_revenue]) / SUM([unique_customers])
```

## Dashboard Layout Suggestion

```
┌─────────────────┬──────────────┬──────────────┐
│  Revenue KPI    │  Profit KPI  │  Orders KPI  │  ← KPI cards (row 1)
├─────────────────┴──────────────┴──────────────┤
│         Monthly Revenue & Profit Trend        │  ← Line chart (row 2)
├─────────────────┬──────────────────────────────┤
│  Revenue by     │   Profit Margin by           │  ← Row 3
│  Region (Bar)   │   Sub-Category (Horiz Bar)   │
├─────────────────┼──────────────────────────────┤
│  Segment Donut  │   YoY Growth Line            │  ← Row 4
└─────────────────┴──────────────────────────────┘
```
