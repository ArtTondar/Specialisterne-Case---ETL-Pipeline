CREATE VIEW humidity_data AS

-- DMI
SELECT
    value AS humidity,
    observed_at,
    pulled_at,
    'DMI' AS source
FROM table1
WHERE type = 'humidity'

UNION ALL

-- BME280 sensor
SELECT
    humidity,
    observed_at,
    pulled_at,
    'BME280' AS source
FROM table2;