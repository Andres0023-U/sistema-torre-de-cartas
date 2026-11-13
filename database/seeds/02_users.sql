-- =========================================================
-- Semilla 02: Usuarios y Perfiles de Jugador (02_users.sql)
--
-- Propósito:
--   Crear las cuentas de demostración para todos los roles del sistema y vincular
--   automáticamente los perfiles de jugador correspondientes en el esquema 'players'.
--
-- Datos insertados:
--   - 35 cuentas de usuario en security."user":
--       * 1 Administrador   : admin@demo.com
--       * 2 Organizadores   : organizador@demo.com, organizador2@demo.com
--       * 32 Jugadores      : jugador1@demo.com hasta jugador32@demo.com
--     (Contraseña de demostración para todas las cuentas: Clave123, inyectada por init-local-db.ps1)
--   - 32 perfiles de jugador en players.player asociados a jugador1@demo.com .. jugador32@demo.com.
--
-- Requisitos previos:
--   - Haber ejecutado 00_roles.sql (roles 'admin', 'organizer', 'player').
--
-- Orden de ejecución:
--   3º en la secuencia (00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06).
-- =========================================================

-- 1. Insertar usuarios de demostración con sus respectivos roles
-- Esperado: 35 registros en security."user"
INSERT INTO security."user" (name, email, password_hash, role_id)
SELECT
    v.name,
    v.email,
    '__PASSWORD_HASH__',
    r.role_id
FROM (
    VALUES
        (1,  'Administrador', 'admin@demo.com',       'admin'),
        (2,  'Organizador',   'organizador@demo.com',  'organizer'),
        (3,  'Organizador 2', 'organizador2@demo.com', 'organizer'),
        (4,  'Jugador 1',     'jugador1@demo.com',     'player'),
        (5,  'Jugador 2',     'jugador2@demo.com',     'player'),
        (6,  'Jugador 3',     'jugador3@demo.com',     'player'),
        (7,  'Jugador 4',     'jugador4@demo.com',     'player'),
        (8,  'Jugador 5',     'jugador5@demo.com',     'player'),
        (9,  'Jugador 6',     'jugador6@demo.com',     'player'),
        (10, 'Jugador 7',     'jugador7@demo.com',     'player'),
        (11, 'Jugador 8',     'jugador8@demo.com',     'player'),
        (12, 'Jugador 9',     'jugador9@demo.com',     'player'),
        (13, 'Jugador 10',    'jugador10@demo.com',    'player'),
        (14, 'Jugador 11',    'jugador11@demo.com',    'player'),
        (15, 'Jugador 12',    'jugador12@demo.com',    'player'),
        (16, 'Jugador 13',    'jugador13@demo.com',    'player'),
        (17, 'Jugador 14',    'jugador14@demo.com',    'player'),
        (18, 'Jugador 15',    'jugador15@demo.com',    'player'),
        (19, 'Jugador 16',    'jugador16@demo.com',    'player'),
        (20, 'Jugador 17',    'jugador17@demo.com',    'player'),
        (21, 'Jugador 18',    'jugador18@demo.com',    'player'),
        (22, 'Jugador 19',    'jugador19@demo.com',    'player'),
        (23, 'Jugador 20',    'jugador20@demo.com',    'player'),
        (24, 'Jugador 21',    'jugador21@demo.com',    'player'),
        (25, 'Jugador 22',    'jugador22@demo.com',    'player'),
        (26, 'Jugador 23',    'jugador23@demo.com',    'player'),
        (27, 'Jugador 24',    'jugador24@demo.com',    'player'),
        (28, 'Jugador 25',    'jugador25@demo.com',    'player'),
        (29, 'Jugador 26',    'jugador26@demo.com',    'player'),
        (30, 'Jugador 27',    'jugador27@demo.com',    'player'),
        (31, 'Jugador 28',    'jugador28@demo.com',    'player'),
        (32, 'Jugador 29',    'jugador29@demo.com',    'player'),
        (33, 'Jugador 30',    'jugador30@demo.com',    'player'),
        (34, 'Jugador 31',    'jugador31@demo.com',    'player'),
        (35, 'Jugador 32',    'jugador32@demo.com',    'player')
) AS v(ord, name, email, role_name)
JOIN security.role r ON r.name = v.role_name
ORDER BY v.ord
ON CONFLICT (email) DO NOTHING;

-- 2. Crear perfil de jugador para cada usuario con rol 'player'
-- Esperado: 32 registros en players.player
INSERT INTO players.player (user_id)
SELECT u.user_id
FROM security."user" u
JOIN security.role r ON r.role_id = u.role_id
WHERE r.name = 'player'
ORDER BY u.user_id
ON CONFLICT (user_id) DO NOTHING;

-- Verificación de registros insertados
-- Esperado: 35 usuarios y 32 perfiles de jugador
SELECT u.user_id, u.name, u.email, r.name AS role
FROM security."user" u
JOIN security.role r ON r.role_id = u.role_id
ORDER BY u.user_id;

SELECT p.player_id, p.user_id, u.name, u.email
FROM players.player p
JOIN security."user" u ON u.user_id = p.user_id
ORDER BY p.player_id;
