CREATE VIEW pressure_data AS

-- DMI
SELECT
    value AS pressure,
    observed_at,
    pulled_at,
    'DMI' AS source
FROM table1
WHERE type = 'pressure'

UNION ALL

-- BME280 sensor
SELECT
    pressure,
    observed_at,
    pulled_at,
    'BME280' AS source
FROM table2;