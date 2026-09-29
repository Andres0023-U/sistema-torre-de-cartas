-- =========================================================
-- SEED: Roles base del sistema
-- Necesarios para que cualquier usuario pueda registrarse
-- =========================================================

INSERT INTO security.role (name) VALUES
    ('admin'),
    ('organizer'),
    ('player');