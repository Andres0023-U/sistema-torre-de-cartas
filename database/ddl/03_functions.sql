-- =========================================================
-- TOWER OF CARDS SYSTEM
-- Funciones
-- =========================================================

-- =========================================================
-- FUNCIÓN: REGISTRO DE AUDITORÍA
-- =========================================================

CREATE OR REPLACE FUNCTION audit.fn_audit_log()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_record_id TEXT;
    v_user_id INTEGER;
    v_record JSONB;
    v_key_columns TEXT[];
    v_column TEXT;
    v_value TEXT;
BEGIN

    -- =====================================================
    -- Determinar el registro afectado
    -- =====================================================

    IF TG_OP = 'DELETE' THEN
        v_record := to_jsonb(OLD);
    ELSE
        v_record := to_jsonb(NEW);
    END IF;


    -- =====================================================
    -- Obtener las columnas de la clave primaria
    -- =====================================================

    v_key_columns := TG_ARGV;


    -- =====================================================
    -- Construir record_id
    -- =====================================================

    FOREACH v_column IN ARRAY v_key_columns
    LOOP

        v_value := v_record ->> v_column;

        IF v_record_id IS NULL THEN
            v_record_id := v_value;
        ELSE
            v_record_id := v_record_id || '-' || v_value;
        END IF;

    END LOOP;


    -- =====================================================
    -- Obtener el usuario de la aplicación
    -- =====================================================

    BEGIN
        v_user_id := NULLIF(
            current_setting('app.user_id', true),
            ''
        )::INTEGER;
    EXCEPTION
        WHEN OTHERS THEN
            v_user_id := NULL;
    END;


    -- =====================================================
    -- Registrar la operación
    -- =====================================================

    INSERT INTO audit.audit_log (
        user_id,
        action,
        table_name,
        record_id,
        old_values,
        new_values
    )
    VALUES (
        v_user_id,
        TG_OP,
        TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
        v_record_id,

        CASE
            WHEN TG_OP IN ('UPDATE', 'DELETE')
            THEN to_jsonb(OLD)::TEXT
            ELSE NULL
        END,

        CASE
            WHEN TG_OP IN ('INSERT', 'UPDATE')
            THEN to_jsonb(NEW)::TEXT
            ELSE NULL
        END
    );


    -- =====================================================
    -- Devolver el registro correspondiente
    -- =====================================================

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;

END;
$$;