use phonepe;
select * from map_transaction;

-- Total Transactions by State
SELECT 
    State,
    SUM(Transaction_count) AS total_transactions,
    SUM(Transaction_amount) AS total_amount
FROM map_transaction
GROUP BY State
ORDER BY total_amount DESC;

-- states which are growing over time
SELECT 
    State,
    Year,
    SUM(Transaction_amount) AS yearly_amount
FROM map_transaction
GROUP BY State, Year
ORDER BY State, Year;

-- Quarter-wise recent performance
SELECT 
    State,
    Year,
    Quarter,
    SUM(Transaction_amount) AS quarterly_amount
FROM map_transaction
GROUP BY State, Year, Quarter
ORDER BY State, Year, Quarter;

-- States with Low Transactions
SELECT 
    State,
    SUM(Transaction_amount) AS total_amount
FROM map_transaction
GROUP BY State
ORDER BY total_amount ASC;






