-- Verificación de cantidades de registros esperadas después de ejecutar las seeds.
-- Esperado:
-- security.role:                       4 registros
-- cards.card:                         18 registros
-- security.user:                      36 registros
-- players.player:                     32 registros
-- players.deck:                       64 registros
-- tournaments.tournament:              8 registros
-- tournaments.tournament_registration: 100 registros
-- tournaments.round:                  10 registros
-- matches.match:                      42 registros

SELECT 'security.role' AS tabla, COUNT(*) AS registros
FROM security.role

UNION ALL
SELECT 'cards.card', COUNT(*)
FROM cards.card

UNION ALL
SELECT 'security.user', COUNT(*)
FROM security."user"

UNION ALL
SELECT 'players.player', COUNT(*)
FROM players.player

UNION ALL
SELECT 'players.deck', COUNT(*)
FROM players.deck

UNION ALL
SELECT 'tournaments.tournament', COUNT(*)
FROM tournaments.tournament

UNION ALL
SELECT 'tournaments.tournament_registration', COUNT(*)
FROM tournaments.tournament_registration

UNION ALL
SELECT 'tournaments.round', COUNT(*)
FROM tournaments.round

UNION ALL
SELECT 'matches.match', COUNT(*)
FROM matches.match;