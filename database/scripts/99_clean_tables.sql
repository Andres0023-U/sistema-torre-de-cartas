BEGIN;

-- Semilla 06: partidas, resultados y datos relacionados
TRUNCATE TABLE matches.match RESTART IDENTITY CASCADE;

-- Semilla 05: inscripciones
TRUNCATE TABLE tournaments.tournament_registration RESTART IDENTITY CASCADE;

-- Semilla 04: torneos y rondas
TRUNCATE TABLE tournaments.tournament RESTART IDENTITY CASCADE;

-- Semilla 03: mazos
TRUNCATE TABLE players.deck RESTART IDENTITY CASCADE;

-- Semilla 02: perfiles de jugadores y usuarios
TRUNCATE TABLE players.player RESTART IDENTITY CASCADE;
TRUNCATE TABLE security."user" RESTART IDENTITY CASCADE;

-- Semilla 01: catálogo de cartas
TRUNCATE TABLE cards.card RESTART IDENTITY CASCADE;

-- Semilla 00: roles
TRUNCATE TABLE security.role RESTART IDENTITY CASCADE;

COMMIT;