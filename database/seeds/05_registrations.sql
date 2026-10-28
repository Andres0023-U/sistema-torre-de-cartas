-- =========================================================
-- Semilla 05: Inscripciones de Jugadores a Torneos (05_registrations.sql)
--
-- Propósito:
--   Registrar a los jugadores de prueba en los 8 torneos del sistema creados en
--   04_tournaments.sql, simulando distintos niveles de ocupación y preparación.
--
-- Datos insertados en tournaments.tournament_registration:
--   1. Torneo Gran Desafío Inicial (finished, cap 32): 32 inscritos (Jugador 1 a 32).
--   2. Torneo Copa Relámpago (finished, cap 4): 4 inscritos (Jugador 1 a 4).
--   3. Torneo Liga de Campeones (in_progress, cap 8): 8 inscritos (Jugador 5 a 12).
--   4. Torneo Desafío Estelar (in_progress, cap 4): 4 inscritos (Jugador 13 a 16).
--   5. Torneo Gran Abierto Anual (pending, cap 16): 16 inscritos (Jugador 17 a 32). Torneo lleno listo para iniciar.
--   6. Torneo Copa Primavera (pending, cap 8): 4 inscritos (Jugador 1 a 4). Parcialmente lleno (4/8).
--   7. Torneo de Aficionados (pending, cap 4): 0 inscritos (0/4). Abierto para pruebas de inscripción desde la web.
--   8. Torneo de Maestros (pending, cap 32): 32 inscritos (Jugador 1 a 32). Torneo de 32 lleno listo para iniciar.
--
-- Requisitos previos:
--   - Ejecutar previamente 00_roles.sql, 01_cards.sql, 02_users.sql, 03_decks.sql y 04_tournaments.sql.
--
-- Orden de ejecución:
--   6º en la secuencia (00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06).
-- =========================================================

BEGIN;

INSERT INTO tournaments.tournament_registration (
    tournament_id,
    player_id
)
SELECT DISTINCT
    t.tournament_id,
    p.player_id
FROM (
    -- Torneo 1: 32 jugadores (Jugador 1 a 32)
    SELECT 'Torneo Gran Desafío Inicial' AS tournament_name, 'jugador' || n || '@demo.com' AS player_email
    FROM generate_series(1, 32) AS n
    UNION ALL
    -- Torneo 2: 4 jugadores (Jugador 1 a 4)
    SELECT 'Torneo Copa Relámpago', 'jugador' || n || '@demo.com'
    FROM generate_series(1, 4) AS n
    UNION ALL
    -- Torneo 3: 8 jugadores (Jugador 5 a 12)
    SELECT 'Torneo Liga de Campeones', 'jugador' || n || '@demo.com'
    FROM generate_series(5, 12) AS n
    UNION ALL
    -- Torneo 4: 4 jugadores (Jugador 13 a 16)
    SELECT 'Torneo Desafío Estelar', 'jugador' || n || '@demo.com'
    FROM generate_series(13, 16) AS n
    UNION ALL
    -- Torneo 5: 16 jugadores (Jugador 17 a 32)
    SELECT 'Torneo Gran Abierto Anual', 'jugador' || n || '@demo.com'
    FROM generate_series(17, 32) AS n
    UNION ALL
    -- Torneo 6: 4 jugadores (Jugador 1 a 4)
    SELECT 'Torneo Copa Primavera', 'jugador' || n || '@demo.com'
    FROM generate_series(1, 4) AS n
    -- Torneo 7: 0 jugadores (sin filas)
    UNION ALL
    -- Torneo 8: 32 jugadores (Jugador 1 a 32)
    SELECT 'Torneo de Maestros', 'jugador' || n || '@demo.com'
    FROM generate_series(1, 32) AS n
) AS data
JOIN tournaments.tournament AS t
    ON t.name = data.tournament_name
JOIN security."user" AS u
    ON u.email = data.player_email
JOIN players.player AS p
    ON p.user_id = u.user_id
ON CONFLICT (tournament_id, player_id) DO NOTHING;

COMMIT;

-- Verificación de inscripciones por torneo
-- Esperado: 100 registros en total en tournaments.tournament_registration
-- (T1: 32, T2: 4, T3: 8, T4: 4, T5: 16, T6: 4, T7: 0, T8: 32)
SELECT
    t.name AS torneo,
    t.status AS estado_torneo,
    t.num_players AS capacidad_maxima,
    COUNT(tr.tournament_registration_id) AS total_inscritos
FROM tournaments.tournament AS t
LEFT JOIN tournaments.tournament_registration AS tr
    ON tr.tournament_id = t.tournament_id
WHERE t.name IN (
    'Torneo Gran Desafío Inicial',
    'Torneo Copa Relámpago',
    'Torneo Liga de Campeones',
    'Torneo Desafío Estelar',
    'Torneo Gran Abierto Anual',
    'Torneo Copa Primavera',
    'Torneo de Aficionados',
    'Torneo de Maestros'
)
GROUP BY t.tournament_id, t.name, t.status, t.num_players
ORDER BY t.tournament_id;
