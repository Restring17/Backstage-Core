-- ==============================================================
-- MIGRACION: Registro financiero y auditoría de reservas
-- Ejecuta esto en Supabase → SQL Editor → New Query → Run
-- ==============================================================

-- 1. Columnas de penalidad en reservas (las necesitamos para cancelaciones confirmadas)
ALTER TABLE public.reservas
    ADD COLUMN IF NOT EXISTS monto_penalidad      REAL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS porcentaje_penalidad  REAL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS razon_cancelacion     TEXT,
    ADD COLUMN IF NOT EXISTS fecha_cancelacion     TIMESTAMP WITH TIME ZONE;

-- 2. Tabla de movimientos de caja
-- Registra cada ingreso real: pago de reserva, penalidad, o timeout de auditoría
CREATE TABLE IF NOT EXISTS public.movimientos_caja (
    id          BIGSERIAL PRIMARY KEY,
    id_reserva  TEXT REFERENCES public.reservas(id_reserva) ON DELETE SET NULL,
    tipo        TEXT NOT NULL,   -- 'INGRESO' | 'PENALIDAD' | 'TIMEOUT'
    monto       REAL NOT NULL DEFAULT 0,
    descripcion TEXT,
    fecha       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.movimientos_caja ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Permitir todo a anon en movimientos_caja"
    ON public.movimientos_caja FOR ALL TO anon USING (true) WITH CHECK (true);

-- 3. Actualizar la función RPC para que acepte los nuevos campos de penalidad
--    (reemplaza la función existente)
CREATE OR REPLACE FUNCTION public.guardar_reserva_con_recursos(
    p_reserva   JSONB,
    p_recursos  JSONB
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO public.reservas (
        id_reserva, id_ambiente, nombre_banda, manager_contacto,
        hora_inicio, hora_fin, estado,
        monto_sin_igv, monto_igv, monto_total,
        monto_penalidad, porcentaje_penalidad,
        razon_cancelacion, fecha_cancelacion
    ) VALUES (
        p_reserva->>'id_reserva',
        p_reserva->>'id_ambiente',
        p_reserva->>'nombre_banda',
        p_reserva->>'manager_contacto',
        (p_reserva->>'hora_inicio')::TIMESTAMPTZ,
        (p_reserva->>'hora_fin')::TIMESTAMPTZ,
        p_reserva->>'estado',
        (p_reserva->>'monto_sin_igv')::REAL,
        (p_reserva->>'monto_igv')::REAL,
        (p_reserva->>'monto_total')::REAL,
        COALESCE((p_reserva->>'monto_penalidad')::REAL, 0),
        COALESCE((p_reserva->>'porcentaje_penalidad')::REAL, 0),
        p_reserva->>'razon_cancelacion',
        CASE WHEN p_reserva->>'fecha_cancelacion' IS NOT NULL
             THEN (p_reserva->>'fecha_cancelacion')::TIMESTAMPTZ
             ELSE NULL END
    )
    ON CONFLICT (id_reserva) DO UPDATE SET
        estado                = EXCLUDED.estado,
        monto_penalidad       = EXCLUDED.monto_penalidad,
        porcentaje_penalidad  = EXCLUDED.porcentaje_penalidad,
        razon_cancelacion     = EXCLUDED.razon_cancelacion,
        fecha_cancelacion     = EXCLUDED.fecha_cancelacion;

    -- Recursos relacionados
    IF jsonb_array_length(p_recursos) > 0 THEN
        INSERT INTO public.reserva_recursos (id_reserva, id_recurso, precio_aplicado)
        SELECT
            p_reserva->>'id_reserva',
            (elem->>'id_recurso'),
            (elem->>'precio_aplicado')::REAL
        FROM jsonb_array_elements(p_recursos) AS elem
        ON CONFLICT DO NOTHING;
    END IF;

    RETURN TRUE;
EXCEPTION WHEN OTHERS THEN
    RAISE;
    RETURN FALSE;
END;
$$;

-- verificación
SELECT column_name FROM information_schema.columns
WHERE table_name = 'reservas' AND column_name IN ('monto_penalidad','porcentaje_penalidad','razon_cancelacion');
