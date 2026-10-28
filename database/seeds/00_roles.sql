-- =========================================================
-- Semilla 00: Roles del Sistema (00_roles.sql)
--
-- Propósito:
--   Inserta los 4 roles base del sistema en la tabla security.role.
--
-- Datos insertados:
--   - admin: Administrador global del sistema.
--   - organizer: Organizador de torneos.
--   - player: Jugador participante.
--   - pending: Usuario registrado pendiente de asignación de rol.
--
-- Requisitos previos:
--   - Esquema de base de datos creado mediante los scripts DDL (00_create_schemas.sql y 01_tables.sql).
--
-- Orden de ejecución:
--   1º en la secuencia (00 -> 01 -> 02 -> 03 -> 04 -> 05 -> 06).
-- =========================================================

-- Esperado: 4 registros en security.role
INSERT INTO security.role (name) VALUES
    ('admin'),
    ('organizer'),
    ('player'),
    ('pending');

-- Verificación de registros insertados
-- Esperado: 4 registros
SELECT role_id, name FROM security.role ORDER BY role_id;
