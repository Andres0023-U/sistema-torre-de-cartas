-- =========================================================
-- Semilla 04: Torneos de Prueba para S.T.C. (04_tournaments.sql)
--
-- Propósito:
--   Crear los 8 torneos de prueba generales del sistema, distribuidos equitativamente
--   entre los dos organizadores registrados (4 torneos por organizador).
--
-- Datos insertados:
--   - 8 torneos en tournaments.tournament en distintos estados ('finished', 'in_progress', 'pending')
--     y con distintas capacidades de participantes (4, 8, 16 y 32 jugadores).
--
--   Distribución de torneos:
--     Organizador 1 (organizador@demo.com):
--       1. Torneo Gran Desafío Inicial: status 'finished', num_players 32
--       2. Torneo Liga de Campeones: status 'in_progress', num_players 8
--       3. Torneo Gran Abierto Anual: status 'pending', num_players 16
--       4. Torneo de Aficionados: status 'pending', num_players 4
--
--     Organizador 2 (organizador2@demo.com):
--       1. Torneo Copa Relámpago: status 'finished', num_players 4
--       2. Torneo Desafío Estelar: status 'in_progress', num_players 4
--       3. Torneo Copa Primavera: status 'pending', num_players 8
--       4. Torneo de Maestros: status 'pending', num_players 32
--
-- Requisitos previos:
--   - Ejecutar previamente 00_roles.sql, 01_cards.sql, 02_users.sql y 03_decks.sql.
--
-- Orden de ejecución:
--   5º en la secuencia (00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06).
-- =========================================================

BEGIN;

INSERT INTO tournaments.tournament (
    name,
    date,
    format,
    num_players,
    status,
    organizer_id
)
SELECT
    t.name,
    t.date::DATE,
    t.format,
    t.num_players,
    t.status,
    u.user_id
FROM (
    VALUES
        ('Torneo Gran Desafío Inicial', '2025-01-15', 'Eliminación Directa', 32, 'finished', 'organizador@demo.com'),
        ('Torneo Copa Relámpago', '2025-01-20', 'Eliminación Directa', 4, 'finished', 'organizador2@demo.com'),
        ('Torneo Liga de Campeones', '2025-02-01', 'Eliminación Directa', 8, 'in_progress', 'organizador@demo.com'),
        ('Torneo Desafío Estelar', '2025-02-10', 'Eliminación Directa', 4, 'in_progress', 'organizador2@demo.com'),
        ('Torneo Gran Abierto Anual', '2025-03-01', 'Eliminación Directa', 16, 'pending', 'organizador@demo.com'),
        ('Torneo Copa Primavera', '2025-03-15', 'Eliminación Directa', 8, 'pending', 'organizador2@demo.com'),
        ('Torneo de Aficionados', '2025-03-20', 'Eliminación Directa', 4, 'pending', 'organizador@demo.com'),
        ('Torneo de Maestros', '2025-03-25', 'Eliminación Directa', 32, 'pending', 'organizador2@demo.com')
) AS t(name, date, format, num_players, status, organizer_email)
JOIN security."user" AS u
    ON u.email = t.organizer_email
WHERE NOT EXISTS (
    SELECT 1
    FROM tournaments.tournament AS existing
    WHERE existing.name = t.name
);

COMMIT;

-- Verificación de los torneos insertados
-- Esperado: 8 registros en tournaments.tournament (4 de organizador@demo.com y 4 de organizador2@demo.com)
SELECT
    t.tournament_id,
    t.name,
    t.date,
    t.format,
    t.num_players,
    t.status,
    u.email AS organizador
FROM tournaments.tournament AS t
JOIN security."user" AS u
    ON u.user_id = t.organizer_id
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
ORDER BY t.tournament_id;
