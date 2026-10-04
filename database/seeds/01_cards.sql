-- =========================================================
-- SEED: Catálogo de cartas
-- =========================================================

INSERT INTO cards.card (card_id, card_name, value, type, effect, max_quantity, rarity, description) VALUES
(1, 'Ataque Básico', 1, 'ataque', 'Ninguno', 4, 'común', 'Inflige 1 de daño.'),
(2, 'Ataque Normal', 2, 'ataque', 'Ninguno', 3, 'poco común', 'Inflige 2 de daño.'),
(3, 'Ataque Fuerte', 3, 'ataque', 'Ninguno', 2, 'rara', 'Inflige 3 de daño.'),
(4, 'Ataque Devastador', 5, 'ataque', 'Ninguno', 1, 'legendaria', 'Inflige 5 de daño.'),
(5, 'Defensa Básica', 1, 'defensa', 'Ninguno', 4, 'común', 'Cubre 1 de daño.'),
(6, 'Defensa Normal', 2, 'defensa', 'Ninguno', 3, 'poco común', 'Cubre 2 de daño.'),
(7, 'Defensa Fuerte', 3, 'defensa', 'Ninguno', 2, 'rara', 'Cubre 3 de daño.'),
(8, 'Defensa Implacable', 5, 'defensa', 'Ninguno', 1, 'legendaria', 'Cubre 5 de daño.'),
(9, 'Curación Básica', 1, 'especial', 'Ninguno', 4, 'común', 'Cura 1 unidad.'),
(10, 'Curación Normal', 2, 'especial', 'Ninguno', 3, 'poco común', 'Cura 2 unidades.'),
(11, 'Curación Fuerte', 3, 'especial', 'Ninguno', 2, 'rara', 'Cura 3 unidades.'),
(12, 'Curación Vigorosa', 5, 'especial', 'Ninguno', 1, 'legendaria', 'Cura 5 unidades.'),
(13, 'Masa Crítica', 0, 'especial', 'Genera daño por la cantidad de cartas de tipo daño en la mano.', 2, 'rara', 'Usa todas tus armas contra el enemigo.'),
(14, 'Muro de Contención', 0, 'especial', 'Genera defensa por la cantidad de cartas de tipo defensa en la mano.', 2, 'rara', 'Usa todas tus defensas para tu fortaleza.'),
(15, 'Infiltración', 0, 'especial', 'Revela la mano de tu enemigo.', 2, 'rara', 'Que tu enemigo quede al desnudo.'),
(16, 'Reinicio Táctico', 0, 'especial', 'Cambia todas tus cartas por nuevas.', 2, 'rara', 'Borrón y cartas nuevas.'),
(17, 'Desarme', 0, 'especial', 'El enemigo pierde una carta de su mano.', 2, 'rara', 'Deja al enemigo sin garras.'),
(18, 'Caja de Suministros', 0, 'especial', 'Consigues dos cartas de tu mazo.', 2, 'rara', 'Asegúrate de tener tu mano con dos espacios libres antes de usarla, no quieres desperdiciar esta carta.');