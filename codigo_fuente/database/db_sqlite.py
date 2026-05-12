"""
Módulo de Base de Datos SQLite: Implementación local (USB/Offline)
Empresa: Backstage-Core
"""

import sqlite3
import os
import json
from typing import List, Optional, Dict, Any
from .db_abstracta import BaseDatos


class DBSQLite(BaseDatos):
    """
    Implementación de persistencia usando SQLite (local).
    Ideal para ejecutar en USB blindado (modo offline).
    """

    def __init__(self, ruta_db: str = "backstage_core.db"):
        """
        Inicializa la conexión a SQLite.

        Args:
            ruta_db: Ruta del archivo de base de datos SQLite
        """
        self._ruta_db = ruta_db
        self._conexion: Optional[sqlite3.Connection] = None
        self._cursor: Optional[sqlite3.Cursor] = None
        self._conectado = False
        self._crear_tablas_si_no_existen()

    def _crear_tablas_si_no_existen(self) -> None:
        """Crea las tablas necesarias. Usa self._conexion si está abierta."""
        # si ya hay conexión activa (llamada desde conectar()), la usamos directamente
        if self._conexion:
            conn = self._conexion
            cursor = self._conexion.cursor()
            owns_conn = False
        else:
            # llamada desde __init__ antes de conectar() — solo para archivos .db
            if self._ruta_db == ":memory:":
                return  # no tiene sentido crear tablas en una conexión temporal de :memory:
            conn = sqlite3.connect(self._ruta_db)
            cursor = conn.cursor()
            owns_conn = True

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recursos (
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
                    datos_json TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ambientes (
                    id_ambiente TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    capacidad_personas INTEGER,
                    precio_alquiler_hora REAL NOT NULL,
                    estado TEXT NOT NULL,
                    requiere_sonido BOOLEAN,
                    requiere_luces BOOLEAN,
                    requiere_andamios BOOLEAN,
                    datos_json TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reservas (
                    id_reserva            TEXT PRIMARY KEY,
                    id_ambiente           TEXT NOT NULL,
                    nombre_banda          TEXT NOT NULL,
                    manager_contacto      TEXT,
                    hora_inicio           TIMESTAMP NOT NULL,
                    hora_fin              TIMESTAMP NOT NULL,
                    estado                TEXT NOT NULL,
                    monto_sin_igv         REAL,
                    monto_igv             REAL,
                    monto_total           REAL,
                    monto_penalidad       REAL DEFAULT 0,
                    porcentaje_penalidad  REAL DEFAULT 0,
                    razon_cancelacion     TEXT,
                    fecha_cancelacion     TIMESTAMP,
                    recursos_json         TEXT,
                    datos_json            TEXT,
                    fecha_creacion        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_ambiente) REFERENCES ambientes(id_ambiente)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movimientos_caja (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_reserva  TEXT REFERENCES reservas(id_reserva) ON DELETE SET NULL,
                    tipo        TEXT NOT NULL,
                    monto       REAL NOT NULL DEFAULT 0,
                    descripcion TEXT,
                    fecha       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            if owns_conn:
                conn.close()
        except Exception as e:
            print(f"❌ Error al crear tablas: {e}")

    def conectar(self) -> bool:
        """Establece conexión con SQLite."""
        try:
            self._conexion = sqlite3.connect(self._ruta_db)
            self._conexion.row_factory = sqlite3.Row
            self._cursor = self._conexion.cursor()
            self._conectado = True
            # asegura que las tablas existen en esta conexión
            self._crear_tablas_si_no_existen()
            print(f"✅ Conectado a SQLite (LOCAL): {self._ruta_db}")
            return True
        except Exception as e:
            print(f"❌ Error de conexión a SQLite: {e}")
            self._conectado = False
            return False

    def desconectar(self) -> bool:
        """Cierra la conexión con SQLite."""
        try:
            if self._conexion:
                self._conexion.close()
            self._conectado = False
            print("✅ Desconectado de SQLite")
            return True
        except Exception as e:
            print(f"❌ Error al desconectar: {e}")
            return False

    def esta_conectado(self) -> bool:
        """Verifica si está conectado."""
        return self._conectado

    # ===== RECURSOS =====
    def guardar_recurso(self, recurso: Dict[str, Any]) -> bool:
        """Guarda un recurso."""
        if not self._conectado or not self._cursor:
            return False

        try:
            self._cursor.execute("""
                INSERT OR REPLACE INTO recursos 
                (id_recurso, nombre, tipo, precio_base_hora, estado, datos_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                recurso.get("id_recurso"),
                recurso.get("nombre"),
                recurso.get("tipo"),
                recurso.get("precio_base_hora", 0),
                recurso.get("estado", "LIBRE"),
                json.dumps(recurso),
            ))
            self._conexion.commit()
            print(f"✅ Recurso {recurso.get('id_recurso')} guardado en SQLite")
            return True
        except Exception as e:
            print(f"❌ Error al guardar recurso: {e}")
            return False

    def obtener_recurso(self, id_recurso: str) -> Optional[Dict[str, Any]]:
        """Obtiene un recurso."""
        if not self._conectado or not self._cursor:
            return None

        try:
            self._cursor.execute("SELECT datos_json FROM recursos WHERE id_recurso = ?", (id_recurso,))
            row = self._cursor.fetchone()
            return json.loads(row[0]) if row else None
        except Exception:
            return None

    def obtener_todos_recursos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los recursos."""
        if not self._conectado or not self._cursor:
            return []

        try:
            self._cursor.execute("SELECT datos_json FROM recursos")
            return [json.loads(row[0]) for row in self._cursor.fetchall()]
        except Exception:
            return []

    def actualizar_recurso(self, id_recurso: str, datos: Dict[str, Any]) -> bool:
        """Actualiza un recurso."""
        if not self._conectado or not self._cursor:
            return False

        try:
            datos_json = json.dumps(datos)
            self._cursor.execute("""
                UPDATE recursos SET datos_json = ? WHERE id_recurso = ?
            """, (datos_json, id_recurso))
            self._conexion.commit()
            print(f"✅ Recurso {id_recurso} actualizado en SQLite")
            return True
        except Exception:
            return False

    def eliminar_recurso(self, id_recurso: str) -> bool:
        """Elimina un recurso."""
        if not self._conectado or not self._cursor:
            return False

        try:
            self._cursor.execute("DELETE FROM recursos WHERE id_recurso = ?", (id_recurso,))
            self._conexion.commit()
            print(f"✅ Recurso {id_recurso} eliminado de SQLite")
            return True
        except Exception:
            return False

    # ===== AMBIENTES =====
    def guardar_ambiente(self, ambiente: Dict[str, Any]) -> bool:
        """Guarda un ambiente."""
        if not self._conectado or not self._cursor:
            return False

        try:
            self._cursor.execute("""
                INSERT OR REPLACE INTO ambientes
                (id_ambiente, nombre, capacidad_personas, precio_alquiler_hora, estado, datos_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                ambiente.get("id_ambiente"),
                ambiente.get("nombre"),
                ambiente.get("capacidad_personas", 100),
                ambiente.get("precio_alquiler_hora", 0),
                ambiente.get("estado", "ACTIVO"),
                json.dumps(ambiente),
            ))
            self._conexion.commit()
            print(f"✅ Ambiente {ambiente.get('id_ambiente')} guardado en SQLite")
            return True
        except Exception:
            return False

    def obtener_ambiente(self, id_ambiente: str) -> Optional[Dict[str, Any]]:
        """Obtiene un ambiente."""
        if not self._conectado or not self._cursor:
            return None

        try:
            self._cursor.execute("SELECT datos_json FROM ambientes WHERE id_ambiente = ?", (id_ambiente,))
            row = self._cursor.fetchone()
            return json.loads(row[0]) if row else None
        except Exception:
            return None

    def obtener_todos_ambientes(self) -> List[Dict[str, Any]]:
        """Obtiene todos los ambientes."""
        if not self._conectado or not self._cursor:
            return []

        try:
            self._cursor.execute("SELECT datos_json FROM ambientes")
            return [json.loads(row[0]) for row in self._cursor.fetchall()]
        except Exception:
            return []

    def actualizar_ambiente(self, id_ambiente: str, datos: Dict[str, Any]) -> bool:
        """Actualiza un ambiente."""
        if not self._conectado or not self._cursor:
            return False

        try:
            datos_json = json.dumps(datos)
            self._cursor.execute("UPDATE ambientes SET datos_json = ? WHERE id_ambiente = ?", (datos_json, id_ambiente))
            self._conexion.commit()
            print(f"✅ Ambiente {id_ambiente} actualizado en SQLite")
            return True
        except Exception:
            return False

    def eliminar_ambiente(self, id_ambiente: str) -> bool:
        """Elimina un ambiente."""
        if not self._conectado or not self._cursor:
            return False

        try:
            self._cursor.execute("DELETE FROM ambientes WHERE id_ambiente = ?", (id_ambiente,))
            self._conexion.commit()
            print(f"✅ Ambiente {id_ambiente} eliminado de SQLite")
            return True
        except Exception:
            return False

    # ===== RESERVAS =====
    def guardar_reserva(self, reserva: Dict[str, Any]) -> bool:
        """Guarda una reserva."""
        if not self._conectado or not self._cursor:
            return False

        try:
            self._cursor.execute("""
                INSERT OR REPLACE INTO reservas
                (id_reserva, id_ambiente, nombre_banda, manager_contacto, 
                 hora_inicio, hora_fin, estado, monto_sin_igv, monto_igv, monto_total, datos_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                reserva.get("id_reserva"),
                reserva.get("id_ambiente"),
                reserva.get("nombre_banda"),
                reserva.get("manager_contacto"),
                reserva.get("hora_inicio"),
                reserva.get("hora_fin"),
                reserva.get("estado", "PENDIENTE_PAGO"),
                reserva.get("monto_sin_igv", 0),
                reserva.get("monto_igv", 0),
                reserva.get("monto_total", 0),
                json.dumps(reserva),
            ))
            self._conexion.commit()
            print(f"✅ Reserva {reserva.get('id_reserva')} guardada en SQLite")
            return True
        except Exception as e:
            print(f"❌ Error al guardar reserva: {e}")
            return False

    def obtener_reserva(self, id_reserva: str) -> Optional[Dict[str, Any]]:
        """Obtiene una reserva."""
        if not self._conectado or not self._cursor:
            return None

        try:
            self._cursor.execute("SELECT datos_json FROM reservas WHERE id_reserva = ?", (id_reserva,))
            row = self._cursor.fetchone()
            return json.loads(row[0]) if row else None
        except Exception:
            return None

    def obtener_todas_reservas(self) -> List[Dict[str, Any]]:
        """Obtiene todas las reservas."""
        if not self._conectado or not self._cursor:
            return []

        try:
            self._cursor.execute("SELECT datos_json FROM reservas ORDER BY fecha_creacion DESC")
            return [json.loads(row[0]) for row in self._cursor.fetchall()]
        except Exception:
            return []

    def obtener_reservas_por_estado(self, estado: str) -> List[Dict[str, Any]]:
        """Obtiene reservas por estado."""
        if not self._conectado or not self._cursor:
            return []

        try:
            self._cursor.execute("SELECT datos_json FROM reservas WHERE estado = ?", (estado,))
            return [json.loads(row[0]) for row in self._cursor.fetchall()]
        except Exception:
            return []

    def actualizar_reserva(self, id_reserva: str, datos: Dict[str, Any]) -> bool:
        """Actualiza una reserva."""
        if not self._conectado or not self._cursor:
            return False

        try:
            datos_json = json.dumps(datos)
            self._cursor.execute("UPDATE reservas SET datos_json = ? WHERE id_reserva = ?", (datos_json, id_reserva))
            self._conexion.commit()
            print(f"✅ Reserva {id_reserva} actualizada en SQLite")
            return True
        except Exception:
            return False

    def eliminar_reserva(self, id_reserva: str) -> bool:
        """Elimina una reserva."""
        if not self._conectado or not self._cursor:
            return False

        try:
            self._cursor.execute("DELETE FROM reservas WHERE id_reserva = ?", (id_reserva,))
            self._conexion.commit()
            print(f"✅ Reserva {id_reserva} eliminada de SQLite")
            return True
        except Exception:
            return False

    # ===== TRANSACCIONES =====
    def iniciar_transaccion(self) -> bool:
        """Inicia una transacción."""
        if not self._conectado or not self._cursor:
            return False
        try:
            self._cursor.execute("BEGIN TRANSACTION")
            print("✅ Transacción iniciada en SQLite")
            return True
        except Exception:
            return False

    def confirmar_transaccion(self) -> bool:
        """Confirma una transacción (COMMIT)."""
        if not self._conectado or not self._conexion:
            return False
        try:
            self._conexion.commit()
            print("✅ Transacción confirmada en SQLite")
            return True
        except Exception:
            return False

    def revertir_transaccion(self) -> bool:
        """Revierte una transacción (ROLLBACK)."""
        if not self._conectado or not self._conexion:
            return False
        try:
            self._conexion.rollback()
            print("✅ Transacción revertida en SQLite")
            return True
        except Exception:
            return False

    # ===== UTILIDAD =====
    def limpiar_datos_test(self) -> bool:
        """Limpia todos los datos (SOLO para modo test)."""
        if not self._conectado or not self._cursor:
            return False

        try:
            self._cursor.execute("DELETE FROM reservas")
            self._cursor.execute("DELETE FROM recursos")
            self._cursor.execute("DELETE FROM ambientes")
            self._conexion.commit()
            print("✅ Datos de test limpiados en SQLite")
            return True
        except Exception:
            return False

    def obtener_informacion_conexion(self) -> Dict[str, str]:
        """Obtiene información de la conexión."""
        return {
            "tipo": "SQLite (Local)",
            "archivo": os.path.abspath(self._ruta_db),
            "estado": "Conectado" if self._conectado else "Desconectado",
            "modo": "LOCAL - OFFLINE",
        }

    # ===== CAJA / AUDITORÍA FINANCIERA =====
    def registrar_movimiento_caja(self, datos: Dict[str, Any]) -> bool:
        """Inserta un movimiento en movimientos_caja."""
        if not self._conectado or not self._cursor:
            return False
        try:
            self._cursor.execute("""
                INSERT INTO movimientos_caja (id_reserva, tipo, monto, descripcion)
                VALUES (?, ?, ?, ?)
            """, (
                datos.get("id_reserva"),
                datos.get("tipo"),
                datos.get("monto", 0),
                datos.get("descripcion", ""),
            ))
            self._conexion.commit()
            return True
        except Exception as e:
            print(f"❌ Error al registrar movimiento de caja: {e}")
            return False

    def obtener_movimientos_caja(self) -> List[Dict[str, Any]]:
        """Devuelve el histórico completo de movimientos de caja."""
        if not self._conectado or not self._cursor:
            return []
        try:
            self._cursor.execute("""
                SELECT id, id_reserva, tipo, monto, descripcion, fecha
                FROM movimientos_caja
                ORDER BY fecha DESC
            """)
            cols = ["id", "id_reserva", "tipo", "monto", "descripcion", "fecha"]
            return [dict(zip(cols, row)) for row in self._cursor.fetchall()]
        except Exception as e:
            print(f"❌ Error al obtener movimientos de caja: {e}")
            return []

    def __repr__(self) -> str:
        return (
            f"DBSQLite("
            f"archivo={self._ruta_db}, "
            f"conectado={self._conectado})"
        )
