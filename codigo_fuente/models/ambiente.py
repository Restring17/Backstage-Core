"""
Módulo de Ambientes: Define la clase Ambiente (Escenario/Auditorio)
Empresa: Backstage-Core
"""

from datetime import datetime
from enum import Enum


class EstadoAmbiente(Enum):
    """Estados posibles de un ambiente"""
    ACTIVO = "ACTIVO"
    MANTENIMIENTO = "MANTENIMIENTO"
    RESERVADO = "RESERVADO"
    BLOQUEADO = "BLOQUEADO"


class Ambiente:
    """
    Representa un ambiente o escenario donde se realizan los eventos.
    """

    def __init__(
        self,
        id_ambiente: str,
        nombre: str,
        capacidad_personas: int,
        precio_alquiler_hora: float,
        requiere_sonido: bool = True,
        requiere_luces: bool = True,
        requiere_andamios: bool = False,
    ):
        """
        Inicializa un ambiente.

        Args:
            id_ambiente: Identificador único del ambiente
            nombre: Nombre del escenario
            capacidad_personas: Capacidad máxima de espectadores
            precio_alquiler_hora: Costo de alquiler por hora
            requiere_sonido: Si necesita sistema de sonido
            requiere_luces: Si necesita sistema de iluminación
            requiere_andamios: Si necesita estructura de andamios
        """
        self._id_ambiente = id_ambiente
        self._nombre = nombre
        self._capacidad_personas = capacidad_personas
        self._precio_alquiler_hora = precio_alquiler_hora
        self._requiere_sonido = requiere_sonido
        self._requiere_luces = requiere_luces
        self._requiere_andamios = requiere_andamios
        self._estado = EstadoAmbiente.ACTIVO
        self._bloques_ocupados = []  # Lista de tuplas (hora_inicio, hora_fin, id_reserva)
        self._equipos_asignados = []  # Lista de IDs de equipos
        self._personal_asignado = []  # Lista de IDs de personal
        self._fecha_creacion = datetime.now()

    # ===== PROPIEDADES (Getters) =====
    @property
    def id_ambiente(self) -> str:
        return self._id_ambiente

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def capacidad_personas(self) -> int:
        return self._capacidad_personas

    @property
    def precio_alquiler_hora(self) -> float:
        return self._precio_alquiler_hora

    @property
    def estado(self) -> EstadoAmbiente:
        return self._estado

    @property
    def bloques_ocupados(self) -> list:
        return self._bloques_ocupados.copy()

    @property
    def equipos_asignados(self) -> list:
        return self._equipos_asignados.copy()

    @property
    def personal_asignado(self) -> list:
        return self._personal_asignado.copy()

    # ===== MÉTODOS DE GESTIÓN =====
    def verificar_disponibilidad(self, hora_inicio: datetime, hora_fin: datetime) -> bool:
        """
        Verifica si el ambiente está disponible en un bloque horario.

        Args:
            hora_inicio: Hora de inicio del bloque a verificar
            hora_fin: Hora de fin del bloque a verificar

        Returns:
            True si está disponible, False si hay conflicto
        """
        if self._estado != EstadoAmbiente.ACTIVO:
            return False

        for ocupado_inicio, ocupado_fin, _ in self._bloques_ocupados:
            # Verifica si hay solapamiento
            if not (hora_fin <= ocupado_inicio or hora_inicio >= ocupado_fin):
                return False

        return True

    def bloquear_ambiente(
        self,
        hora_inicio: datetime,
        hora_fin: datetime,
        id_reserva: str,
    ) -> bool:
        """
        Bloquea el ambiente para una reserva específica.

        Args:
            hora_inicio: Hora de inicio del bloqueo
            hora_fin: Hora de fin del bloqueo
            id_reserva: ID de la reserva asociada

        Returns:
            True si se bloqueó exitosamente, False si hay conflicto
        """
        if self.verificar_disponibilidad(hora_inicio, hora_fin):
            self._bloques_ocupados.append((hora_inicio, hora_fin, id_reserva))
            self._estado = EstadoAmbiente.RESERVADO
            return True
        return False

    def liberar_bloque(self, id_reserva: str) -> bool:
        """
        Libera un bloque horario específico.

        Args:
            id_reserva: ID de la reserva a liberar

        Returns:
            True si se liberó exitosamente, False si no existe
        """
        self._bloques_ocupados = [b for b in self._bloques_ocupados if b[2] != id_reserva]
        if not self._bloques_ocupados:
            self._estado = EstadoAmbiente.ACTIVO
        return True

    def asignar_equipo(self, id_equipo: str) -> None:
        """
        Asigna un equipo al ambiente.

        Args:
            id_equipo: ID del equipo a asignar
        """
        if id_equipo not in self._equipos_asignados:
            self._equipos_asignados.append(id_equipo)

    def asignar_personal(self, id_personal: str) -> None:
        """
        Asigna personal técnico al ambiente.

        Args:
            id_personal: ID del personal a asignar
        """
        if id_personal not in self._personal_asignado:
            self._personal_asignado.append(id_personal)

    def limpiar_asignaciones(self) -> None:
        """Limpia las asignaciones de equipos y personal."""
        self._equipos_asignados = []
        self._personal_asignado = []

    def enviar_a_mantenimiento(self) -> None:
        """Marca el ambiente como en mantenimiento."""
        self._estado = EstadoAmbiente.MANTENIMIENTO

    def reactivar(self) -> None:
        """Reactiva el ambiente."""
        if not self._bloques_ocupados:
            self._estado = EstadoAmbiente.ACTIVO

    # ===== MÉTODOS DE INFORMACIÓN =====
    def generar_hoja_trabajo(self) -> dict:
        """
        Genera una hoja de trabajo con los requerimientos del ambiente.

        Returns:
            Diccionario con información de setup técnico
        """
        return {
            "id_ambiente": self._id_ambiente,
            "nombre": self._nombre,
            "capacidad": self._capacidad_personas,
            "requiere_sonido": self._requiere_sonido,
            "requiere_luces": self._requiere_luces,
            "requiere_andamios": self._requiere_andamios,
            "equipos_asignados": self._equipos_asignados,
            "personal_asignado": self._personal_asignado,
        }

    def __repr__(self) -> str:
        return (
            f"Ambiente("
            f"id={self._id_ambiente}, "
            f"nombre={self._nombre}, "
            f"capacidad={self._capacidad_personas}, "
            f"estado={self._estado.value})"
        )
