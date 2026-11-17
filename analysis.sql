-- 1. Daily summary: average, hottest, coldest temperature and total rain
SELECT reading_date,
       ROUND(AVG(temperature_c), 1) AS avg_temp,
       MAX(temperature_c) AS max_temp,
       MIN(temperature_c) AS min_temp,
       ROUND(SUM(rain_mm), 1) AS total_rain_mm
FROM weather_readings
GROUP BY reading_date
ORDER BY reading_date;

-- 2. The three hottest hours of the day, on average
SELECT hour_of_day,
       ROUND(AVG(temperature_c), 1) AS avg_temp
FROM weather_readings
GROUP BY hour_of_day
ORDER BY avg_temp DESC
LIMIT 3;

-- 3. Day-over-day temperature change
WITH daily AS (
    SELECT reading_date, AVG(temperature_c) AS avg_temp
    FROM weather_readings
    GROUP BY reading_date
)
SELECT reading_date,
       ROUND(avg_temp, 1) AS avg_temp,
       ROUND(avg_temp - LAG(avg_temp) OVER (ORDER BY reading_date), 1) AS change_from_prev_day
FROM daily;