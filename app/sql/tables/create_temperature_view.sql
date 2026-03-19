CREATE VIEW temperature_data AS

-- DMI
SELECT
    value AS temperature,
    observed_at,
    pulled_at,
    'DMI' AS source
FROM table1
WHERE type = 'temperature'

UNION ALL

-- DS18B20 sensor
SELECT
    temperature,
    observed_at,
    pulled_at,
    'DS18B20' AS source
FROM table2

UNION ALL

-- BME280 sensor
SELECT
    temperature,
    observed_at,
    pulled_at,
    'BME280' AS source
FROM table3;