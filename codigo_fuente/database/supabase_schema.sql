-- ==============================================================================
-- Esquema de Base de Datos para Supabase (PostgreSQL)
-- Proyecto: Backstage-Core
-- ==============================================================================

-- 1. Tabla de Ambientes
CREATE TABLE IF NOT EXISTS public.ambientes (
    id_ambiente TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    capacidad_personas INTEGER,
    precio_alquiler_hora REAL NOT NULL,
    estado TEXT NOT NULL,
    requiere_sonido BOOLEAN,
    requiere_luces BOOLEAN,
    requiere_andamios BOOLEAN,
    datos_json JSONB,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Tabla de Recursos (Equivalente para Equipos Físicos y Personal Técnico)
CREATE TABLE IF NOT EXISTS public.recursos (
    id_recurso TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,
    precio_base_hora REAL NOT NULL,
    estado TEXT NOT NULL,
    categoria TEXT,
    marca TEXT,
    especialidad TEXT,
    requiere_electricidad BOOLEAN,
    peso_kg REAL,
    anos_experiencia INTEGER,
    datos_json JSONB,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Tabla de Reservas
CREATE TABLE IF NOT EXISTS public.reservas (
    id_reserva TEXT PRIMARY KEY,
    id_ambiente TEXT NOT NULL REFERENCES public.ambientes(id_ambiente) ON DELETE RESTRICT,
    nombre_banda TEXT NOT NULL,
    manager_contacto TEXT,
    hora_inicio TIMESTAMP WITH TIME ZONE NOT NULL,
    hora_fin TIMESTAMP WITH TIME ZONE NOT NULL,
    estado TEXT NOT NULL,
    monto_sin_igv REAL,
    monto_igv REAL,
    monto_total REAL,
    recursos_json JSONB,
    datos_json JSONB,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Tabla Intermedia: Reserva - Recursos (Relación Muchos a Muchos)
CREATE TABLE IF NOT EXISTS public.reserva_recursos (
    id_reserva TEXT REFERENCES public.reservas(id_reserva) ON DELETE CASCADE,
    id_recurso TEXT REFERENCES public.recursos(id_recurso) ON DELETE CASCADE,
    precio_aplicado REAL,
    PRIMARY KEY (id_reserva, id_recurso)
);

-- Configuración de seguridad (Opcional, pero recomendado en Supabase si usas el cliente anónimo)
-- Habilita RLS (Row Level Security)
ALTER TABLE public.ambientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recursos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reservas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reserva_recursos ENABLE ROW LEVEL SECURITY;

-- Políticas para permitir inserción/lectura total para la demostración (Ajustar en producción)
CREATE POLICY "Permitir todo a anon en ambientes" ON public.ambientes FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "Permitir todo a anon en recursos" ON public.recursos FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "Permitir todo a anon en reservas" ON public.reservas FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "Permitir todo a anon en reserva_recursos" ON public.reserva_recursos FOR ALL TO anon USING (true) WITH CHECK (true);
