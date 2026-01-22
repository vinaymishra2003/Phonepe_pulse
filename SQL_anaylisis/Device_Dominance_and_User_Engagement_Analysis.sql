use phonepe;
select * from aggregated_user;

-- device brands are most used overall
SELECT 
    Brand,
    SUM(User_count) AS total_users
FROM aggregated_user
GROUP BY Brand
ORDER BY total_users DESC;

-- most used brands in each state
SELECT 
    State,
    Brand,
    SUM(User_count) AS total_users
FROM aggregated_user
GROUP BY State, Brand
ORDER BY State, total_users DESC;

-- brand usage over time (year & quarter)
SELECT 
    Year,
    Quarter,
    Brand,
    SUM(User_count) AS total_users
FROM aggregated_user
GROUP BY Year, Quarter, Brand
ORDER BY Year, Quarter, total_users DESC;

-- underutilized brands
SELECT 
    Brand,
    SUM(User_count) AS total_users,
    AVG(Percentage) AS avg_percentage
FROM aggregated_user
GROUP BY Brand
HAVING SUM(User_count) > 100000
   AND AVG(Percentage) < 5
ORDER BY total_users DESC;

-- Top brand per state
SELECT State, Brand, total_users
FROM (
    SELECT 
        State,
        Brand,
        SUM(User_count) AS total_users,
        RANK() OVER (PARTITION BY State ORDER BY SUM(User_count) DESC) AS rnk
    FROM aggregated_user
    GROUP BY State, Brand
) t
WHERE rnk = 1;




