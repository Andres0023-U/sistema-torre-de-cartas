-- =========================================================
-- Semilla 03: Mazos de Demostración para Jugadores (03_decks.sql)
--
-- Propósito:
--   Asignar a cada uno de los 32 jugadores dos mazos reglamentarios de 20 cartas cada uno
--   ("Mazo Equilibrado" y "Mazo Defensivo") para permitirles inscribirse y competir en torneos.
--
-- Datos insertados:
--   - 64 mazos en players.deck (2 por jugador).
--   - 512 registros mazo-carta en players.deck_card (8 tipos de carta por mazo * 64 mazos,
--     sumando 20 cartas por mazo y respetando los límites max_quantity de cada carta).
--
-- Requisitos previos:
--   - Ejecutar previamente 00_roles.sql, 01_cards.sql y 02_users.sql.
--
-- Orden de ejecución:
--   4º en la secuencia (00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06).
-- =========================================================

BEGIN;

-- 1. Crear los dos mazos para cada jugador de demostración.
INSERT INTO players.deck (player_id, name)
SELECT
    p.player_id,
    d.deck_name
FROM generate_series(1, 32) AS n(player_number)
JOIN security."user" AS u
    ON u.email = 'jugador' || n.player_number || '@demo.com'
JOIN security.role AS r
    ON r.role_id = u.role_id
   AND r.name = 'player'
JOIN players.player AS p
    ON p.user_id = u.user_id
CROSS JOIN (
    VALUES
        ('Mazo Equilibrado'),
        ('Mazo Defensivo')
) AS d(deck_name)
WHERE NOT EXISTS (
    SELECT 1
    FROM players.deck AS existing
    WHERE existing.player_id = p.player_id
      AND existing.name = d.deck_name
);

-- 2. Composición del Mazo Equilibrado: 20 cartas.
-- 4 Ataque Básico, 3 Ataque Normal, 2 Ataque Fuerte,
-- 1 Ataque Devastador, 4 Defensa Básica, 3 Defensa Normal,
-- 2 Defensa Fuerte y 1 Defensa Implacable.
INSERT INTO players.deck_card (deck_id, card_id, quantity)
SELECT
    d.deck_id,
    c.card_id,
    composition.quantity
FROM generate_series(1, 32) AS n(player_number)
JOIN security."user" AS u
    ON u.email = 'jugador' || n.player_number || '@demo.com'
JOIN security.role AS r
    ON r.role_id = u.role_id
   AND r.name = 'player'
JOIN players.player AS p
    ON p.user_id = u.user_id
JOIN players.deck AS d
    ON d.player_id = p.player_id
   AND d.name = 'Mazo Equilibrado'
JOIN (
    VALUES
        ('Ataque Básico', 4),
        ('Ataque Normal', 3),
        ('Ataque Fuerte', 2),
        ('Ataque Devastador', 1),
        ('Defensa Básica', 4),
        ('Defensa Normal', 3),
        ('Defensa Fuerte', 2),
        ('Defensa Implacable', 1)
) AS composition(card_name, quantity)
    ON TRUE
JOIN cards.card AS c
    ON c.card_name = composition.card_name
ON CONFLICT (deck_id, card_id) DO NOTHING;

-- 3. Composición del Mazo Defensivo: 20 cartas.
-- 4 Defensa Básica, 3 Defensa Normal, 2 Defensa Fuerte,
-- 1 Defensa Implacable, 4 Curación Básica, 3 Curación Normal,
-- 2 Curación Fuerte y 1 Curación Vigorosa.
INSERT INTO players.deck_card (deck_id, card_id, quantity)
SELECT
    d.deck_id,
    c.card_id,
    composition.quantity
FROM generate_series(1, 32) AS n(player_number)
JOIN security."user" AS u
    ON u.email = 'jugador' || n.player_number || '@demo.com'
JOIN security.role AS r
    ON r.role_id = u.role_id
   AND r.name = 'player'
JOIN players.player AS p
    ON p.user_id = u.user_id
JOIN players.deck AS d
    ON d.player_id = p.player_id
   AND d.name = 'Mazo Defensivo'
JOIN (
    VALUES
        ('Defensa Básica', 4),
        ('Defensa Normal', 3),
        ('Defensa Fuerte', 2),
        ('Defensa Implacable', 1),
        ('Curación Básica', 4),
        ('Curación Normal', 3),
        ('Curación Fuerte', 2),
        ('Curación Vigorosa', 1)
) AS composition(card_name, quantity)
    ON TRUE
JOIN cards.card AS c
    ON c.card_name = composition.card_name
ON CONFLICT (deck_id, card_id) DO NOTHING;

COMMIT;

-- Verificación de los mazos y sus cartas
-- Esperado: 64 mazos y 512 registros en players.deck_card
-- Esperado: 20 cartas por mazo y 8 tipos de carta por mazo

SELECT
    u.email,
    d.name AS mazo,
    COALESCE(SUM(dc.quantity), 0) AS total_cartas,
    COUNT(dc.card_id) AS tipos_de_carta
FROM players.deck AS d
JOIN players.player AS p
    ON p.player_id = d.player_id
JOIN security."user" AS u
    ON u.user_id = p.user_id
LEFT JOIN players.deck_card AS dc
    ON dc.deck_id = d.deck_id
WHERE u.email LIKE 'jugador%@demo.com'
GROUP BY u.email, d.deck_id, d.name
ORDER BY u.email, d.name;
