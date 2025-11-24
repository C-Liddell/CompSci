SELECT Country, COUNT(*) AS "noVolcanoes"
FROM volcanoes
GROUP BY Country
HAVING "noVolcanoes" > 40;