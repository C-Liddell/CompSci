SELECT Country, COUNT(*) AS "noVolcanoes"
FROM volcanoes
WHERE Name LIKE "P%"
GROUP BY Country;