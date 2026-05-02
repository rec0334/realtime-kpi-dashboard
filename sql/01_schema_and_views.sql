-- ============================================================
-- PROJECT 6: Real-Time KPI Dashboard
-- Database: retail_kpi_db
-- Schema: Star Schema (Fact + Dimension tables)
-- Author: Revanth Reddy Chitti
-- ============================================================

-- ============================================================
-- STEP 1: CREATE DATABASE
-- ============================================================
CREATE DATABASE IF NOT EXISTS retail_kpi_db;
USE retail_kpi_db;

-- ============================================================
-- STEP 2: DIMENSION TABLES
-- ============================================================

-- DIM: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_key        INT PRIMARY KEY,           -- YYYYMMDD format
    full_date       DATE NOT NULL,
    day_of_week     VARCHAR(10),
    day_num         TINYINT,
    week_num        TINYINT,
    month_num       TINYINT,
    month_name      VARCHAR(10),
    quarter         TINYINT,
    year            SMALLINT,
    is_weekend      BOOLEAN,
    is_month_end    BOOLEAN
);

-- DIM: Customer
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key    INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     VARCHAR(20) UNIQUE NOT NULL,
    customer_name   VARCHAR(100),
    segment         VARCHAR(30),       -- Consumer / Corporate / Home Office
    city            VARCHAR(100),
    state           VARCHAR(100),
    region          VARCHAR(20)        -- North / South / East / West
);

-- DIM: Product
CREATE TABLE IF NOT EXISTS dim_product (
    product_key     INT AUTO_INCREMENT PRIMARY KEY,
    product_id      VARCHAR(30) UNIQUE NOT NULL,
    product_name    VARCHAR(200),
    category        VARCHAR(50),       -- Technology / Furniture / Office Supplies
    sub_category    VARCHAR(50)
);

-- DIM: Ship Mode
CREATE TABLE IF NOT EXISTS dim_shipment (
    shipment_key    INT AUTO_INCREMENT PRIMARY KEY,
    ship_mode       VARCHAR(30) UNIQUE NOT NULL   -- Standard / Second / First / Same Day
);

-- ============================================================
-- STEP 3: FACT TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id        VARCHAR(30) NOT NULL,
    order_date_key  INT NOT NULL,
    ship_date_key   INT NOT NULL,
    customer_key    INT NOT NULL,
    product_key     INT NOT NULL,
    shipment_key    INT NOT NULL,

    -- Measures
    quantity        INT NOT NULL DEFAULT 1,
    unit_price      DECIMAL(10,2),
    discount        DECIMAL(4,2) DEFAULT 0.00,
    sales           DECIMAL(12,2) NOT NULL,
    profit          DECIMAL(12,2),
    ship_days       TINYINT,           -- derived: ship_date - order_date

    -- Constraints
    FOREIGN KEY (order_date_key)  REFERENCES dim_date(date_key),
    FOREIGN KEY (ship_date_key)   REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_key)    REFERENCES dim_customer(customer_key),
    FOREIGN KEY (product_key)     REFERENCES dim_product(product_key),
    FOREIGN KEY (shipment_key)    REFERENCES dim_shipment(shipment_key),

    INDEX idx_order_date (order_date_key),
    INDEX idx_customer   (customer_key),
    INDEX idx_product    (product_key)
);

-- ============================================================
-- STEP 4: KPI VIEWS (reporting layer)
-- ============================================================

-- VIEW 1: Monthly Revenue & Profit Summary
CREATE OR REPLACE VIEW vw_monthly_kpi AS
SELECT
    d.year,
    d.month_num,
    d.month_name,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    SUM(f.quantity)                     AS total_units,
    ROUND(SUM(f.sales), 2)              AS total_revenue,
    ROUND(SUM(f.profit), 2)             AS total_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(f.sales), 2)              AS avg_order_value
FROM fact_sales f
JOIN dim_date d ON f.order_date_key = d.date_key
GROUP BY d.year, d.month_num, d.month_name
ORDER BY d.year, d.month_num;

-- VIEW 2: Revenue by Region
CREATE OR REPLACE VIEW vw_region_kpi AS
SELECT
    c.region,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    COUNT(DISTINCT f.customer_key)      AS unique_customers,
    ROUND(SUM(f.sales), 2)              AS total_revenue,
    ROUND(SUM(f.profit), 2)             AS total_profit,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.region
ORDER BY total_revenue DESC;

-- VIEW 3: Category Performance
CREATE OR REPLACE VIEW vw_category_kpi AS
SELECT
    p.category,
    p.sub_category,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    SUM(f.quantity)                     AS units_sold,
    ROUND(SUM(f.sales), 2)              AS total_revenue,
    ROUND(SUM(f.profit), 2)             AS total_profit,
    ROUND(AVG(f.discount) * 100, 1)    AS avg_discount_pct,
    ROUND(SUM(f.profit) / NULLIF(SUM(f.sales), 0) * 100, 2) AS profit_margin_pct
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category, p.sub_category
ORDER BY total_revenue DESC;

-- VIEW 4: Customer Segment KPIs
CREATE OR REPLACE VIEW vw_segment_kpi AS
SELECT
    c.segment,
    COUNT(DISTINCT f.customer_key)      AS unique_customers,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    ROUND(SUM(f.sales), 2)              AS total_revenue,
    ROUND(SUM(f.profit), 2)             AS total_profit,
    ROUND(AVG(f.sales), 2)             AS avg_order_value
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.segment
ORDER BY total_revenue DESC;

-- VIEW 5: Top 10 Products by Revenue
CREATE OR REPLACE VIEW vw_top_products AS
SELECT
    p.product_name,
    p.category,
    p.sub_category,
    SUM(f.quantity)                     AS units_sold,
    ROUND(SUM(f.sales), 2)              AS total_revenue,
    ROUND(SUM(f.profit), 2)             AS total_profit
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category, p.sub_category
ORDER BY total_revenue DESC
LIMIT 10;

-- VIEW 6: YoY Growth (Year-over-Year comparison)
CREATE OR REPLACE VIEW vw_yoy_growth AS
SELECT
    curr.year,
    curr.month_num,
    curr.month_name,
    curr.total_revenue AS revenue_current_year,
    prev.total_revenue AS revenue_prior_year,
    ROUND(
        (curr.total_revenue - prev.total_revenue)
        / NULLIF(prev.total_revenue, 0) * 100, 2
    ) AS yoy_growth_pct
FROM vw_monthly_kpi curr
LEFT JOIN vw_monthly_kpi prev
    ON curr.month_num = prev.month_num
    AND curr.year = prev.year + 1
ORDER BY curr.year, curr.month_num;

-- ============================================================
-- STEP 5: STORED PROCEDURES (operational queries)
-- ============================================================

DELIMITER $$

-- Proc 1: Get KPI summary for a given year
CREATE PROCEDURE sp_annual_kpi(IN p_year INT)
BEGIN
    SELECT
        p_year                          AS report_year,
        COUNT(DISTINCT f.order_id)      AS total_orders,
        COUNT(DISTINCT f.customer_key)  AS unique_customers,
        ROUND(SUM(f.sales), 2)          AS total_revenue,
        ROUND(SUM(f.profit), 2)         AS total_profit,
        ROUND(SUM(f.profit)/NULLIF(SUM(f.sales),0)*100,2) AS profit_margin_pct,
        ROUND(AVG(f.sales), 2)          AS avg_order_value
    FROM fact_sales f
    JOIN dim_date d ON f.order_date_key = d.date_key
    WHERE d.year = p_year;
END$$

-- Proc 2: Get top N customers by revenue
CREATE PROCEDURE sp_top_customers(IN p_limit INT)
BEGIN
    SELECT
        c.customer_name,
        c.segment,
        c.region,
        COUNT(DISTINCT f.order_id)  AS orders,
        ROUND(SUM(f.sales), 2)      AS lifetime_value,
        ROUND(SUM(f.profit), 2)     AS total_profit
    FROM fact_sales f
    JOIN dim_customer c ON f.customer_key = c.customer_key
    GROUP BY c.customer_key, c.customer_name, c.segment, c.region
    ORDER BY lifetime_value DESC
    LIMIT p_limit;
END$$

DELIMITER ;

-- ============================================================
-- STEP 6: OPTIMISED INDEXES (query performance)
-- ============================================================

-- Composite index for date + region reporting
CREATE INDEX idx_fact_date_region
    ON fact_sales(order_date_key, customer_key);

-- Index for product-level rollups
CREATE INDEX idx_fact_product_date
    ON fact_sales(product_key, order_date_key);
