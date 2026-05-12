# Checklist — Backstage-Core

Estado actual del proyecto. Marco lo que está hecho y lo que falta.

---

## Estructura de carpetas

- [x] `codigo_fuente/` — raíz del código Python
- [x] `codigo_fuente/models/`
- [x] `codigo_fuente/services/`
- [x] `codigo_fuente/database/`
- [x] `codigo_fuente/views/`

---

## Modelos (`models/`)

- [x] `recurso.py`
  - [x] `Recurso` (abstracta) — id, nombre, precio, estado, bloques horarios
  - [x] `EquipoFisico` (hereda de Recurso) — categoria, marca, peso, electricidad
  - [x] `PersonalTecnico` (hereda de Recurso) — especialidad, experiencia
  - [x] `EstadoDisponibilidad` (enum)
  - [x] `marcar_en_uso()`, `verificar_disponibilidad()`, `enviar_a_mantenimiento()`

- [x] `ambiente.py`
  - [x] `Ambiente` — bloques ocupados, verificación de disponibilidad
  - [x] `EstadoAmbiente` (enum)
  - [x] `bloquear_ambiente()`, `liberar_bloque()`, `generar_hoja_trabajo()`

- [x] `reserva.py`
  - [x] `ReservaEscenario`
  - [x] `EstadoReserva` (enum: PENDIENTE_PAGO, CONFIRMADA, CANCELADA, COMPLETADA)
  - [x] `TIMEOUT_PAGO_HORAS = 24` — 24h para pagar antes del rollback
  - [x] `BUFFER_OPERATIVO_MINUTOS = 30`
  - [x] `TASA_IGV = 0.18`
  - [x] `validar_reserva()`, `confirmar_reserva()`, `cancelar_reserva()`, `aplicar_timeout()`
  - [x] `calcular_presupuesto_total()`, `obtener_desglose_presupuesto()`

---

## Servicios (`services/`)

- [x] `tarificador.py`
  - [x] `calcular_costo_recurso()` — con recargos por tipo y experiencia
  - [x] `calcular_presupuesto_completo()` — ambiente + recursos + buffer + IGV
  - [x] `generar_factura()` — texto formateado para consola
  - [x] `calcular_penalidad()` — según días restantes antes del evento
  - [x] `generar_factura_penalidad()`

- [x] `gestor_reservas.py`
  - [x] `GestorReservas(tarificador, base_datos)` — acepta BD por inyección
  - [x] `crear_reserva()` — crea en memoria y persiste en BD
  - [x] `confirmar_pago_reserva()` — confirma + registra INGRESO en caja
  - [x] `cancelar_reserva()` — penalidad si corresponde + actualiza BD + registra caja
  - [x] `obtener_reserva()`, `obtener_reservas_activas()`, `obtener_historial_completo()`
  - [x] `generar_reporte_ocupacion_ambiente()`
  - [x] `generar_reporte_ingresos()` — resumen de la sesión en memoria

---

## Base de datos (`database/`)

- [x] `db_abstracta.py` — contrato `BaseDatos` (ABC)
  - [x] conexión, CRUD recursos, CRUD ambientes, CRUD reservas
  - [x] transacciones: `iniciar_transaccion()`, `confirmar_transaccion()`, `revertir_transaccion()`
  - [x] caja: `registrar_movimiento_caja()`, `obtener_movimientos_caja()`

- [x] `db_sqlite.py`
  - [x] Tablas creadas automáticamente al conectar (usando la conexión activa, no una temporal)
  - [x] `reservas` con columnas de penalidad: `monto_penalidad`, `porcentaje_penalidad`, `razon_cancelacion`, `fecha_cancelacion`
  - [x] `movimientos_caja` — registro financiero e historial de auditoría
  - [x] `registrar_movimiento_caja()` / `obtener_movimientos_caja()` implementados
  - [x] `limpiar_datos_test()` funcional

- [x] `db_supabase.py`
  - [x] Conecta usando `SUPABASE_URL` y `SUPABASE_KEY` del `.env`
  - [x] `guardar_reserva()` via RPC `guardar_reserva_con_recursos` (atómico en PostgreSQL)
  - [x] `registrar_movimiento_caja()` / `obtener_movimientos_caja()` implementados
  - [x] `limpiar_datos_test()` deshabilitada (nube)

- [x] `supabase_schema.sql` — schema inicial (tablas + RLS)
- [x] `supabase_datos_demo.sql` — datos de prueba (3 ambientes, 4 equipos, 3 técnicos)
- [x] `supabase_migracion_caja.sql` — ALTER TABLE reservas + CREATE movimientos_caja + RPC actualizado

---

## Vistas (`views/`)

- [x] `menu_consola.py`
  - [x] Selección de entorno al inicio (Supabase / SQLite)
  - [x] Carga datos de demo en SQLite (`_cargar_datos_demo`)
  - [x] Carga datos desde Supabase al iniciar modo nube (`_cargar_datos_supabase`)
  - [x] `_crear_reserva()` — parsea fecha con soporte de año de 2 dígitos
  - [x] `_confirmar_pago()` — actualiza BD + registra INGRESO en caja
  - [x] `_cancelar_reserva()` — delega toda la persistencia al GestorReservas
  - [x] `_reporte_ingresos()` — muestra sesión actual + histórico completo desde BD
  - [x] `_reporte_ocupacion()`, `_listar_recursos()`, `_listar_ambientes()`, `_info_conexion()`
  - [x] `_gestionar_mantenimiento()`

---

## Scripts y configuración

- [x] `1_Instalar_Requisitos.sh` — crea `.venv`, instala dependencias (Linux)
- [x] `2_Iniciar_Sistema.sh` — detecta `.venv`, arranca con ruta absoluta (Linux)
- [x] `1_Instalar_Requisitos.bat` — equivalente para Windows, misma lógica
- [x] `2_Iniciar_Sistema.bat` — usa `%~dp0` para path absoluto del venv (Windows)
- [x] `.env.example` — template de variables de entorno
- [x] `requirements.txt` — `supabase>=2.15.0`, `websockets>=13.0`, `python-dotenv>=1.0.0`, `python-dateutil>=2.8.2`

---

## Pendiente / mejoras posibles

- [ ] Tests unitarios para `Tarificador` y `GestorReservas`
- [ ] Políticas RLS de Supabase más restrictivas (ahora están en modo `anon` abierto)
- [ ] Paginación en reportes si el volumen de movimientos crece
- [ ] Exportar facturas a PDF o CSV
