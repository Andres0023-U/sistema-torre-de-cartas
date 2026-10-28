-- =========================================================
-- Semilla 02: Usuarios y Perfiles de Jugador (02_users.sql)
--
-- Propósito:
--   Crear los usuarios de prueba del sistema S.T.C. con sus respectivos roles y
--   perfiles de jugador.
--
-- Datos insertados:
--   - 1 Administrador (admin@demo.com).
--   - 2 Organizadores (organizador@demo.com, organizador2@demo.com).
--   - 1 Usuario pendiente de aprobación (pendiente@demo.com).
--   - 32 Jugadores (jugador1@demo.com a jugador32@demo.com) con sus correspondientes
--     perfiles en la tabla players.player.
--
-- Requisitos previos:
--   - Ejecutar previamente 00_roles.sql.
--   - Reemplazar el marcador '__PASSWORD_HASH__' por un hash válido generado mediante
--     backend/app/core/security.py (hash_password('Clave123')).
--
-- Orden de ejecución:
--   3º en la secuencia (00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06).
-- =========================================================

DO $seed$
DECLARE
    v_hash TEXT := '$2b$12$0tLzT/PZWx9YAYYSTpQamuhFyEtT0gPYK9jxpYjWy780mRYalmXMe';
    v_role_id INTEGER;
    v_existing_role_id INTEGER;
    v_user_id INTEGER;
    v_name TEXT;
    v_email TEXT;
    v_role_name TEXT;
BEGIN
    -- Evita ejecutar la semilla con el marcador sin reemplazar.
    IF v_hash = '__PASSWORD_HASH__'
       OR v_hash IS NULL
       OR length(v_hash) < 50 THEN
        RAISE EXCEPTION
            'Hash pendiente: genera el hash de Clave123 con hash_password() del proyecto.';
    END IF;

    -- Usuarios: administrador, organizadores y usuario pendiente.
    -- Después, los 32 jugadores.
    FOR v_name, v_email, v_role_name IN
        SELECT *
        FROM (VALUES
            ('Administrador', 'admin@demo.com', 'admin'),
            ('Organizador', 'organizador@demo.com', 'organizer'),
            ('Organizador 2', 'organizador2@demo.com', 'organizer'),
            ('Pendiente', 'pendiente@demo.com', 'pending'),
            ('Jugador 1', 'jugador1@demo.com', 'player'),
            ('Jugador 2', 'jugador2@demo.com', 'player'),
            ('Jugador 3', 'jugador3@demo.com', 'player'),
            ('Jugador 4', 'jugador4@demo.com', 'player'),
            ('Jugador 5', 'jugador5@demo.com', 'player'),
            ('Jugador 6', 'jugador6@demo.com', 'player'),
            ('Jugador 7', 'jugador7@demo.com', 'player'),
            ('Jugador 8', 'jugador8@demo.com', 'player'),
            ('Jugador 9', 'jugador9@demo.com', 'player'),
            ('Jugador 10', 'jugador10@demo.com', 'player'),
            ('Jugador 11', 'jugador11@demo.com', 'player'),
            ('Jugador 12', 'jugador12@demo.com', 'player'),
            ('Jugador 13', 'jugador13@demo.com', 'player'),
            ('Jugador 14', 'jugador14@demo.com', 'player'),
            ('Jugador 15', 'jugador15@demo.com', 'player'),
            ('Jugador 16', 'jugador16@demo.com', 'player'),
            ('Jugador 17', 'jugador17@demo.com', 'player'),
            ('Jugador 18', 'jugador18@demo.com', 'player'),
            ('Jugador 19', 'jugador19@demo.com', 'player'),
            ('Jugador 20', 'jugador20@demo.com', 'player'),
            ('Jugador 21', 'jugador21@demo.com', 'player'),
            ('Jugador 22', 'jugador22@demo.com', 'player'),
            ('Jugador 23', 'jugador23@demo.com', 'player'),
            ('Jugador 24', 'jugador24@demo.com', 'player'),
            ('Jugador 25', 'jugador25@demo.com', 'player'),
            ('Jugador 26', 'jugador26@demo.com', 'player'),
            ('Jugador 27', 'jugador27@demo.com', 'player'),
            ('Jugador 28', 'jugador28@demo.com', 'player'),
            ('Jugador 29', 'jugador29@demo.com', 'player'),
            ('Jugador 30', 'jugador30@demo.com', 'player'),
            ('Jugador 31', 'jugador31@demo.com', 'player'),
            ('Jugador 32', 'jugador32@demo.com', 'player')
        ) AS data(name, email, role_name)
    LOOP
        -- Resolver el rol por nombre, sin asumir sus IDs.
        SELECT role_id
        INTO v_role_id
        FROM security.role
        WHERE name = v_role_name;

        IF NOT FOUND THEN
            RAISE EXCEPTION
                'No existe el rol requerido: %', v_role_name;
        END IF;

        -- Si el correo ya existe, no sobrescribir el usuario.
        SELECT user_id, role_id
        INTO v_user_id, v_existing_role_id
        FROM security."user"
        WHERE email = v_email;

        IF FOUND THEN
            IF v_existing_role_id <> v_role_id THEN
                RAISE EXCEPTION
                    'El correo % ya existe con un rol diferente.',
                    v_email;
            END IF;
        ELSE
            INSERT INTO security."user" (
                name,
                email,
                password_hash,
                role_id,
                is_active
            )
            VALUES (
                v_name,
                v_email,
                v_hash,
                v_role_id,
                TRUE
            )
            RETURNING user_id INTO v_user_id;
        END IF;

        -- Crear perfil solamente para usuarios con rol player.
        IF v_role_name = 'player' THEN
            INSERT INTO players.player (user_id)
            SELECT v_user_id
            WHERE NOT EXISTS (
                SELECT 1
                FROM players.player
                WHERE user_id = v_user_id
            );
        END IF;
    END LOOP;
END;
$seed$;

-- Verificación de usuarios y perfiles insertados
-- Esperado: 36 registros en security."user" (1 admin, 2 organizadores, 1 pendiente, 32 jugadores)
-- Esperado: 32 registros en players.player (solo para usuarios con rol 'player')
SELECT u.email, r.name AS rol, p.player_id
FROM security."user" u
JOIN security.role r ON r.role_id = u.role_id
LEFT JOIN players.player p ON p.user_id = u.user_id
ORDER BY u.user_id;
