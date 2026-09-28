-- =========================================================
-- TOWER OF CARDS SYSTEM
-- Triggers de auditoría
-- =========================================================


-- =========================================================
-- SECURITY
-- =========================================================

CREATE TRIGGER trg_audit_user
AFTER INSERT OR UPDATE OR DELETE ON security."user"
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('user_id');


CREATE TRIGGER trg_audit_role
AFTER INSERT OR UPDATE OR DELETE ON security.role
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('role_id');


-- =========================================================
-- PLAYERS
-- =========================================================

CREATE TRIGGER trg_audit_player
AFTER INSERT OR UPDATE OR DELETE ON players.player
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('player_id');


CREATE TRIGGER trg_audit_deck
AFTER INSERT OR UPDATE OR DELETE ON players.deck
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('deck_id');


CREATE TRIGGER trg_audit_deck_card
AFTER INSERT OR UPDATE OR DELETE ON players.deck_card
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('deck_id', 'card_id');


-- =========================================================
-- TOURNAMENTS
-- =========================================================

CREATE TRIGGER trg_audit_tournament
AFTER INSERT OR UPDATE OR DELETE ON tournaments.tournament
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('tournament_id');


CREATE TRIGGER trg_audit_round
AFTER INSERT OR UPDATE OR DELETE ON tournaments.round
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('round_id');


-- =========================================================
-- CARDS
-- =========================================================

CREATE TRIGGER trg_audit_card
AFTER INSERT OR UPDATE OR DELETE ON cards.card
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('card_id');


-- =========================================================
-- MATCHES
-- =========================================================

CREATE TRIGGER trg_audit_match
AFTER INSERT OR UPDATE OR DELETE ON matches.match
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('match_id');


CREATE TRIGGER trg_audit_result
AFTER INSERT OR UPDATE OR DELETE ON matches.result
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('result_id');


CREATE TRIGGER trg_audit_match_deck_card
AFTER INSERT OR UPDATE OR DELETE ON matches.match_deck_card
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('match_deck_card_id');


CREATE TRIGGER trg_audit_match_player_state
AFTER INSERT OR UPDATE OR DELETE ON matches.match_player_state
FOR EACH ROW
EXECUTE FUNCTION audit.fn_audit_log('match_id', 'player_slot');