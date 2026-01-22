use phonepe;
select * from map_user;

-- Total Registered Users by State
SELECT 
    State,
    SUM(Registered_users) AS total_registered_users
FROM map_user
GROUP BY State
ORDER BY total_registered_users DESC;

-- Total App Opens by State
SELECT 
    State,
    SUM(App_opens) AS total_app_opens
FROM map_user
GROUP BY State
ORDER BY total_app_opens DESC;

-- Engagement Ratio (Aap open per user)
SELECT 
    State,
    SUM(App_opens) * 1.0 / SUM(Registered_users) AS engagement_ratio
FROM map_user
GROUP BY State
ORDER BY engagement_ratio DESC;

-- District-wise Engagement Analysis
SELECT 
    State,
    District,
    SUM(Registered_users) AS users,
    SUM(App_opens) AS app_opens
FROM map_user
GROUP BY State, District
ORDER BY app_opens DESC;

-- Year-wise User Growth
SELECT 
    Year,
    SUM(Registered_users) AS total_users
FROM map_user
GROUP BY Year
ORDER BY Year;

-- Quarter-wise Engagement Trend
SELECT 
    Year,
    Quarter,
    SUM(App_opens) AS total_app_opens
FROM map_user
GROUP BY Year, Quarter
ORDER BY Year, Quarter;






