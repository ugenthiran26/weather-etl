CREATE TABLE IF NOT EXISTS weather_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recorded_at DATETIME NOT NULL,
    reading_date DATE NOT NULL,
    hour_of_day TINYINT NOT NULL,
    temperature_c DECIMAL(4,1),
    humidity_pct TINYINT,
    rain_mm DECIMAL(5,2),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_recorded_at (recorded_at)
);