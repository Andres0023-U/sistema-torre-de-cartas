-- =========================================================
-- Semilla 06: Rondas, Selecciones de Mazo, Partidas y Resultados (06_matches.sql)
--
-- Propósito:
--   Poblar el historial de competición (rondas, selección de mazos por ronda, enfrentamientos
--   y resultados) para los torneos finalizados y en curso del sistema S.T.C.
--
-- Datos insertados:
--   - Torneo 1 (Gran Desafío Inicial, finished, 32 jugadores):
--     5 rondas (Ronda 1 a Final), 31 partidas con resultados completos.
--     Proporciona historial completo para probar el cuadro de 32 participantes y el ranking global.
--   - Torneo 2 (Copa Relámpago, finished, 4 jugadores):
--     2 rondas (Ronda 1 y Final), 3 partidas con resultados completos.
--   - Torneo 3 (Liga de Campeones, in_progress, 8 jugadores):
--     Ronda 1 (finalizada, 4 partidas con resultado) y Ronda 2/Semifinal en curso (2 partidas: 1 con resultado y 1 pendiente).
--   - Torneo 4 (Desafío Estelar, in_progress, 4 jugadores):
--     Ronda 1 en curso (2 partidas creadas sin resultados aún).
--   - Torneos 5, 6, 7 y 8 (pending):
--     Sin rondas ni partidas creadas.
--
-- Requisitos previos:
--   - Ejecutar previamente 00_roles.sql, 01_cards.sql, 02_users.sql, 03_decks.sql,
--     04_tournaments.sql y 05_registrations.sql.
--
-- Orden de ejecución:
--   7º en la secuencia (00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06).
-- =========================================================

DO $seed_matches$
DECLARE
    v_t1_id INT; v_t2_id INT; v_t3_id INT; v_t4_id INT;
    v_r_id INT;
    v_m_id INT;
    v_d1_id INT; v_d2_id INT;
BEGIN
    -- Obtener IDs de torneos
    SELECT tournament_id INTO v_t1_id FROM tournaments.tournament WHERE name = 'Torneo Gran Desafío Inicial';
    SELECT tournament_id INTO v_t2_id FROM tournaments.tournament WHERE name = 'Torneo Copa Relámpago';
    SELECT tournament_id INTO v_t3_id FROM tournaments.tournament WHERE name = 'Torneo Liga de Campeones';
    SELECT tournament_id INTO v_t4_id FROM tournaments.tournament WHERE name = 'Torneo Desafío Estelar';

    -- =========================================================================
    -- TORNEO 1: 'Torneo Gran Desafío Inicial' (finished, 32 jugadores, 5 rondas)
    -- =========================================================================
    IF v_t1_id IS NOT NULL THEN

        -- --- RONDA 1 (32 jugadores -> 16 partidas) ---
        INSERT INTO tournaments.round (tournament_id, number, name, status)
        VALUES (v_t1_id, 1, 'Ronda 1', 'finished')
        RETURNING round_id INTO v_r_id;

        -- Selecciones de mazo Ronda 1 (Mazo Equilibrado para los 32 jugadores)
        INSERT INTO tournaments.round_deck_selection (round_id, player_id, deck_id)
        SELECT v_r_id, p.player_id, d.deck_id
        FROM generate_series(1, 32) AS n(i)
        JOIN security."user" u ON u.email = 'jugador' || n.i || '@demo.com'
        JOIN players.player p ON p.user_id = u.user_id
        JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado';

        -- Partidas y resultados Ronda 1: Jugador i (impar) gana contra Jugador i+1 (par)
        FOR i IN 1..16 LOOP
            SELECT d.deck_id INTO v_d1_id
            FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado'
            WHERE u.email = 'jugador' || (2 * i - 1) || '@demo.com';

            SELECT d.deck_id INTO v_d2_id
            FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado'
            WHERE u.email = 'jugador' || (2 * i) || '@demo.com';

            INSERT INTO matches.match (round_id, deck1_id, deck2_id)
            VALUES (v_r_id, v_d1_id, v_d2_id)
            RETURNING match_id INTO v_m_id;

            INSERT INTO matches.result (match_id, winner_id, end_phase, player1_final_life, player2_final_life, player1_points, player2_points, date)
            VALUES (v_m_id, v_d1_id, 'normal', 15, 0, 3, 0, '2025-01-15 10:00:00+00');
        END LOOP;

        -- --- RONDA 2 (16 ganadores -> 8 partidas) ---
        INSERT INTO tournaments.round (tournament_id, number, name, status)
        VALUES (v_t1_id, 2, 'Ronda 2', 'finished')
        RETURNING round_id INTO v_r_id;

        -- Jugadores que avanzan: 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31
        INSERT INTO tournaments.round_deck_selection (round_id, player_id, deck_id)
        SELECT v_r_id, p.player_id, d.deck_id
        FROM generate_series(1, 31, 2) AS n(i)
        JOIN security."user" u ON u.email = 'jugador' || n.i || '@demo.com'
        JOIN players.player p ON p.user_id = u.user_id
        JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado';

        -- Partidas y resultados Ronda 2: Jugadores (4*k - 3) ganan
        FOR k IN 1..8 LOOP
            SELECT d.deck_id INTO v_d1_id
            FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado'
            WHERE u.email = 'jugador' || (4 * k - 3) || '@demo.com';

            SELECT d.deck_id INTO v_d2_id
            FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado'
            WHERE u.email = 'jugador' || (4 * k - 1) || '@demo.com';

            INSERT INTO matches.match (round_id, deck1_id, deck2_id)
            VALUES (v_r_id, v_d1_id, v_d2_id)
            RETURNING match_id INTO v_m_id;

            INSERT INTO matches.result (match_id, winner_id, end_phase, player1_final_life, player2_final_life, player1_points, player2_points, date)
            VALUES (v_m_id, v_d1_id, 'normal', 12, 0, 3, 0, '2025-01-15 12:00:00+00');
        END LOOP;

        -- --- RONDA 3 (8 ganadores -> 4 partidas) ---
        INSERT INTO tournaments.round (tournament_id, number, name, status)
        VALUES (v_t1_id, 3, 'Ronda 3', 'finished')
        RETURNING round_id INTO v_r_id;

        -- Jugadores que avanzan: 1, 5, 9, 13, 17, 21, 25, 29
        INSERT INTO tournaments.round_deck_selection (round_id, player_id, deck_id)
        SELECT v_r_id, p.player_id, d.deck_id
        FROM generate_series(1, 29, 4) AS n(i)
        JOIN security."user" u ON u.email = 'jugador' || n.i || '@demo.com'
        JOIN players.player p ON p.user_id = u.user_id
        JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado';

        FOR k IN 1..4 LOOP
            SELECT d.deck_id INTO v_d1_id
            FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado'
            WHERE u.email = 'jugador' || (8 * k - 7) || '@demo.com';

            SELECT d.deck_id INTO v_d2_id
            FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado'
            WHERE u.email = 'jugador' || (8 * k - 3) || '@demo.com';

            INSERT INTO matches.match (round_id, deck1_id, deck2_id)
            VALUES (v_r_id, v_d1_id, v_d2_id)
            RETURNING match_id INTO v_m_id;

            INSERT INTO matches.result (match_id, winner_id, end_phase, player1_final_life, player2_final_life, player1_points, player2_points, date)
            VALUES (v_m_id, v_d1_id, 'normal', 10, 0, 3, 0, '2025-01-15 14:00:00+00');
        END LOOP;

        -- --- RONDA 4 (4 ganadores / Semifinal -> 2 partidas) ---
        INSERT INTO tournaments.round (tournament_id, number, name, status)
        VALUES (v_t1_id, 4, 'Semifinal', 'finished')
        RETURNING round_id INTO v_r_id;

        -- Jugadores que avanzan: 1, 9, 17, 25
        INSERT INTO tournaments.round_deck_selection (round_id, player_id, deck_id)
        SELECT v_r_id, p.player_id, d.deck_id
        FROM (VALUES (1), (9), (17), (25)) AS n(i)
        JOIN security."user" u ON u.email = 'jugador' || n.i || '@demo.com'
        JOIN players.player p ON p.user_id = u.user_id
        JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado';

        -- Semifinal 1: Jugador 1 vs Jugador 9 -> Gana Jugador 1
        SELECT d.deck_id INTO v_d1_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador1@demo.com';
        SELECT d.deck_id INTO v_d2_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador9@demo.com';
        INSERT INTO matches.match (round_id, deck1_id, deck2_id) VALUES (v_r_id, v_d1_id, v_d2_id) RETURNING match_id INTO v_m_id;
        INSERT INTO matches.result (match_id, winner_id, end_phase, player1_final_life, player2_final_life, player1_points, player2_points, date)
        VALUES (v_m_id, v_d1_id, 'normal', 8, 0, 3, 0, '2025-01-15 16:00:00+00');

        -- Semifinal 2: Jugador 17 vs Jugador 25 -> Gana Jugador 17
        SELECT d.deck_id INTO v_d1_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador17@demo.com';
        SELECT d.deck_id INTO v_d2_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador25@demo.com';
        INSERT INTO matches.match (round_id, deck1_id, deck2_id) VALUES (v_r_id, v_d1_id, v_d2_id) RETURNING match_id INTO v_m_id;
        INSERT INTO matches.result (match_id, winner_id, end_phase, player1_final_life, player2_final_life, player1_points, player2_points, date)
        VALUES (v_m_id, v_d1_id, 'normal', 6, 0, 3, 0, '2025-01-15 16:00:00+00');

        -- --- RONDA 5 (2 ganadores / Final -> 1 partida) ---
        INSERT INTO tournaments.round (tournament_id, number, name, status)
        VALUES (v_t1_id, 5, 'Final', 'finished')
        RETURNING round_id INTO v_r_id;

        -- Jugadores que avanzan a la final: 1 y 17
        INSERT INTO tournaments.round_deck_selection (round_id, player_id, deck_id)
        SELECT v_r_id, p.player_id, d.deck_id
        FROM (VALUES (1), (17)) AS n(i)
        JOIN security."user" u ON u.email = 'jugador' || n.i || '@demo.com'
        JOIN players.player p ON p.user_id = u.user_id
        JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado';

        -- Final: Jugador 1 vs Jugador 17 -> Gana Jugador 1 (¡Campeón del Torneo 1!)
        SELECT d.deck_id INTO v_d1_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador1@demo.com';
        SELECT d.deck_id INTO v_d2_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador17@demo.com';
        INSERT INTO matches.match (round_id, deck1_id, deck2_id) VALUES (v_r_id, v_d1_id, v_d2_id) RETURNING match_id INTO v_m_id;
        INSERT INTO matches.result (match_id, winner_id, end_phase, player1_final_life, player2_final_life, player1_points, player2_points, date)
        VALUES (v_m_id, v_d1_id, 'normal', 5, 0, 3, 0, '2025-01-15 18:00:00+00');

    END IF;

    -- =========================================================================
    -- TORNEO 2: 'Torneo Copa Relámpago' (finished, 4 jugadores, 2 rondas)
    -- =========================================================================
    IF v_t2_id IS NOT NULL THEN

        -- --- RONDA 1 (4 jugadores -> 2 partidas) ---
        INSERT INTO tournaments.round (tournament_id, number, name, status)
        VALUES (v_t2_id, 1, 'Ronda 1', 'finished')
        RETURNING round_id INTO v_r_id;

        -- Selecciones de mazo Ronda 1 (Mazo Defensivo para Jugadores 1 a 4)
        INSERT INTO tournaments.round_deck_selection (round_id, player_id, deck_id)
        SELECT v_r_id, p.player_id, d.deck_id
        FROM generate_series(1, 4) AS n(i)
        JOIN security."user" u ON u.email = 'jugador' || n.i || '@demo.com'
        JOIN players.player p ON p.user_id = u.user_id
        JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo';

        -- Match 1: Jugador 1 vs Jugador 2 -> Gana Jugador 1
        SELECT d.deck_id INTO v_d1_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo' WHERE u.email = 'jugador1@demo.com';
        SELECT d.deck_id INTO v_d2_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo' WHERE u.email = 'jugador2@demo.com';
        INSERT INTO matches.match (round_id, deck1_id, deck2_id) VALUES (v_r_id, v_d1_id, v_d2_id) RETURNING match_id INTO v_m_id;
        INSERT INTO matches.result (match_id, winner_id, end_phase, player1_final_life, player2_final_life, player1_points, player2_points, date)
        VALUES (v_m_id, v_d1_id, 'normal', 10, 0, 3, 0, '2025-01-20 10:00:00+00');

        -- Match 2: Jugador 3 vs Jugador 4 -> Gana Jugador 3
        SELECT d.deck_id INTO v_d1_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo' WHERE u.email = 'jugador3@demo.com';
        SELECT d.deck_id INTO v_d2_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo' WHERE u.email = 'jugador4@demo.com';
        INSERT INTO matches.match (round_id, deck1_id, deck2_id) VALUES (v_r_id, v_d1_id, v_d2_id) RETURNING match_id INTO v_m_id;
        INSERT INTO matches.result (match_id, winner_id, end_phase, player1_final_life, player2_final_life, player1_points, player2_points, date)
        VALUES (v_m_id, v_d1_id, 'normal', 8, 0, 3, 0, '2025-01-20 10:00:00+00');

        -- --- RONDA 2 (Final -> 1 partida) ---
        INSERT INTO tournaments.round (tournament_id, number, name, status)
        VALUES (v_t2_id, 2, 'Final', 'finished')
        RETURNING round_id INTO v_r_id;

        -- Jugadores que avanzan: 1 y 3
        INSERT INTO tournaments.round_deck_selection (round_id, player_id, deck_id)
        SELECT v_r_id, p.player_id, d.deck_id
        FROM (VALUES (1), (3)) AS n(i)
        JOIN security."user" u ON u.email = 'jugador' || n.i || '@demo.com'
        JOIN players.player p ON p.user_id = u.user_id
        JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo';

        -- Final: Jugador 1 vs Jugador 3 -> Gana Jugador 3 (¡Campeón del Torneo 2!)
        SELECT d.deck_id INTO v_d1_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo' WHERE u.email = 'jugador1@demo.com';
        SELECT d.deck_id INTO v_d2_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo' WHERE u.email = 'jugador3@demo.com';
        INSERT INTO matches.match (round_id, deck1_id, deck2_id) VALUES (v_r_id, v_d1_id, v_d2_id) RETURNING match_id INTO v_m_id;
        INSERT INTO matches.result (match_id, winner_id, end_phase, player1_final_life, player2_final_life, player1_points, player2_points, date)
        VALUES (v_m_id, v_d2_id, 'overtime', 0, 4, 0, 2, '2025-01-20 12:00:00+00');

    END IF;

    -- =========================================================================
    -- TORNEO 3: 'Torneo Liga de Campeones' (in_progress, 8 jugadores)
    -- =========================================================================
    IF v_t3_id IS NOT NULL THEN

        -- --- RONDA 1 (8 jugadores -> 4 partidas completas) ---
        INSERT INTO tournaments.round (tournament_id, number, name, status)
        VALUES (v_t3_id, 1, 'Ronda 1', 'finished')
        RETURNING round_id INTO v_r_id;

        -- Selecciones de mazo Ronda 1 (Mazo Equilibrado para Jugadores 5 a 12)
        INSERT INTO tournaments.round_deck_selection (round_id, player_id, deck_id)
        SELECT v_r_id, p.player_id, d.deck_id
        FROM generate_series(5, 12) AS n(i)
        JOIN security."user" u ON u.email = 'jugador' || n.i || '@demo.com'
        JOIN players.player p ON p.user_id = u.user_id
        JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado';

        -- Partidas R1: J5 vs J6 (gana J5), J7 vs J8 (gana J7), J9 vs J10 (gana J9), J11 vs J12 (gana J11)
        FOR k IN 1..4 LOOP
            SELECT d.deck_id INTO v_d1_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador' || (2 * k + 3) || '@demo.com';
            SELECT d.deck_id INTO v_d2_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador' || (2 * k + 4) || '@demo.com';

            INSERT INTO matches.match (round_id, deck1_id, deck2_id) VALUES (v_r_id, v_d1_id, v_d2_id) RETURNING match_id INTO v_m_id;
            INSERT INTO matches.result (match_id, winner_id, end_phase, player1_final_life, player2_final_life, player1_points, player2_points, date)
            VALUES (v_m_id, v_d1_id, 'normal', 10, 0, 3, 0, '2025-02-01 10:00:00+00');
        END LOOP;

        -- --- RONDA 2 / Semifinal (4 ganadores: J5, J7, J9, J11 -> En Curso) ---
        INSERT INTO tournaments.round (tournament_id, number, name, status)
        VALUES (v_t3_id, 2, 'Semifinal', 'in_progress')
        RETURNING round_id INTO v_r_id;

        -- Selecciones de mazo Ronda 2
        INSERT INTO tournaments.round_deck_selection (round_id, player_id, deck_id)
        SELECT v_r_id, p.player_id, d.deck_id
        FROM (VALUES (5), (7), (9), (11)) AS n(i)
        JOIN security."user" u ON u.email = 'jugador' || n.i || '@demo.com'
        JOIN players.player p ON p.user_id = u.user_id
        JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado';

        -- Match 1: J5 vs J7 -> TIENE RESULTADO (Gana J5)
        SELECT d.deck_id INTO v_d1_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador5@demo.com';
        SELECT d.deck_id INTO v_d2_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador7@demo.com';
        INSERT INTO matches.match (round_id, deck1_id, deck2_id) VALUES (v_r_id, v_d1_id, v_d2_id) RETURNING match_id INTO v_m_id;
        INSERT INTO matches.result (match_id, winner_id, end_phase, player1_final_life, player2_final_life, player1_points, player2_points, date)
        VALUES (v_m_id, v_d1_id, 'normal', 7, 0, 3, 0, '2025-02-01 12:00:00+00');

        -- Match 2: J9 vs J11 -> CREADO SIN RESULTADO (Pendiente de jugar/cargar en UI)
        SELECT d.deck_id INTO v_d1_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador9@demo.com';
        SELECT d.deck_id INTO v_d2_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Equilibrado' WHERE u.email = 'jugador11@demo.com';
        INSERT INTO matches.match (round_id, deck1_id, deck2_id) VALUES (v_r_id, v_d1_id, v_d2_id);

    END IF;

    -- =========================================================================
    -- TORNEO 4: 'Torneo Desafío Estelar' (in_progress, 4 jugadores)
    -- =========================================================================
    IF v_t4_id IS NOT NULL THEN

        -- --- RONDA 1 (4 jugadores -> En Curso, sin resultados cargados aún) ---
        INSERT INTO tournaments.round (tournament_id, number, name, status)
        VALUES (v_t4_id, 1, 'Ronda 1', 'in_progress')
        RETURNING round_id INTO v_r_id;

        -- Selecciones de mazo Ronda 1 (Mazo Defensivo para Jugadores 13 a 16)
        INSERT INTO tournaments.round_deck_selection (round_id, player_id, deck_id)
        SELECT v_r_id, p.player_id, d.deck_id
        FROM generate_series(13, 16) AS n(i)
        JOIN security."user" u ON u.email = 'jugador' || n.i || '@demo.com'
        JOIN players.player p ON p.user_id = u.user_id
        JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo';

        -- Match 1: J13 vs J14 (Sin resultado)
        SELECT d.deck_id INTO v_d1_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo' WHERE u.email = 'jugador13@demo.com';
        SELECT d.deck_id INTO v_d2_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo' WHERE u.email = 'jugador14@demo.com';
        INSERT INTO matches.match (round_id, deck1_id, deck2_id) VALUES (v_r_id, v_d1_id, v_d2_id);

        -- Match 2: J15 vs J16 (Sin resultado)
        SELECT d.deck_id INTO v_d1_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo' WHERE u.email = 'jugador15@demo.com';
        SELECT d.deck_id INTO v_d2_id FROM security."user" u JOIN players.player p ON p.user_id = u.user_id JOIN players.deck d ON d.player_id = p.player_id AND d.name = 'Mazo Defensivo' WHERE u.email = 'jugador16@demo.com';
        INSERT INTO matches.match (round_id, deck1_id, deck2_id) VALUES (v_r_id, v_d1_id, v_d2_id);

    END IF;

END $seed_matches$;

-- Verificación de rondas, selecciones de mazo, partidas y resultados insertados
-- Esperado: 10 registros en tournaments.round (T1: 5, T2: 2, T3: 2, T4: 1)
-- Esperado: 84 registros en tournaments.round_deck_selection (T1: 62, T2: 6, T3: 12, T4: 4)
-- Esperado: 42 registros en matches.match (T1: 31, T2: 3, T3: 6, T4: 2)
-- Esperado: 39 registros en matches.result (T1: 31, T2: 3, T3: 5, T4: 0)
SELECT
    t.name AS torneo,
    COUNT(DISTINCT r.round_id) AS total_rondas,
    COUNT(DISTINCT rds.round_deck_selection_id) AS total_selecciones_mazo,
    COUNT(DISTINCT m.match_id) AS total_partidas,
    COUNT(DISTINCT res.result_id) AS total_resultados
FROM tournaments.tournament t
LEFT JOIN tournaments.round r ON r.tournament_id = t.tournament_id
LEFT JOIN tournaments.round_deck_selection rds ON rds.round_id = r.round_id
LEFT JOIN matches.match m ON m.round_id = r.round_id
LEFT JOIN matches.result res ON res.match_id = m.match_id
WHERE t.name IN (
    'Torneo Gran Desafío Inicial',
    'Torneo Copa Relámpago',
    'Torneo Liga de Campeones',
    'Torneo Desafío Estelar'
)
GROUP BY t.tournament_id, t.name
ORDER BY t.tournament_id;
