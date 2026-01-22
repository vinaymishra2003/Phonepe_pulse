use phonepe;
select * from aggregated_transaction;

-- transactions by state comparision
SELECT
    State,
    SUM(Transaction_count) AS total_transactions,
    SUM(Transaction_amount) AS total_amount
FROM aggregated_transaction
GROUP BY State
ORDER BY total_transactions DESC;

-- comparision of transaction by quarter
SELECT
    Year,
    Quarter,
    SUM(Transaction_count) AS total_transactions,
    SUM(Transaction_amount) AS total_amount
FROM aggregated_transaction
GROUP BY Year, Quarter
ORDER BY Year, Quarter;

-- transactions by payment category
SELECT
    Transaction_type,
    SUM(Transaction_count) AS total_transactions,
    SUM(Transaction_amount) AS total_amount
FROM aggregated_transaction
GROUP BY Transaction_type
ORDER BY total_transactions DESC;

-- States with consistent growth
WITH yearly_data AS (
  SELECT
    State,
    Year,
    SUM(Transaction_amount) AS total_amount
  FROM aggregated_transaction
  GROUP BY State, Year
),
growth AS (
  SELECT
    State,
    Year,
    total_amount,
    LAG(total_amount) OVER (PARTITION BY State ORDER BY Year) AS prev_amount
  FROM yearly_data
)
SELECT DISTINCT State
FROM growth
WHERE total_amount > prev_amount;

-- States with stagnation or decline
SELECT
  State,
  Year,
  total_amount,
  (total_amount - prev_amount) AS growth_value
FROM (
  SELECT
    State,
    Year,
    SUM(Transaction_amount) AS total_amount,
    LAG(SUM(Transaction_amount)) OVER (PARTITION BY State ORDER BY Year) AS prev_amount
  FROM aggregated_transaction
  GROUP BY State, Year
) t
WHERE total_amount <= prev_amount;

-- Categories that are growing
SELECT
  Transaction_type,
  Year,
  SUM(Transaction_amount) AS total_amount
FROM aggregated_transaction
GROUP BY Transaction_type, Year
ORDER BY Transaction_type, Year;

-- Categories that are losing usage
WITH type_year AS (
  SELECT
    Transaction_type,
    Year,
    SUM(Transaction_amount) AS total_amount
  FROM aggregated_transaction
  GROUP BY Transaction_type, Year
),
trend AS (
  SELECT
    Transaction_type,
    Year,
    total_amount,
    LAG(total_amount) OVER (PARTITION BY Transaction_type ORDER BY Year) AS prev_amount
  FROM type_year
)
SELECT *
FROM trend
WHERE total_amount < prev_amount;









