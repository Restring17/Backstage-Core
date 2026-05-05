# 🎸 GUÍA DE INSTALACIÓN Y USO - EventResourceManager

## 📋 Requisitos Previos

- **Python 3.12+** instalado ([descargar](https://www.python.org/downloads/))
- **Git** (opcional, para clonar el repositorio)
- Conexión a Internet (solo si usas modo Supabase)

---

## 🚀 Instalación Rápida (Windows)

### Opción 1: Archivos Batch (Recomendado)

1. **Descarga o clona el repositorio**
   ```bash
   git clone https://github.com/Restring17/Backstage-Core.git
   cd Backstage-Core
   ```

2. **Ejecuta el instalador**
   - Haz doble clic en `1_Instalar_Requisitos.bat`
   - Espera a que termine (verás "Instalación completada")

3. **Inicia el sistema**
   - Haz doble clic en `2_Iniciar_Sistema.bat`
   - Selecciona tu entorno: `[2] Local (SQLite)` para empezar

### Opción 2: Terminal Manual

```bash
# Navega al directorio del proyecto
cd codigo_fuente

# Instala dependencias
pip install -r requirements.txt

# Ejecuta el sistema
python main.py
```

---

## 🌐 Configuración de Supabase (Modo Nube)

Si quieres usar **modo Supabase** en lugar de SQLite local:

1. **Crea una cuenta en Supabase**
   - Accede a https://supabase.com
   - Crea un nuevo proyecto

2. **Obtén tus credenciales**
   - Proyecto → Settings → API
   - Copia `URL de proyecto` y `anon key`

3. **Configura variables de entorno (Windows)**
   ```bash
   setx SUPABASE_URL "https://vyrekmlhxcljvilzmyan.supabase.co"
   setx SUPABASE_KEY "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ5cmVrbWxoeGNsanZpbHpteWFuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4MzIyNzcsImV4cCI6MjA5MzQwODI3N30.XU5PEXe02oZ4fUE5_ubsZNbc9xiyLT9B97_c8vxNo2o"
   ```

4. **Reinicia la terminal y ejecuta**
   ```bash
   python main.py
   ```

5. **En el menú, selecciona**
   ```
   [1] Nube (Supabase - Requiere Internet)
   ```

---

## 📁 Estructura del Proyecto

```
Backstage-Core/
├── codigo_fuente/
│   ├── main.py                    # Punto de entrada
│   ├── requirements.txt           # Dependencias Python
│   │
│   ├── models/                    # Clases del modelo
│   │   ├── recurso.py            # Recurso, EquipoFisico, PersonalTecnico
│   │   ├── ambiente.py           # Ambiente (escenario)
│   │   └── reserva.py            # ReservaEscenario (lógica transaccional)
│   │
│   ├── services/                  # Lógica de negocio
│   │   ├── tarificador.py        # Cálculo de presupuestos + IGV
│   │   └── gestor_reservas.py    # Validación y control de transacciones
│   │
│   ├── database/                  # Capa de persistencia (Patrón Repositorio)
│   │   ├── db_abstracta.py       # Interfaz BaseDatos
│   │   ├── db_supabase.py        # Implementación PostgreSQL (Nube)
│   │   └── db_sqlite.py          # Implementación SQLite (Local/USB)
│   │
│   └── views/                     # Interfaz de usuario
│       └── menu_consola.py       # Menú interactivo
│
├── 1_Instalar_Requisitos.bat     # Script de instalación (Windows)
├── 2_Iniciar_Sistema.bat         # Script de inicio (Windows)
├── .env.example                  # Ejemplo de configuración
├── README.md                      # Descripción del proyecto
└── LICENSE
```

---

## 🎮 Uso del Sistema

### Pantalla de Inicio

```
[1] 🌐 Nube (Supabase - Requiere Internet)
[2] 💾 Local (SQLite - Modo Offline/USB)
[3] ❌ Salir
```

**Recomendación**: Comienza con `[2] Local` para probar sin conexión.

### Menú Principal

Una vez dentro, verás opciones para:

1. **🎫 Crear Nueva Reserva**
   - Selecciona un ambiente
   - Ingresa datos de la banda
   - Elige recursos (equipos y personal técnico)
   - El sistema calcula automáticamente el costo + IGV (18%)

2. **🔍 Consultar Reserva**
   - Ingresa el ID de reserva generado
   - Ve el estado y detalles

3. **✅ Confirmar Pago**
   - Resuelve el bloqueo de 3 minutos
   - Ingresa el monto exacto para confirmar

4. **❌ Cancelar Reserva**
   - Realiza rollback automático
   - Libera todos los recursos

5. **📊 Reporte de Ocupación**
   - Ve qué escenarios están ocupados

6. **💰 Reporte de Ingresos**
   - Total recaudado, IGV, promedios

---

## 💡 Características Principales

### Buffer Operativo (30 minutos)
El sistema añade automáticamente 30 minutos después de cada evento para limpieza/desarme.
```python
# Ejemplo: Si reservas de 18:00 a 20:00
# Los recursos se liberan recién a las 20:30
```

### Bloqueo de Transacción (3 minutos)
Si creas una reserva, tienes 3 minutos para confirmar el pago.
```python
# Si no confirmas en 3 minutos → Rollback automático
# Todos los recursos se liberan
```

### Cálculo de IGV (18%)
El presupuesto se calcula automáticamente con impuestos incluidos.
```python
# Ambiente: 500/hora × 2.5 horas = 1250
# Recursos: 150/hora × 2.5 horas = 375
# Subtotal: 1625
# IGV 18%: 292.50
# TOTAL: 1917.50
```

### Arquitectura Dual (Nube/Local)
Gracias al Patrón Repositorio, puedes cambiar entre Supabase y SQLite sin cambiar tu código.

---

## 🐛 Solución de Problemas

### "Python no está instalado"
```
❌ ERROR: Python no está instalado o no está en el PATH
```
**Solución**: Descarga e instala [Python 3.12+](https://www.python.org/downloads/). Asegúrate de marcar "Add Python to PATH" durante la instalación.

### "Error de conexión a Supabase"
```
❌ Error: No se pudo conectar a Supabase. ¿Credenciales configuradas?
```
**Solución**: Verifica que las variables de entorno `SUPABASE_URL` y `SUPABASE_KEY` estén configuradas correctamente.

### "Módulo no encontrado"
```
ModuleNotFoundError: No module named 'models'
```
**Solución**: Asegúrate de ejecutar desde `codigo_fuente/`:
```bash
cd codigo_fuente
python main.py
```

### "No hay ambientes disponibles"
Al usar Supabase por primera vez, necesitas crear ambientes y recursos en la BD. Por ahora, usa modo Local que carga datos de demostración automáticamente.

---

## 📊 Datos de Demostración (Modo Local)

Al iniciar en modo SQLite, el sistema carga:

**Ambientes:**
- Escenario Principal (5000 personas) - S/.500/hora
- Escenario Secundario (2000 personas) - S/.250/hora

**Equipos:**
- Consola Soundcraft Si Impact - S/.150/hora
- Guitarra Eléctrica Fender Stratocaster - S/.50/hora

**Personal Técnico:**
- Juan García (Ingeniero de Sonido) - S/.80/hora
- María López (Especialista Iluminación) - S/.70/hora

---

## 🔐 Seguridad

### Para Supabase:
- **NUNCA** hagas commit del archivo `.env` con credenciales reales
- Usa `.env.example` como plantilla
- En producción, usa variables de entorno del sistema/contenedor

### Para SQLite:
- El archivo `backstage_core.db` contiene todos los datos locales
- Ten un backup del USB si lo usas como "USB blindado"
- La opción "Limpiar datos" (`[3]` en el menú local) está disponible solo para testing

---

## 📚 Documentación Técnica

### Clases Principales

#### `Recurso` (Abstracta)
```python
class Recurso(ABC):
    # Propiedades comunes
    id_recurso, nombre, precio_base_hora, estado
    
    # Métodos abstractos
    preparar_recurso()
    obtener_tipo_recurso()
    
    # Métodos comunes
    marcar_en_uso(hora_inicio, hora_fin)
    verificar_disponibilidad(hora_inicio, hora_fin)
```

#### `EquipoFisico` (Hereda de Recurso)
```python
class EquipoFisico(Recurso):
    categoria  # Instrumento, Iluminación, Andamiaje
    marca
    requiere_conexion_electrica
    peso_kg
```

#### `PersonalTecnico` (Hereda de Recurso)
```python
class PersonalTecnico(Recurso):
    especialidad  # Sonido, Luces, Estructuras
    años_experiencia
    activo
    horas_extras_acumuladas
```

#### `ReservaEscenario` (Transaccional)
```python
class ReservaEscenario:
    TIMEOUT_PAGO_MINUTOS = 3
    BUFFER_OPERATIVO_MINUTOS = 30
    TASA_IGV = 0.18  # 18%
    
    # Métodos clave
    validar_reserva()
    confirmar_reserva(monto_a_pagar)
    cancelar_reserva()
    calcular_presupuesto_total()
```

---

## 🎯 Próximos Pasos

1. **Prueba el sistema localmente** con datos de demostración
2. **Crea algunas reservas** y experimenta con los horarios
3. **Confirma pagos** para ver cómo cambian los estados
4. **Consulta reportes** de ingresos y ocupación
5. (Opcional) **Conecta a Supabase** para persistencia en la nube

---

## 👨‍💻 Autor

**Adrian Jose Felix Ramirez Rivera** (`Restring17`)  
Estudiante de Ingeniería de Sistemas y Software  
Proyecto Final - Curso de Lenguajes de Programación

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## ❓ Preguntas/Soporte

Si tienes problemas:
1. Revisa esta guía
2. Verifica que Python esté correctamente instalado
3. Asegúrate de estar en la carpeta `codigo_fuente/`
4. Intenta ejecutar en modo SQLite local primero

¡Que disfrutes usando Backstage-Core! 🎸
