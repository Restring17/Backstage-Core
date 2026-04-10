# 🎸 EventResourceManager (Backstage-Core)

**Sistema de Gestión de Recursos, Inventario y Personal para Eventos Musicales.**
Proyecto final para el curso de Lenguajes de Programación, desarrollado 100% en Python aplicando los pilares de la Programación Orientada a Objetos (POO).

---

## 📖 Descripción del Proyecto

Las productoras de eventos y festivales enfrentan problemas críticos al gestionar múltiples escenarios simultáneamente. Este sistema backend resuelve la asignación transaccional de recursos finitos: asegura que el inventario físico (instrumentos, consolas, andamios) y el personal técnico especializado no se crucen en el mismo bloque horario.

El sistema simula el motor de reservas interno de un festival, validando disponibilidad en tiempo real, calculando presupuestos dinámicos e impidiendo la sobreasignación de recursos mediante bloqueos de concurrencia.

---

## ✨ Características Principales (Lógica de Negocio)

* **Tarificador Dinámico:** Cálculo automático del costo total de alquiler de equipos y personal, incluyendo el desglose de impuestos (IGV 18%).
* **Buffer Operativo (Brecha de Tiempo):** El sistema añade automáticamente una brecha de 30 minutos al finalizar cada evento para labores de limpieza y desarme técnico, bloqueando los recursos durante ese periodo.
* **Control de Concurrencia (Bloqueo de 3 Minutos):** Al iniciar una reserva, los recursos entran en estado `PENDIENTE_PAGO` por 3 minutos. Si no se confirma la transacción, el sistema realiza un *Rollback* automático, liberando el stock.
* **Arquitectura Dual de Base de Datos:** Soporte nativo para operar en la Nube o de manera Local sin cambiar la lógica del negocio (Patrón Repositorio).

---

## 🛠️ Stack Tecnológico y Paradigma

* **Lenguaje:** Python 3.12+
* **Paradigma:** Programación Orientada a Objetos (Herencia, Polimorfismo, Abstracción, Encapsulamiento).
* **Base de Datos (Nube):** Supabase (PostgreSQL) vía `supabase-py`.
* **Base de Datos (Local):** SQLite (Módulo integrado `sqlite3`).
* **Entorno de Desarrollo:** VSCode / PyCharm (Fácilmente portable a Google Colab).

---

## 🏗️ Arquitectura del Proyecto

El proyecto está diseñado a prueba de fallos de conectividad, permitiendo arrancar en dos modalidades distintas a través de un Bootloader principal.

```text
📁 codigo_fuente/
├── 📄 main.py                 # (El punto de entrada que llama a las vistas)
│
├── 📁 models/                 # (El MODELO: solo clases y atributos)
│   ├── 📄 recurso.py          # Clase padre Recurso, y las hijas Equipo y Personal
│   ├── 📄 ambiente.py         # Clase Escenario/Auditorio
│   └── 📄 reserva.py          # Clase que une todo
│
├── 📁 services/               # (El CONTROLADOR: la lógica y reglas)
│   ├── 📄 gestor_reservas.py  # Calcula IGV, maneja los 3 minutos de bloqueo
│   └── 📄 tarificador.py      # Lógica matemática de cobros
│
├── 📁 views/                  # (La VISTA: la interfaz en terminal)
│   └── 📄 menu_consola.py     # Los prints, inputs y diseño del menú
│
└── 📁 database/               # (Capa de persistencia)
    ├── 📄 db_abstracta.py     # Clase abstracta BaseDeDatos
    ├── 📄 db_supabase.py      # Conexión real a la nube
    └── 📄 db_sqlite.py        # Conexión offline al USB
```
## 🚀 Instalación y Uso (Modo Local / USB)

Para ejecutar este proyecto en cualquier máquina con Windows sin necesidad de configurar entornos virtuales manualmente:

1. Clona este repositorio:
   ```bash
   git clone [https://github.com/tu_usuario/EventResourceManager.git](https://github.com/tu_usuario/EventResourceManager.git)

2. Ejecuta el archivo `1_Instalar_Requisitos.bat` para instalar las librerías necesarias (como Supabase).

3. Ejecuta el archivo `2_Iniciar_Sistema.bat` para levantar la interfaz en consola.

4. En el menú de inicio, selecciona tu entorno:

* `[1]` Nube (Supabase - Requiere Internet)

* `[2]` Local (SQLite - Modo Offline)

* `[3]` Restaurar BD Local (Limpiar datos)
## 🧑‍💻 Autor
* Adrian Jose Felix Ramirez Rivera `Restring17` - Estudiante de Ingeniería de Sistemas y Software.
