"""
Módulo de Base de Datos Abstracta: Define la interfaz para persistencia
Empresa: Backstage-Core
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BaseDatos(ABC):
    """
    Clase abstracta que define la interfaz para cualquier sistema de persistencia.
    Permite cambiar entre Supabase (nube) y SQLite (local) sin cambiar la lógica del negocio.
    Patrón: Repository Pattern
    """

    @abstractmethod
    def conectar(self) -> bool:
        """
        Establece la conexión con la base de datos.

        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        pass

    @abstractmethod
    def desconectar(self) -> bool:
        """
        Cierra la conexión con la base de datos.

        Returns:
            True si se desconectó correctamente
        """
        pass

    @abstractmethod
    def esta_conectado(self) -> bool:
        """
        Verifica el estado de la conexión.

        Returns:
            True si está conectado, False en caso contrario
        """
        pass

    # ===== OPERACIONES CRUD PARA RECURSOS =====
    @abstractmethod
    def guardar_recurso(self, recurso: Dict[str, Any]) -> bool:
        """
        Guarda un recurso en la BD.

        Args:
            recurso: Diccionario con datos del recurso

        Returns:
            True si se guardó exitosamente
        """
        pass

    @abstractmethod
    def obtener_recurso(self, id_recurso: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un recurso por ID.

        Args:
            id_recurso: ID del recurso

        Returns:
            Diccionario con datos del recurso, None si no existe
        """
        pass

    @abstractmethod
    def obtener_todos_recursos(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los recursos.

        Returns:
            Lista de diccionarios con datos de recursos
        """
        pass

    @abstractmethod
    def actualizar_recurso(self, id_recurso: str, datos: Dict[str, Any]) -> bool:
        """
        Actualiza un recurso.

        Args:
            id_recurso: ID del recurso
            datos: Diccionario con datos a actualizar

        Returns:
            True si se actualizó exitosamente
        """
        pass

    @abstractmethod
    def eliminar_recurso(self, id_recurso: str) -> bool:
        """
        Elimina un recurso.

        Args:
            id_recurso: ID del recurso

        Returns:
            True si se eliminó exitosamente
        """
        pass

    # ===== OPERACIONES CRUD PARA AMBIENTES =====
    @abstractmethod
    def guardar_ambiente(self, ambiente: Dict[str, Any]) -> bool:
        """Guarda un ambiente."""
        pass

    @abstractmethod
    def obtener_ambiente(self, id_ambiente: str) -> Optional[Dict[str, Any]]:
        """Obtiene un ambiente por ID."""
        pass

    @abstractmethod
    def obtener_todos_ambientes(self) -> List[Dict[str, Any]]:
        """Obtiene todos los ambientes."""
        pass

    @abstractmethod
    def actualizar_ambiente(self, id_ambiente: str, datos: Dict[str, Any]) -> bool:
        """Actualiza un ambiente."""
        pass

    @abstractmethod
    def eliminar_ambiente(self, id_ambiente: str) -> bool:
        """Elimina un ambiente."""
        pass

    # ===== OPERACIONES CRUD PARA RESERVAS =====
    @abstractmethod
    def guardar_reserva(self, reserva: Dict[str, Any]) -> bool:
        """Guarda una reserva."""
        pass

    @abstractmethod
    def obtener_reserva(self, id_reserva: str) -> Optional[Dict[str, Any]]:
        """Obtiene una reserva por ID."""
        pass

    @abstractmethod
    def obtener_todas_reservas(self) -> List[Dict[str, Any]]:
        """Obtiene todas las reservas."""
        pass

    @abstractmethod
    def obtener_reservas_por_estado(self, estado: str) -> List[Dict[str, Any]]:
        """Obtiene reservas filtradas por estado."""
        pass

    @abstractmethod
    def actualizar_reserva(self, id_reserva: str, datos: Dict[str, Any]) -> bool:
        """Actualiza una reserva."""
        pass

    @abstractmethod
    def eliminar_reserva(self, id_reserva: str) -> bool:
        """Elimina una reserva."""
        pass

    # ===== OPERACIONES DE TRANSACTION CONTROL =====
    @abstractmethod
    def iniciar_transaccion(self) -> bool:
        """Inicia una transacción de BD."""
        pass

    @abstractmethod
    def confirmar_transaccion(self) -> bool:
        """Confirma una transacción (COMMIT)."""
        pass

    @abstractmethod
    def revertir_transaccion(self) -> bool:
        """Revierte una transacción (ROLLBACK)."""
        pass

    # ===== OPERACIONES DE UTILIDAD =====
    @abstractmethod
    def limpiar_datos_test(self) -> bool:
        """
        Limpia todos los datos para modo de prueba.
        (Solo en SQLite, deshabilitado en Supabase por seguridad)

        Returns:
            True si se limpió exitosamente
        """
        pass

    @abstractmethod
    def obtener_informacion_conexion(self) -> Dict[str, str]:
        """
        Obtiene información sobre la conexión actual.

        Returns:
            Diccionario con datos de la conexión
        """
        pass
