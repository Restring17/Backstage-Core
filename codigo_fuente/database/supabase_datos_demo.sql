-- ==============================================================
-- DATOS DE DEMOSTRACIÓN - Backstage-Core (Supabase)
-- Ejecuta esto en: Supabase → SQL Editor → New Query → Run
-- ==============================================================

-- ===============================
-- 1. AMBIENTES (Escenarios)
-- ===============================
INSERT INTO public.ambientes
    (id_ambiente, nombre, capacidad_personas, precio_alquiler_hora,
     estado, requiere_sonido, requiere_luces, requiere_andamios)
VALUES
    ('AMB-001', 'Escenario Principal',   5000, 500.0, 'ACTIVO', true,  true,  false),
    ('AMB-002', 'Escenario Secundario',  2000, 250.0, 'ACTIVO', true,  true,  false),
    ('AMB-003', 'Sala de Ensayo',         200,  80.0, 'ACTIVO', true,  false, false)
ON CONFLICT (id_ambiente) DO UPDATE SET
    nombre               = EXCLUDED.nombre,
    capacidad_personas   = EXCLUDED.capacidad_personas,
    precio_alquiler_hora = EXCLUDED.precio_alquiler_hora,
    estado               = EXCLUDED.estado;

-- ===============================
-- 2. RECURSOS — Equipos Físicos
-- ===============================
INSERT INTO public.recursos
    (id_recurso, nombre, tipo, precio_base_hora, estado,
     categoria, marca, requiere_electricidad, peso_kg)
VALUES
    ('EQ-001', 'Consola Soundcraft Si Impact',          'EQUIPO_FISICO', 150.0, 'LIBRE',
     'Audio',       'Soundcraft', true,  45.5),
    ('EQ-002', 'Guitarra Eléctrica Fender Stratocaster','EQUIPO_FISICO',  50.0, 'LIBRE',
     'Instrumento', 'Fender',     false,  3.5),
    ('EQ-003', 'Kit de Iluminación LED PRO',            'EQUIPO_FISICO', 120.0, 'LIBRE',
     'Iluminación', 'Chauvet',    true,  22.0),
    ('EQ-004', 'Sistema de Sonido Line Array',          'EQUIPO_FISICO', 200.0, 'LIBRE',
     'Audio',       'JBL',        true,  80.0)
ON CONFLICT (id_recurso) DO UPDATE SET
    nombre               = EXCLUDED.nombre,
    precio_base_hora     = EXCLUDED.precio_base_hora,
    estado               = EXCLUDED.estado;

-- ===============================
-- 3. RECURSOS — Personal Técnico
-- ===============================
INSERT INTO public.recursos
    (id_recurso, nombre, tipo, precio_base_hora, estado,
     especialidad, anos_experiencia)
VALUES
    ('PERS-001', 'Juan García - Ingeniero de Sonido',        'PERSONAL_TECNICO',  80.0, 'LIBRE',
     'Sonido', 10),
    ('PERS-002', 'María López - Especialista en Iluminación','PERSONAL_TECNICO',  70.0, 'LIBRE',
     'Luces',   7),
    ('PERS-003', 'Carlos Ruiz - Técnico de Estructuras',     'PERSONAL_TECNICO',  65.0, 'LIBRE',
     'Estructuras', 5)
ON CONFLICT (id_recurso) DO UPDATE SET
    nombre               = EXCLUDED.nombre,
    precio_base_hora     = EXCLUDED.precio_base_hora,
    estado               = EXCLUDED.estado;

-- ===============================
-- VERIFICACIÓN: ver lo insertado
-- ===============================
SELECT 'AMBIENTES' AS tabla, COUNT(*) AS total FROM public.ambientes
UNION ALL
SELECT 'RECURSOS',           COUNT(*)           FROM public.recursos;
