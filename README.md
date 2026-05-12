# Backstage-Core

Sistema de gestión de recursos para eventos musicales. Permite reservar escenarios con sus equipos y personal técnico, controlando disponibilidad horaria y calculando presupuestos con IGV.

Corre en modo nube (Supabase) o modo local (SQLite), sin cambiar nada de la lógica.

---

## Stack

- Python 3.12+
- SQLite (modo offline, sin dependencias extra)
- Supabase / PostgreSQL (modo nube, requiere internet y `.env`)
- `supabase-py`, `python-dotenv`

---

## Estructura

```
codigo_fuente/
├── main.py
├── requirements.txt
│
├── models/
│   ├── recurso.py        # Recurso (ABC), EquipoFisico, PersonalTecnico
│   ├── ambiente.py       # Ambiente + gestión de bloques horarios
│   └── reserva.py        # ReservaEscenario + EstadoReserva
│
├── services/
│   ├── tarificador.py    # Cálculo de precios, IGV, recargos, facturas
│   └── gestor_reservas.py # Orquesta el ciclo de vida de una reserva
│
├── database/
│   ├── db_abstracta.py   # Interfaz BaseDatos (ABC)
│   ├── db_supabase.py    # Implementación para Supabase
│   └── db_sqlite.py      # Implementación para SQLite local
│
└── views/
    └── menu_consola.py   # Menú interactivo en consola
```

---

## Inicio rápido

**Linux / macOS:**
```bash
./1_Instalar_Requisitos.sh
./2_Iniciar_Sistema.sh
```

**Windows:**
```
1_Instalar_Requisitos.bat
2_Iniciar_Sistema.bat
```

Para modo Supabase, copia `.env.example` → `.env` y pon las credenciales antes de arrancar.

---

## Autor

Adrian Jose Felix Ramirez Rivera (`Restring17`)
