-- =========================================================
-- Semilla 00: Roles del Sistema (00_roles.sql)
--
-- Propósito:
--   Poblar el catálogo base de roles de seguridad del sistema Torre de Cartas (S.T.C.).
--
-- Datos insertados:
--   - 3 roles únicos en security.role:
--       1. 'admin'     : Administrador general de la plataforma.
--       2. 'organizer' : Organizador de torneos y gestor de rondas/partidas.
--       3. 'player'    : Jugador participante en torneos y creador de mazos.
--
-- Requisitos previos:
--   - Esquema 'security' y tabla 'security.role' creados mediante los scripts DDL.
--
-- Orden de ejecución:
--   1º en la secuencia (00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06).
-- =========================================================

-- Esperado: 3 registros en security.role
INSERT INTO security.role (name) VALUES
    ('admin'),
    ('organizer'),
    ('player')
ON CONFLICT (name) DO NOTHING;

-- Verificación de registros insertados
-- Esperado: 3 registros
SELECT role_id, name FROM security.role ORDER BY role_id;
