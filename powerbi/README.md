# Power BI — Connection & Dashboard Setup

## Connect to MySQL

1. Open Power BI Desktop
2. **Get Data** → **MySQL Database**
3. Server: `localhost` | Database: `retail_kpi_db`
4. Import these views:
   - `vw_monthly_kpi` — for trend charts
   - `vw_region_kpi` — for map/bar charts
   - `vw_category_kpi` — for category breakdown
   - `vw_segment_kpi` — for donut chart
   - `vw_yoy_growth` — for YoY line chart

## Recommended Visuals

| Visual | View | Fields |
|--------|------|--------|
| Line chart | vw_monthly_kpi | month_name → total_revenue, total_profit |
| Bar chart | vw_region_kpi | region → total_revenue |
| Donut | vw_segment_kpi | segment → total_revenue |
| Table | vw_category_kpi | All fields |
| KPI Card | vw_monthly_kpi | SUM(total_revenue) |
| YoY Line | vw_yoy_growth | year/month → yoy_growth_pct |

## DAX Measures (add in Power BI)

```dax
Profit Margin % = 
DIVIDE(SUM(fact_sales[profit]), SUM(fact_sales[sales]), 0) * 100

Avg Order Value = 
AVERAGEX(VALUES(fact_sales[order_id]), CALCULATE(SUM(fact_sales[sales])))

MoM Revenue Growth % = 
VAR current = SUM(fact_sales[sales])
VAR prior   = CALCULATE(SUM(fact_sales[sales]), DATEADD(dim_date[full_date], -1, MONTH))
RETURN DIVIDE(current - prior, prior, 0) * 100
```
