# Arquitectura — Backstage-Core

## Capas del sistema

```
views/menu_consola.py
        │
        ▼
services/gestor_reservas.py  ←→  services/tarificador.py
        │
        ▼
models/ (Recurso, Ambiente, ReservaEscenario)
        │
        ▼
database/ (BaseDatos → DBSQLite | DBSupabase)
```

La vista no habla directamente con la BD. Todo pasa por los servicios.  
Los modelos no saben nada de persistencia — solo contienen estado y reglas de negocio.

---

## Modelos

### Recurso (abstracta)

Base para `EquipoFisico` y `PersonalTecnico`.

```
Recurso
├── id_recurso, nombre, precio_base_hora, estado
├── _bloques_horarios_ocupados: List
├── marcar_en_uso(hora_inicio, hora_fin)
├── verificar_disponibilidad(hora_inicio, hora_fin): bool
├── enviar_a_mantenimiento()
├── preparar_recurso(): dict         ← abstracto
└── obtener_tipo_recurso(): str      ← abstracto

EquipoFisico(Recurso)
├── categoria, marca, peso_kg
└── requiere_electricidad: bool

PersonalTecnico(Recurso)
├── especialidad, anos_experiencia
└── activo: bool
```

### Ambiente

Maneja los bloques horarios ocupados del escenario.

```
Ambiente
├── id_ambiente, nombre, capacidad_personas
├── precio_alquiler_hora, estado
├── _bloques_ocupados: List
├── verificar_disponibilidad(hora_ini, hora_fin): bool
├── bloquear_ambiente(hora_ini, hora_fin, id_reserva): bool
└── liberar_bloque(id_reserva): bool
```

### ReservaEscenario

Clase central. Orquesta el ciclo de vida de una reserva.

```
ReservaEscenario
├── TIMEOUT_PAGO_HORAS = 24         # 24h para pagar antes del rollback
├── BUFFER_OPERATIVO_MINUTOS = 30   # tiempo de limpieza post-evento
├── TASA_IGV = 0.18
│
├── id_reserva, ambiente, nombre_banda, manager_contacto
├── hora_inicio, hora_fin, hora_liberacion_real
├── estado: EstadoReserva (PENDIENTE_PAGO → CONFIRMADA → CANCELADA/COMPLETADA)
├── monto_sin_igv, monto_igv, monto_total_con_igv
│
├── validar_reserva(): (bool, str)
├── confirmar_reserva(monto): bool
├── cancelar_reserva(): bool
├── aplicar_timeout(): bool
└── calcular_presupuesto_total()
```

---

## Servicios

### Tarificador

Solo matemáticas. No toca modelos ni BD.

- Calcula costo de cada recurso aplicando recargos (equipos delicados +15%, personal con experiencia +10% cada 5 años)
- Aplica el buffer de 30 min sobre la duración
- Genera facturas en texto formateado
- Calcula penalidades por cancelación según días restantes

### GestorReservas

Orquesta operaciones. Recibe `tarificador` y `base_datos` por constructor.

```python
GestorReservas(tarificador=Tarificador(), base_datos=DBSQLite())
```

Métodos principales:
- `crear_reserva(...)` → crea la reserva en memoria y la guarda en BD
- `confirmar_pago_reserva(id, monto)` → confirma y registra movimiento INGRESO en caja
- `cancelar_reserva(id, razon)` → aplica penalidad si corresponde, actualiza BD, registra PENALIDAD o TIMEOUT en caja
- `generar_reporte_ingresos()` → resumen en memoria
- (el reporte completo histórico lo hace directamente `menu_consola` consultando `obtener_movimientos_caja()`)

---

## Base de datos

### Patrón Repositorio

`GestorReservas` no sabe si habla con SQLite o Supabase. Solo conoce la interfaz:

```python
# para cambiar de BD, solo cambia aquí:
self._base_datos = DBSQLite("backstage_core.db")   # local
self._base_datos = DBSupabase()                     # nube
# el resto del código no cambia
```

### BaseDatos (abstracta)

Define el contrato que deben cumplir todas las implementaciones:
- Conexión: `conectar()`, `desconectar()`, `esta_conectado()`
- CRUD: recursos, ambientes, reservas
- Transacciones: `iniciar_transaccion()`, `confirmar_transaccion()`, `revertir_transaccion()`
- Caja: `registrar_movimiento_caja()`, `obtener_movimientos_caja()`

### DBSQLite

- Crea las tablas automáticamente al conectar
- Transacciones reales con BEGIN/COMMIT/ROLLBACK de sqlite3
- Archivo: `backstage_core.db` (se crea en `codigo_fuente/`)
- `limpiar_datos_test()` funcional (útil en desarrollo)

### DBSupabase

- Usa `supabase-py` con credenciales del `.env`
- `guardar_reserva()` usa RPC (`guardar_reserva_con_recursos`) para atomicidad real en PostgreSQL
- `iniciar_transaccion()` / `revertir_transaccion()` son no-ops — Supabase SDK no expone BEGIN/ROLLBACK directamente; el rollback real está en la función RPC de PostgreSQL
- `limpiar_datos_test()` deshabilitada en nube

---

## Tablas de BD

### `reservas`
| Campo | Tipo | Notas |
|-------|------|-------|
| id_reserva | TEXT PK | formato RES-YYYYMMDD-NNNN |
| id_ambiente | TEXT FK | |
| nombre_banda, manager_contacto | TEXT | |
| hora_inicio, hora_fin | TIMESTAMP | |
| estado | TEXT | PENDIENTE_PAGO / CONFIRMADA / CANCELADA |
| monto_sin_igv, monto_igv, monto_total | REAL | |
| monto_penalidad, porcentaje_penalidad | REAL | se llenan al cancelar |
| razon_cancelacion, fecha_cancelacion | TEXT/TS | solo en cancelaciones |

### `reserva_recursos`
Relación N:N entre reservas y recursos. Guarda el `precio_aplicado` en el momento de la reserva.

### `movimientos_caja`
| Campo | Tipo | Notas |
|-------|------|-------|
| id | SERIAL | autoincremental |
| id_reserva | TEXT FK | nullable (ON DELETE SET NULL) |
| tipo | TEXT | INGRESO / PENALIDAD / TIMEOUT |
| monto | REAL | 0 para TIMEOUT (solo auditoría) |
| descripcion | TEXT | |
| fecha | TIMESTAMP | |

---

## Flujo de una reserva

```
[1] Usuario crea reserva
    MenuConsola → GestorReservas.crear_reserva()
    → ReservaEscenario creada, estado=PENDIENTE_PAGO
    → GestorReservas llama base_datos.guardar_reserva() via RPC (Supabase) o INSERT (SQLite)

[2] Usuario confirma pago
    MenuConsola → GestorReservas.confirmar_pago_reserva()
    → Verifica timeout (24h)
    → Confirma en el modelo: bloquea ambiente + recursos
    → base_datos.actualizar_reserva(estado=CONFIRMADA)
    → base_datos.registrar_movimiento_caja(tipo=INGRESO, monto=total)

[3a] Usuario cancela
    MenuConsola → GestorReservas.cancelar_reserva()
    → Si CONFIRMADA: calcula penalidad según días restantes
    → Rollback en recursos (libera bloques horarios)
    → base_datos.actualizar_reserva(estado=CANCELADA, penalidad=...)
    → base_datos.registrar_movimiento_caja(tipo=PENALIDAD, monto=penalidad)

[3b] Timeout (reserva pendiente cancelada)
    → base_datos.actualizar_reserva(estado=CANCELADA)
    → base_datos.registrar_movimiento_caja(tipo=TIMEOUT, monto=0)
```
