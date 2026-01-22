use phonepe;
select * from aggregated_insurance;

-- insurance transactions per state
SELECT
    State,
    SUM(Transaction_count) AS total_insurance_transactions
FROM aggregated_insurance
WHERE Transaction_type = 'Insurance'
GROUP BY State
ORDER BY total_insurance_transactions DESC;

-- insurance amount per state
SELECT
    State,
    SUM(Transaction_amount) AS total_insurance_amount
FROM aggregated_insurance
WHERE Transaction_type = 'Insurance'
GROUP BY State
ORDER BY total_insurance_amount DESC;

-- Year-wise Insurance Growth
SELECT
    Year,
    SUM(Transaction_count) AS insurance_transactions
FROM aggregated_insurance
WHERE Transaction_type = 'Insurance'
GROUP BY Year
ORDER BY Year;

-- State + Year Growth Analysis
SELECT
    State,
    Year,
    SUM(Transaction_count) AS insurance_transactions
FROM aggregated_insurance
WHERE Transaction_type = 'Insurance'
GROUP BY State, Year
ORDER BY State, Year;

-- Quarterly Insurance Trend
SELECT
    Year,
    Quarter,
    SUM(Transaction_count) AS insurance_transactions
FROM aggregated_insurance
WHERE Transaction_type = 'Insurance'
GROUP BY Year, Quarter
ORDER BY Year, Quarter;

-- States with LOW insurance penetration
SELECT
    State,
    SUM(Transaction_count) AS total_insurance_transactions
FROM aggregated_insurance
WHERE Transaction_type = 'Insurance'
GROUP BY State
ORDER BY total_insurance_transactions ASC;





