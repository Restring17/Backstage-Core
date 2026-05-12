# 🎸 CHANGELOG: Actualizaciones Backstage-Core
**Fecha:** 03 de Mayo de 2026

## 📄 1. Actualizaciones en la Documentación (Word / UML)
* **Mejora de Redacción en Problemática:** Se elevó el nivel técnico de los "Problemas Específicos" utilizando terminología de ingeniería de software e industria musical (ej. *Falta de concurrencia*, *changeovers*, *soundchecks*).
* **Eliminación de Redundancia:** Se eliminó el diagrama de "Proceso de Pago" por ser un flujo sincrónico que ensuciaba la arquitectura.
* **Nuevo Proceso 2 (Gestión de Mantenimiento):** Se diseñó e integró un nuevo diagrama y flujo lógico para enviar equipos a mantenimiento, evitando conflictos de reserva.
* **Mejora del Proceso 3 (Cancelación con Penalidades):** Se actualizó el flujo de cancelación (Rollback) para incluir un cálculo de proximidad del evento y el cobro automático de penalidades corporativas.

## ⚙️ 2. Actualizaciones en la Lógica de Negocio (Backend)
* **Actualización de Timeout (`models/reserva.py`):** 
  * Se migró la lógica B2C a B2B.
  * Cambio de variable: `TIMEOUT_PAGO_MINUTOS` (3) pasó a `TIMEOUT_PAGO_HORAS` (24).
  * Se actualizó la fórmula matemática para calcular el tiempo transcurrido dividiendo entre 3600 segundos.
* **Control de Estados de Inventario (`models/recurso.py`):** 
  * Se actualizó el método `enviar_a_mantenimiento()`.
  * Ahora incluye validación de seguridad para evitar que equipos con bloques horarios futuros asignados o en estado `OCUPADO` sean retirados del sistema.
  * Retorna una tupla `(bool, str)` para mejor manejo en la vista.
* **Motor de Penalidades (`services/tarificador.py`):** 
  * Se agregó el método `calcular_penalidad(monto, dias_faltantes)` con reglas del 100% (≤14 días), 50% (15-29 días) y 10% (≥30 días).
  * Se agregó el método `generar_factura_penalidad()` para emitir el comprobante.
* **Orquestación de Cancelación (`services/gestor_reservas.py`):** 
  * Se reescribió `cancelar_reserva()` para calcular la fecha del evento contra `datetime.now()`, delegar el cálculo de cobro al Tarificador y luego ejecutar el Rollback.

## 🖥️ 3. Actualizaciones en la Interfaz de Usuario (`views/menu_consola.py`)
* **Refactorización a Código Limpio:** Se reemplazó la larga cadena de `if/elif` del menú principal por el patrón `match - case` (Structural Pattern Matching) nativo de Python 3.10+.
* **Nueva Opción en Menú:** Se añadió la opción `[8] Enviar Equipo a Mantenimiento` que conecta directamente con la nueva lógica de la clase `Recurso`.
* **Manejo de Excepciones (Anti-Crash):** Se envolvieron los `input()` numéricos (como los cobros) en bloques `try...except ValueError` para evitar cierres abruptos por errores de tipeo del usuario.
* **Corrección de Magic Strings:** Las actualizaciones de estado hacia la base de datos ahora utilizan los Enums oficiales (ej. `EstadoReserva.CANCELADA.value`) en lugar de strings sueltos propensos a errores.

## 🗄️ 4. Bases de Datos (`database/`)
* **DBSupabase:** Se proporcionó la estructura real (`_client.table("reservas").insert().execute()`) para reemplazar el código "mock" simulado, usando la librería oficial `supabase-py`. Se identificaron las variables de entorno necesarias (`SUPABASE_URL` y `SUPABASE_KEY` tipo *anon public*).
* **DBSQLite:** Se validó que el código actual ya está completamente funcional y automatizado, ejecutando el `CREATE TABLE IF NOT EXISTS` durante la inicialización de la clase, sin necesidad de configuración adicional.