"""
Base de datos Supabase — conexión a PostgreSQL en la nube.
Empresa: Backstage-Core
"""

import os
from typing import List, Optional, Dict, Any
from .db_abstracta import BaseDatos


class DBSupabase(BaseDatos):
    """
    Persistencia usando Supabase (PostgreSQL).
    Necesita SUPABASE_URL y SUPABASE_KEY en el .env antes de iniciar.
    """

    def __init__(self):
        """Inicializa la conexión a Supabase."""
        self._conectado = False
        self._supabase_url = os.getenv("SUPABASE_URL", "")
        self._supabase_key = os.getenv("SUPABASE_KEY", "")
        self._client = None

        if not self._supabase_url or not self._supabase_key:
            print("⚠️  Variables SUPABASE_URL y/o SUPABASE_KEY no configuradas.")
            print("   Copia .env.example como .env y añade tus credenciales.")
            return

        try:
            from supabase import create_client
            self._client = create_client(self._supabase_url, self._supabase_key)
        except ImportError:
            print("⚠️  El paquete 'supabase' no está instalado.")
            print("   Ejecuta: pip install supabase")

    def conectar(self) -> bool:
        """Prueba la conexión haciendo un SELECT rápido. Retorna True si responde."""
        if not self._client:
            print("❌ Error: Cliente de Supabase no inicializado.")
            print("   Revisa que SUPABASE_URL y SUPABASE_KEY estén configuradas en .env")
            return False

        try:
            self._client.table("ambientes").select("id_ambiente").limit(1).execute()
            self._conectado = True
            print("✅ Conectado a Supabase (NUBE)")
            return True
        except Exception as e:
            print(f"❌ Error de conexión a Supabase: {e}")
            print("   Verifica que el esquema SQL esté importado y las credenciales sean válidas.")
            self._conectado = False
            return False

    def desconectar(self) -> bool:
        """Cierra la conexión con Supabase."""
        self._conectado = False
        print("✅ Desconectado de Supabase")
        return True

    def esta_conectado(self) -> bool:
        """Verifica si está conectado a Supabase."""
        return self._conectado

    # ===== RECURSOS =====
    def guardar_recurso(self, recurso: Dict[str, Any]) -> bool:
        """Guarda un recurso en Supabase."""
        if not self._conectado:
            print("❌ No conectado a Supabase")
            return False

        try:
            self._client.table("recursos").upsert(recurso).execute()
            print(f"✅ Recurso {recurso.get('id_recurso')} guardado en Supabase")
            return True
        except Exception as e:
            print(f"❌ Error al guardar recurso: {e}")
            return False

    def obtener_recurso(self, id_recurso: str) -> Optional[Dict[str, Any]]:
        """Obtiene un recurso por ID."""
        if not self._conectado:
            return None

        try:
            response = self._client.table("recursos").select("*").eq("id_recurso", id_recurso).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error al obtener recurso: {e}")
            return None

    def obtener_todos_recursos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los recursos."""
        if not self._conectado:
            return []

        try:
            response = self._client.table("recursos").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Error al obtener recursos: {e}")
            return []

    def actualizar_recurso(self, id_recurso: str, datos: Dict[str, Any]) -> bool:
        """Actualiza un recurso."""
        if not self._conectado:
            return False

        try:
            self._client.table("recursos").update(datos).eq("id_recurso", id_recurso).execute()
            print(f"✅ Recurso {id_recurso} actualizado en Supabase")
            return True
        except Exception as e:
            print(f"❌ Error al actualizar recurso: {e}")
            return False

    def eliminar_recurso(self, id_recurso: str) -> bool:
        """Elimina un recurso."""
        if not self._conectado:
            return False

        try:
            self._client.table("recursos").delete().eq("id_recurso", id_recurso).execute()
            print(f"✅ Recurso {id_recurso} eliminado de Supabase")
            return True
        except Exception as e:
            print(f"❌ Error al eliminar recurso: {e}")
            return False

    # ===== AMBIENTES =====
    def guardar_ambiente(self, ambiente: Dict[str, Any]) -> bool:
        """Guarda un ambiente."""
        if not self._conectado:
            return False
        try:
            self._client.table("ambientes").upsert(ambiente).execute()
            print(f"✅ Ambiente {ambiente.get('id_ambiente')} guardado en Supabase")
            return True
        except Exception as e:
            print(f"❌ Error al guardar ambiente: {e}")
            return False

    def obtener_ambiente(self, id_ambiente: str) -> Optional[Dict[str, Any]]:
        """Obtiene un ambiente."""
        if not self._conectado:
            return None
        try:
            response = self._client.table("ambientes").select("*").eq("id_ambiente", id_ambiente).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error al obtener ambiente: {e}")
            return None

    def obtener_todos_ambientes(self) -> List[Dict[str, Any]]:
        """Obtiene todos los ambientes."""
        if not self._conectado:
            return []
        try:
            response = self._client.table("ambientes").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Error al obtener ambientes: {e}")
            return []

    def actualizar_ambiente(self, id_ambiente: str, datos: Dict[str, Any]) -> bool:
        """Actualiza un ambiente."""
        if not self._conectado:
            return False
        try:
            self._client.table("ambientes").update(datos).eq("id_ambiente", id_ambiente).execute()
            print(f"✅ Ambiente {id_ambiente} actualizado en Supabase")
            return True
        except Exception as e:
            print(f"❌ Error al actualizar ambiente: {e}")
            return False

    def eliminar_ambiente(self, id_ambiente: str) -> bool:
        """Elimina un ambiente."""
        if not self._conectado:
            return False
        try:
            self._client.table("ambientes").delete().eq("id_ambiente", id_ambiente).execute()
            print(f"✅ Ambiente {id_ambiente} eliminado de Supabase")
            return True
        except Exception as e:
            print(f"❌ Error al eliminar ambiente: {e}")
            return False

    # ===== RESERVAS =====
    def guardar_reserva(self, reserva: Dict[str, Any]) -> bool:
        """
        Llama al RPC guardar_reserva_con_recursos para guardar reserva y recursos juntos.
        Copia el dict recibido para no modificar el original.
        """
        if not self._conectado:
            return False
        try:
            reserva_data = dict(reserva)
            recursos_detalle = reserva_data.pop("recursos_detalle", [])

            # datetime → ISO string para que PostgreSQL lo acepte
            for campo_fecha in ("hora_inicio", "hora_fin"):
                if campo_fecha in reserva_data and hasattr(reserva_data[campo_fecha], "isoformat"):
                    reserva_data[campo_fecha] = reserva_data[campo_fecha].isoformat()

            self._client.rpc(
                "guardar_reserva_con_recursos",
                {
                    "p_reserva":  reserva_data,
                    "p_recursos": recursos_detalle,
                }
            ).execute()

            print(f"✅ Reserva {reserva_data.get('id_reserva')} guardada en Supabase")
            return True
        except Exception as e:
            print(f"❌ Error al guardar reserva: {e}")
            return False

    def obtener_reserva(self, id_reserva: str) -> Optional[Dict[str, Any]]:
        """Obtiene una reserva."""
        if not self._conectado:
            return None
        try:
            response = self._client.table("reservas").select("*").eq("id_reserva", id_reserva).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error al obtener reserva: {e}")
            return None

    def obtener_todas_reservas(self) -> List[Dict[str, Any]]:
        """Obtiene todas las reservas."""
        if not self._conectado:
            return []
        try:
            response = self._client.table("reservas").select("*").order("fecha_creacion", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Error al obtener reservas: {e}")
            return []

    def obtener_reservas_por_estado(self, estado: str) -> List[Dict[str, Any]]:
        """Obtiene reservas por estado."""
        if not self._conectado:
            return []
        try:
            response = self._client.table("reservas").select("*").eq("estado", estado).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Error al obtener reservas por estado: {e}")
            return []

    def actualizar_reserva(self, id_reserva: str, datos: Dict[str, Any]) -> bool:
        """Actualiza una reserva."""
        if not self._conectado:
            return False
        try:
            self._client.table("reservas").update(datos).eq("id_reserva", id_reserva).execute()
            print(f"✅ Reserva {id_reserva} actualizada en Supabase")
            return True
        except Exception as e:
            print(f"❌ Error al actualizar reserva: {e}")
            return False

    def eliminar_reserva(self, id_reserva: str) -> bool:
        """Elimina una reserva."""
        if not self._conectado:
            return False
        try:
            self._client.table("reservas").delete().eq("id_reserva", id_reserva).execute()
            print(f"✅ Reserva {id_reserva} eliminada de Supabase")
            return True
        except Exception as e:
            print(f"❌ Error al eliminar reserva: {e}")
            return False

    # ===== TRANSACCIONES =====
    # Supabase no expone BEGIN/COMMIT desde el cliente Python — cada operación es autocommit.
    # Los rollbacks reales van por funciones RPC en PostgreSQL (ver guardar_reserva_con_recursos).
    def iniciar_transaccion(self) -> bool:
        if not self._conectado:
            return False
        return True

    def confirmar_transaccion(self) -> bool:
        if not self._conectado:
            return False
        return True

    def revertir_transaccion(self) -> bool:
        # No hay forma de hacer ROLLBACK desde el SDK; el RPC de PostgreSQL lo maneja internamente.
        if not self._conectado:
            return False
        print("⚠️  Rollback no disponible desde el cliente. Revisa el estado en el panel de Supabase.")
        return False

    # ===== UTILIDAD =====
    def limpiar_datos_test(self) -> bool:
        # Deshabilitado en nube — borrar directo desde el panel de Supabase
        print("⚠️  Limpieza deshabilitada en modo nube. Usa el panel de Supabase.")
        return False

    # ===== CAJA / AUDITORÍA FINANCIERA =====
    def registrar_movimiento_caja(self, datos: Dict[str, Any]) -> bool:
        """Inserta un movimiento en movimientos_caja."""
        if not self._conectado:
            return False
        try:
            self._client.table("movimientos_caja").insert({
                "id_reserva":  datos.get("id_reserva"),
                "tipo":        datos.get("tipo"),
                "monto":       datos.get("monto", 0),
                "descripcion": datos.get("descripcion", ""),
            }).execute()
            return True
        except Exception as e:
            print(f"❌ Error al registrar movimiento de caja: {e}")
            return False

    def obtener_movimientos_caja(self) -> List[Dict[str, Any]]:
        """Devuelve el histórico completo de movimientos de caja."""
        if not self._conectado:
            return []
        try:
            response = (
                self._client.table("movimientos_caja")
                .select("*")
                .order("fecha", desc=True)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Error al obtener movimientos de caja: {e}")
            return []

    def obtener_informacion_conexion(self) -> Dict[str, str]:
        """Obtiene información de la conexión."""
        url_display = self._supabase_url if self._supabase_url else "(no configurada)"
        return {
            "tipo": "Supabase (PostgreSQL en la Nube)",
            "url": url_display,
            "estado": "Conectado ✅" if self._conectado else "Desconectado ❌",
            "modo": "NUBE - ONLINE",
        }

    def __repr__(self) -> str:
        return (
            f"DBSupabase("
            f"conectado={self._conectado}, "
            f"url={self._supabase_url})"
        )
