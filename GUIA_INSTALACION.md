# Guía de instalación — Backstage-Core

## Requisitos

- Python 3.12 o superior
- Conexión a internet solo si usas modo Supabase

---

## Instalación

### Linux / macOS

```bash
# 1. instala dependencias en un venv aislado
./1_Instalar_Requisitos.sh

# 2. arranca el sistema
./2_Iniciar_Sistema.sh
```

### Windows

Doble clic en `1_Instalar_Requisitos.bat`, luego `2_Iniciar_Sistema.bat`.

Los scripts crean automáticamente un entorno virtual `.venv/` en la raíz del proyecto e instalan todo ahí, sin tocar el Python del sistema.

### Manual (cualquier OS)

```bash
# desde la raíz del proyecto
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r codigo_fuente/requirements.txt
cd codigo_fuente
python main.py
```

---

## Configuración de Supabase

Si vas a usar el modo nube:

1. Crea un proyecto en https://supabase.com
2. Ve a Settings → API y copia la URL y la `anon key`
3. Copia `.env.example` → `.env` en la raíz del proyecto y pega tus credenciales:

```
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=eyJ...
```

4. Importa el schema SQL: abre el SQL Editor de Supabase y pega el contenido de `codigo_fuente/database/supabase_schema.sql`

5. Carga datos de demo: ejecuta `codigo_fuente/database/supabase_datos_demo.sql` en el mismo editor

6. Si ya tienes una base existente y quieres agregar el registro de caja, ejecuta también `supabase_migracion_caja.sql`

---

## Uso del sistema

Al arrancar se elige el entorno:

```
[1] Nube (Supabase)
[2] Local (SQLite)
[3] Salir
```

**Modo Local** carga datos de demo automáticamente (3 ambientes, 4 equipos, 3 técnicos).  
**Modo Supabase** necesita que los datos estén en la BD antes de operar.

### Menú principal

| Opción | Función |
|--------|---------|
| 1 | Crear nueva reserva |
| 2 | Consultar reserva por ID |
| 3 | Confirmar pago |
| 4 | Cancelar reserva |
| 5 | Reporte de ocupación por ambiente |
| 6 | Reporte de ingresos (sesión + histórico BD) |
| 7 | Listar recursos disponibles |
| 8 | Listar ambientes |
| 9 | Info de conexión |
| 0 | Salir |

### Flujo de una reserva

1. Crea reserva → estado `PENDIENTE_PAGO`, tienes **24 horas** para pagar
2. Confirmas pago → estado `CONFIRMADA`, recursos bloqueados
3. Post-evento: los recursos se liberan **30 minutos después** del fin (buffer de desarme)
4. Si cancelas una reserva confirmada → se aplica penalidad según días restantes

### Cálculo de precios

```
Ambiente:  S/.500/hora × 2.5 horas (2h evento + 0.5h buffer) = S/.1250
Equipo:    S/.150/hora × 2.5 horas                           = S/.375
Personal:  S/.80/hora  × 2.5 horas                           = S/.200
Subtotal:                                                       S/.1825
IGV 18%:                                                        S/.328.50
TOTAL:                                                          S/.2153.50
```

---

## Estructura del proyecto

```
Backstage-Core/
├── codigo_fuente/
│   ├── main.py
│   ├── requirements.txt
│   ├── models/
│   │   ├── recurso.py        # clases de recursos (equipo/personal)
│   │   ├── ambiente.py       # escenarios y bloques horarios
│   │   └── reserva.py        # ciclo de vida de una reserva
│   ├── services/
│   │   ├── tarificador.py    # precios, IGV, facturas, penalidades
│   │   └── gestor_reservas.py
│   ├── database/
│   │   ├── db_abstracta.py
│   │   ├── db_supabase.py
│   │   ├── db_sqlite.py
│   │   ├── supabase_schema.sql
│   │   ├── supabase_datos_demo.sql
│   │   └── supabase_migracion_caja.sql
│   └── views/
│       └── menu_consola.py
│
├── 1_Instalar_Requisitos.sh / .bat
├── 2_Iniciar_Sistema.sh / .bat
├── .env.example
└── README.md
```

---

## Problemas comunes

**"No existe el fichero .venv/bin/python3"**  
Ejecuta primero `1_Instalar_Requisitos.sh`. Si el error persiste, borra la carpeta `.venv/` y vuelve a ejecutar el script.

**"Error de conexión a Supabase"**  
Verifica que el archivo `.env` existe en la raíz (no dentro de `codigo_fuente/`) y que las credenciales son correctas. El sistema busca el `.env` usando `python-dotenv`.

**"No hay ambientes disponibles" en modo Supabase**  
Las tablas están vacías. Ejecuta `supabase_datos_demo.sql` desde el SQL Editor de Supabase.

**"ModuleNotFoundError: No module named 'supabase'"**  
El entorno virtual no tiene las dependencias. Ejecuta `1_Instalar_Requisitos.sh` de nuevo o activa el venv manualmente y corre `pip install -r codigo_fuente/requirements.txt`.

---

## Seguridad

- El archivo `.env` no debe subirse a git. Está en `.gitignore` por defecto.
- Las claves que veas en la `GUIA_INSTALACION.md` antigua eran de un proyecto de prueba — si las pusiste en producción, regéneralas desde el panel de Supabase (Settings → API → Regenerate).
- Las políticas RLS del schema están en modo `anon` para demo. En producción habría que restringirlas.
