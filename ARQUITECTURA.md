# 🏗️ ARQUITECTURA DEL SISTEMA - EventResourceManager

## Diagrama de Clases UML

```
┌─────────────────────────────────────────────────────────────┐
│                   📊 CAPA DE MODELOS (models/)              │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                  🎁 Recurso (Abstracta)                      │
│                                                              │
│  - id_recurso: str                                           │
│  - nombre: str                                               │
│  - precio_base_hora: float                                   │
│  - estado: EstadoDisponibilidad                              │
│  - _bloques_horarios_ocupados: List                          │
│                                                              │
│  + marcar_en_uso(hora_inicio, hora_fin)                     │
│  + verificar_disponibilidad(hora_inicio, hora_fin): bool    │
│  + enviar_a_mantenimiento()                                  │
│  + preparar_recurso(): dict (ABSTRACTO)                     │
│  + obtener_tipo_recurso(): str (ABSTRACTO)                  │
└──────────────────────────────────────────────────────────────┘
         △                                      △
         │ hereda                               │ hereda
         │                                      │
    ┌─────────────────────┐          ┌─────────────────────┐
    │  EquipoFisico       │          │ PersonalTecnico     │
    │                     │          │                     │
    │ - categoria: str    │          │ - especialidad: str │
    │ - marca: str        │          │ - años_experiencia  │
    │ - peso_kg: float    │          │ - activo: bool      │
    │ - requiere_...      │          │ - horas_extras      │
    │   electricidad      │          │                     │
    │                     │          │ + asignar_turno()   │
    └─────────────────────┘          └─────────────────────┘


┌──────────────────────────────────────────────────────────────┐
│                  🏛️  Ambiente                                 │
│                                                              │
│  - id_ambiente: str                                          │
│  - nombre: str                                               │
│  - capacidad_personas: int                                   │
│  - precio_alquiler_hora: float                               │
│  - estado: EstadoAmbiente                                    │
│  - _bloques_ocupados: List                                   │
│  - _equipos_asignados: List                                  │
│  - _personal_asignado: List                                  │
│                                                              │
│  + verificar_disponibilidad(hora_ini, hora_fin): bool       │
│  + bloquear_ambiente(hora_ini, hora_fin, id_res): bool      │
│  + liberar_bloque(id_reserva): bool                          │
│  + asignar_equipo(id_equipo)                                 │
│  + asignar_personal(id_personal)                             │
│  + generar_hoja_trabajo(): dict                              │
└──────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────┐
│              🎫 ReservaEscenario (TRANSACCIONAL)             │
│                                                              │
│  CONSTANTES:                                                 │
│  - TIMEOUT_PAGO_MINUTOS = 3                                  │
│  - BUFFER_OPERATIVO_MINUTOS = 30                             │
│  - TASA_IGV = 0.18 (18%)                                     │
│                                                              │
│  ATRIBUTOS:                                                  │
│  - id_reserva: str                                           │
│  - ambiente: Ambiente                                        │
│  - nombre_banda: str                                         │
│  - hora_inicio: datetime                                     │
│  - hora_fin: datetime                                        │
│  - hora_liberacion_real: datetime                            │
│  - _recursos_solicitados: List[Recurso]                     │
│  - estado: EstadoReserva                                     │
│  - monto_total_con_igv: float                                │
│                                                              │
│  MÉTODOS CLAVE:                                              │
│  + validar_reserva(): (bool, str)  ← VERIFICA disponibilidad│
│  + confirmar_reserva(monto): bool  ← RESUELVE bloqueo 3 min │
│  + cancelar_reserva(): bool        ← ROLLBACK automático    │
│  + calcular_presupuesto_total()    ← CALCULA costo + IGV    │
│  + aplicar_timeout(): bool         ← EXPIRA tras 3 minutos  │
│  + generar_hoja_trabajo(): dict    ← PARA técnicos          │
└──────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│             💼 CAPA DE SERVICIOS (services/)                │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              💰 Tarificador                                  │
│                                                              │
│  CONSTANTES:                                                 │
│  - TASA_IGV = 0.18                                           │
│  - BUFFER_MINUTOS = 30                                       │
│  - RECARGO_EQUIPOS_DELICADOS = 0.15                          │
│  - RECARGO_EXPERIENCIA = 0.10 per 5 años                     │
│                                                              │
│  + calcular_costo_recurso(recurso, duracion, recargos)      │
│  + calcular_presupuesto_completo(...)                        │
│  + validar_precio_recurso(recurso, precio): bool            │
│  + generar_factura(id_res, cliente, desglose): str          │
└──────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────┐
│            🎮 GestorReservas                                 │
│                                                              │
│  ESTADO INTERNO:                                             │
│  - _reservas_activas: dict                                   │
│  - _reservas_historial: List                                 │
│  - _tarificador: Tarificador                                │
│                                                              │
│  MÉTODOS TRANSACCIONALES:                                    │
│  + crear_reserva(...): ReservaEscenario                     │
│  + validar_reserva(id_res): (bool, str)                     │
│  + confirmar_pago_reserva(id_res, monto): bool              │
│  + cancelar_reserva(id_res, razon): bool                    │
│                                                              │
│  MÉTODOS DE CONSULTA:                                        │
│  + obtener_reserva(id_res): ReservaEscenario                │
│  + obtener_reservas_por_estado(estado): List                │
│  + obtener_reservas_por_ambiente(id_amb): List              │
│                                                              │
│  MÉTODOS DE REPORTING:                                       │
│  + generar_reporte_ocupacion_ambiente(id): dict             │
│  + generar_reporte_ingresos(): dict                          │
└──────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│         🗄️  CAPA DE PERSISTENCIA (database/)                │
│              (Patrón Repository)                             │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│            🔗 BaseDatos (Abstracta)                          │
│                                                              │
│  + conectar(): bool         (ABSTRACTO)                      │
│  + desconectar(): bool      (ABSTRACTO)                      │
│  + esta_conectado(): bool   (ABSTRACTO)                      │
│                                                              │
│  CRUD para Recursos:                                         │
│  + guardar_recurso(recurso): bool                            │
│  + obtener_recurso(id): dict                                 │
│  + obtener_todos_recursos(): List                            │
│  + actualizar_recurso(id, datos): bool                       │
│  + eliminar_recurso(id): bool                                │
│                                                              │
│  CRUD para Ambientes:                                        │
│  + guardar_ambiente(ambiente): bool                          │
│  + obtener_ambiente(id): dict                                │
│  + ... (los otros CRUD)                                      │
│                                                              │
│  CRUD para Reservas:                                         │
│  + guardar_reserva(reserva): bool                            │
│  + obtener_reserva(id): dict                                 │
│  + obtener_reservas_por_estado(estado): List                │
│  + ... (los otros CRUD)                                      │
│                                                              │
│  TRANSACCIONES:                                              │
│  + iniciar_transaccion(): bool                               │
│  + confirmar_transaccion(): bool                             │
│  + revertir_transaccion(): bool                              │
│                                                              │
│  UTILIDAD:                                                   │
│  + limpiar_datos_test(): bool                                │
│  + obtener_informacion_conexion(): dict                      │
└──────────────────────────────────────────────────────────────┘
         △                                      △
         │ implementa                           │ implementa
         │                                      │
    ┌─────────────────────┐          ┌──────────────────────┐
    │  DBSupabase         │          │  DBSQLite            │
    │                     │          │                      │
    │ (PostgreSQL Nube)   │          │ (SQLite Local/USB)   │
    │                     │          │                      │
    │ ✅ Escalable        │          │ ✅ Offline           │
    │ ✅ Multi-usuario    │          │ ✅ Sin dependencias  │
    │ ✅ Backup automático│          │ ✅ Portable          │
    │ ❌ Requiere Internet│          │ ❌ Mono-usuario      │
    │                     │          │                      │
    └─────────────────────┘          └──────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│          👁️  CAPA DE PRESENTACIÓN (views/)                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│            🖥️  MenuConsola                                   │
│                                                              │
│  MENÚ INICIO:                                                │
│  [1] 🌐 Nube (Supabase)                                     │
│  [2] 💾 Local (SQLite)                                      │
│                                                              │
│  MENÚ PRINCIPAL:                                             │
│  [1] 🎫 Crear Nueva Reserva                                 │
│  [2] 🔍 Consultar Reserva                                   │
│  [3] ✅ Confirmar Pago                                      │
│  [4] ❌ Cancelar Reserva                                    │
│  [5] 📊 Reporte Ocupación                                   │
│  [6] 💰 Reporte Ingresos                                    │
│  [7] 📦 Listar Recursos                                     │
│  [8] 🏛️  Listar Ambientes                                   │
│  [9] ℹ️  Info Conexión                                      │
│  [0] 🚪 Salir                                               │
│                                                              │
│  MÉTODOS:                                                    │
│  + seleccionar_entorno(): bool                              │
│  + ejecutar()                                                │
│  + mostrar_menu_principal()                                  │
│  - _crear_reserva()                                          │
│  - _confirmar_pago()                                         │
│  - _reporte_ingresos()                                       │
│  - ...                                                       │
└──────────────────────────────────────────────────────────────┘

```

---

## 🔄 Flujo Transaccional Completo

```
CLIENTE SOLICITA RESERVA
        ↓
[MenuConsola] → [GestorReservas.crear_reserva()]
        ↓
[ReservaEscenario] creada con estado PENDIENTE_PAGO
        ↓
[Tarificador.calcular_presupuesto_completo()]
  • Costo Ambiente × horas (con buffer 30 min)
  • Costo Recursos × horas (con buffer 30 min)
  • Aplica recargos por equipos/experiencia
  • Suma IGV 18%
        ↓
Reserva.id = "RES-20260409-0001"
Reserva.monto_total_con_igv = S/.1917.50
⏱️ BLOQUEO DE 3 MINUTOS INICIA
        ↓
CLIENTE CONFIRMA PAGO
        ↓
[MenuConsola] → [GestorReservas.confirmar_pago_reserva()]
        ↓
¿Pasó el timeout de 3 min?
├─ SÍ → [Rollback automático]
│        Todos los recursos Se liberan
│        Estado → CANCELADA
│        ❌ Volver a intentar
│
└─ NO → ¿Monto es correcto?
         ├─ NO → ❌ Error "Monto incorrecto"
         │
         └─ SÍ → ✅ Bloquea Ambiente
                  ✅ Bloquea Recursos (marcar_en_uso)
                  ✅ Asigna equipos al ambiente
                  Estado → CONFIRMADA
                  ✅ Guardar en BD
                  ✅ Generar hoja de trabajo
                  ✅ Mostrar factura
                        ↓
                  EVENTO LISTO PARA EJECUCIÓN
                        ↓
                  Hora INICIO: Escenario activo
                  Hora FIN + 30 min BUFFER: Libera recursos
```

---

## Matrices de CRUD por Nivel

| Operación | Modelo | Service | DB |
|-----------|--------|---------|-----|
| Crear Recurso | ✅ `Recurso.__init__()` | ❌ | ✅ `DBSQLite.guardar_recurso()` |
| Crear Reserva | ✅ `ReservaEscenario.__init__()` | ✅ `GestorReservas.crear_reserva()` | ✅ `DBSQLite.guardar_reserva()` |
| Validar Disponibilidad | ✅ `ReservaEscenario.validar_reserva()` | ✅ `GestorReservas.validar_reserva()` | ❌ |
| Calcular Presupuesto | ✅ `ReservaEscenario.calcular_presupuesto_total()` | ✅ `Tarificador.calcular_presupuesto_completo()` | ❌ |
| Confirmar Pago | ✅ `ReservaEscenario.confirmar_reserva()` | ✅ `GestorReservas.confirmar_pago_reserva()` | ✅ `actualizar_reserva()` |
| Cancelar | ✅ `ReservaEscenario.cancelar_reserva()` | ✅ `GestorReservas.cancelar_reserva()` | ✅ `actualizar_reserva()` |
| Consultar | ✅ `obtener_*` properties | ✅ `obtener_reserva()` | ✅ `obtener_reserva()` |
| Reportes | ❌ | ✅ Varios métodos | ✅ Consultas complejas |

---

## Concepto de Patrón Repositorio

```python
# El código de negocio NO sabe detalles de BD

# ❌ MALO: Acoplado a SQLite
class GestorReservas:
    def guardar_reserva(self, reserva):
        conexion = sqlite3.connect("..db")  # Dependencia directa
        
# ✅ BUENO: Desacoplado (Patrón Repositorio)
class GestorReservas:
    def __init__(self, base_datos: BaseDatos):  # Inyección de dependencia
        self._base_datos = base_datos
        
    def guardar_reserva(self, reserva):
        self._base_datos.guardar_reserva(reserva_dict)  # Agnóstico
        
# Ahora puedo cambiar:
# gestor = GestorReservas(DBSQLite())        # Modo local
# gestor = GestorReservas(DBSupabase())      # Modo nube
# Sin cambiar NADA en GestorReservas ✨
```

---

## Responsabilidades por Capa

### 📊 Models (Lógica de Dominio)
- Representa entidades del mundo real (Recurso, Ambiente, Reserva)
- Valida reglas de negocio a nivel de objeto
- NO conoce sobre BD o presentación

### 💼 Services (Lógica Aplicativa)
- Orquesta operaciones complejas
- Ejecuta transacciones
- Calcula valores derivados (presupuestos)
- UI llama aquí

### 🗄️ Database (Persistencia)
- Capa de abstracción
- Implementaciones concretas (SQLite, Supabase)
- Services NO conocen detalles internos

### 👁️ Views (Presentación)
- Interfaz usuario
- Recolecta inputs
- Muestra outputs
- Llama a Services

---

Esta arquitectura garantiza:
✅ **Separación de responsabilidades**  
✅ **Fácil de testear** (mocks posibles)  
✅ **Escalable** (agregar nuevas BD sin cambiar lógica)  
✅ **Mantenible** (cambios aislados)  
✅ **Profesional** (sigue patrones reales de la industria)
