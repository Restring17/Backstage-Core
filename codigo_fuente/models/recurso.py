"""
Módulo de Recursos: Define la clase abstracta Recurso y sus herencias.
Empresa: Backstage-Core
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


class EstadoDisponibilidad(Enum):
    """Estados posibles de un recurso"""
    LIBRE = "LIBRE"
    OCUPADO = "OCUPADO"
    PENDIENTE = "PENDIENTE"
    MANTENIMIENTO = "MANTENIMIENTO"
    CANCELADO = "CANCELADO"


class Recurso(ABC):
    """
    Clase abstracta que representa un recurso (equipo o personal).
    Base para EquipoFisico y PersonalTecnico.
    """

    def __init__(
        self,
        id_recurso: str,
        nombre: str,
        precio_base_hora: float,
        estado: EstadoDisponibilidad = EstadoDisponibilidad.LIBRE,
    ):
        """
        Inicializa un recurso.

        Args:
            id_recurso: Identificador único del recurso
            nombre: Nombre del recurso
            precio_base_hora: Costo base por hora en soles
            estado: Estado inicial de disponibilidad
        """
        self._id_recurso = id_recurso
        self._nombre = nombre
        self._precio_base_hora = precio_base_hora
        self._estado = estado
        self._bloques_horarios_ocupados = []  # Lista de tuplas (hora_inicio, hora_fin)
        self._fecha_creacion = datetime.now()

    # ===== PROPIEDADES (Getters) =====
    @property
    def id_recurso(self) -> str:
        return self._id_recurso

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio_base_hora(self) -> float:
        return self._precio_base_hora

    @property
    def estado(self) -> EstadoDisponibilidad:
        return self._estado

    @property
    def bloques_ocupados(self) -> list:
        return self._bloques_horarios_ocupados.copy()

    # ===== MÉTODOS DE ESTADO =====
    def marcar_en_uso(self, hora_inicio: datetime, hora_fin: datetime) -> None:
        """
        Marca el recurso como ocupado en un bloque horario específico.

        Args:
            hora_inicio: Hora de inicio del bloqueo
            hora_fin: Hora de fin del bloqueo
        """
        self._bloques_horarios_ocupados.append((hora_inicio, hora_fin))
        self._estado = EstadoDisponibilidad.OCUPADO

    def liberar(self) -> None:
        """Libera el recurso si no hay más bloques ocupados."""
        if not self._bloques_horarios_ocupados:
            self._estado = EstadoDisponibilidad.LIBRE
        else:
            self._estado = EstadoDisponibilidad.OCUPADO
    def remover_bloque_horario(self, hora_inicio: datetime, hora_fin: datetime) -> bool:
        """
        Remueve un bloque horario específico (usado en cancelaciones/rollback).

        Args:
            hora_inicio: Hora de inicio del bloque a remover
            hora_fin: Hora de fin del bloque a remover

        Returns:
            True si se removió exitosamente, False si no encontró el bloque
        """
        bloque_a_remover = (hora_inicio, hora_fin)
        if bloque_a_remover in self._bloques_horarios_ocupados:
            self._bloques_horarios_ocupados.remove(bloque_a_remover)
            self.liberar()
            return True
        return False
    def enviar_a_mantenimiento(self) -> tuple[bool, str]:
        """
        Marca el recurso como en mantenimiento, verificando antes que no esté en uso.
        
        Returns:
            tuple: (Éxito de la operación (bool), Mensaje descriptivo (str))
        """
        # Validamos si está ocupado o tiene bloques horarios programados en el futuro
        if self._estado == EstadoDisponibilidad.OCUPADO or len(self._bloques_horarios_ocupados) > 0:
            return False, f"Error: El recurso '{self._nombre}' tiene eventos programados y no puede retirarse."
        
        self._estado = EstadoDisponibilidad.MANTENIMIENTO
        return True, f"Éxito: El recurso '{self._nombre}' ha sido enviado a mantenimiento."
    
    def finalizar_mantenimiento(self) -> tuple[bool, str]:
        """
        Finaliza el mantenimiento y devuelve el recurso al catálogo disponible.
        """
        if self._estado != EstadoDisponibilidad.MANTENIMIENTO:
            return False, "Error: El recurso no se encuentra en mantenimiento."
            
        self._estado = EstadoDisponibilidad.LIBRE
        return True, f"Éxito: El recurso '{self._nombre}' vuelve a estar LIBRE y operativo."

    # ===== MÉTODOS ABSTRACTOS (deben implementarse en subclases) =====
    @abstractmethod
    def preparar_recurso(self) -> dict:
        """Prepara el recurso para su uso (implementación específica por tipo)."""
        pass

    @abstractmethod
    def obtener_tipo_recurso(self) -> str:
        """Retorna el tipo de recurso."""
        pass

    # ===== MÉTODO DE VALIDACIÓN =====
    def verificar_disponibilidad(self, hora_inicio: datetime, hora_fin: datetime) -> bool:
        """
        Verifica si el recurso está disponible en un bloque horario.

        Args:
            hora_inicio: Hora de inicio del bloque a verificar
            hora_fin: Hora de fin del bloque a verificar

        Returns:
            True si está disponible, False si hay conflicto
        """
        if self._estado == EstadoDisponibilidad.MANTENIMIENTO:
            return False

        for ocupado_inicio, ocupado_fin in self._bloques_horarios_ocupados:
            # Verifica si hay solapamiento
            if not (hora_fin <= ocupado_inicio or hora_inicio >= ocupado_fin):
                return False

        return True

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self._id_recurso}, "
            f"nombre={self._nombre}, "
            f"estado={self._estado.value})"
        )


class EquipoFisico(Recurso):
    """
    Representa un equipo físico (instrumento, consola, andamios).
    Hereda de Recurso.
    """

    def __init__(
        self,
        id_recurso: str,
        nombre: str,
        precio_base_hora: float,
        categoria: str,
        marca: str = "Genérico",
        requiere_conexion_electrica: bool = False,
        peso_kg: float = 0.0,
    ):
        """
        Inicializa un equipo físico.

        Args:
            id_recurso: ID único del equipo
            nombre: Nombre del equipo
            precio_base_hora: Costo base por hora
            categoria: Categoría (Instrumento, Iluminación, Andamiaje, etc.)
            marca: Marca del equipo
            requiere_conexion_electrica: Si necesita alimentación
            peso_kg: Peso del equipo en kg
        """
        super().__init__(id_recurso, nombre, precio_base_hora)
        self._categoria = categoria
        self._marca = marca
        self._requiere_conexion_electrica = requiere_conexion_electrica
        self._peso_kg = peso_kg

    @property
    def categoria(self) -> str:
        return self._categoria

    @property
    def marca(self) -> str:
        return self._marca

    @property
    def requiere_conexion_electrica(self) -> bool:
        return self._requiere_conexion_electrica

    @property
    def peso_kg(self) -> float:
        return self._peso_kg

    def preparar_recurso(self) -> dict:
        """Prepara el equipo para su uso (revisión técnica)."""
        return {
            "tipo_accion": "REVISION_TECNICA",
            "id_recurso": self._id_recurso,
            "nombre": self._nombre,
            "categoria": self._categoria,
            "requiere_electricidad": self._requiere_conexion_electrica,
            "peso_kg": self._peso_kg,
        }

    def obtener_tipo_recurso(self) -> str:
        return "EQUIPO_FISICO"

    def __repr__(self) -> str:
        return (
            f"EquipoFisico("
            f"id={self._id_recurso}, "
            f"nombre={self._nombre}, "
            f"categoria={self._categoria}, "
            f"marca={self._marca})"
        )


class PersonalTecnico(Recurso):
    """
    Representa un miembro del personal técnico (técnico de sonido, luces, etc.).
    Hereda de Recurso.
    """

    def __init__(
        self,
        id_recurso: str,
        nombre: str,
        precio_base_hora: float,
        especialidad: str,
        años_experiencia: int = 0,
        activo: bool = True,
    ):
        """
        Inicializa un personal técnico.

        Args:
            id_recurso: ID único del técnico
            nombre: Nombre completo
            precio_base_hora: Tarifa por hora en soles
            especialidad: Especialidad (Sonido, Luces, Estructuras, etc.)
            años_experiencia: Años de experiencia
            activo: Si está disponible para trabajar
        """
        super().__init__(id_recurso, nombre, precio_base_hora)
        self._especialidad = especialidad
        self._años_experiencia = años_experiencia
        self._activo = activo
        self._horas_extras_acumuladas = 0

    @property
    def especialidad(self) -> str:
        return self._especialidad

    @property
    def años_experiencia(self) -> int:
        return self._años_experiencia

    @property
    def activo(self) -> bool:
        return self._activo

    @property
    def horas_extras(self) -> int:
        return self._horas_extras_acumuladas

    def asignar_turno(self, duracion_horas: float) -> None:
        """
        Asigna un turno al técnico y calcula horas extras automáticamente.

        Args:
            duracion_horas: Duración del turno en horas
        """
        if duracion_horas > 8:
            self._horas_extras_acumuladas += (duracion_horas - 8)

    def preparar_recurso(self) -> dict:
        """Prepara el técnico para su asignación (notificación)."""
        return {
            "tipo_accion": "ASIGNACION_TURNO",
            "id_tecnico": self._id_recurso,
            "nombre": self._nombre,
            "especialidad": self._especialidad,
            "horas_extras": self._horas_extras_acumuladas,
        }

    def obtener_tipo_recurso(self) -> str:
        return "PERSONAL_TECNICO"
    
    def remover_bloque_horario(self, hora_inicio: datetime, hora_fin: datetime) -> None:
        """Remueve un bloque horario específico de la lista de ocupados."""
        self._bloques_horarios_ocupados = [
            (inicio, fin)
            for inicio, fin in self._bloques_horarios_ocupados
            if not (inicio == hora_inicio and fin == hora_fin)
        ]

    def inactivar(self) -> None:
        """Marca el técnico como inactivo (enfermedad, vacaciones, etc.)."""
        self._activo = False
        self._estado = EstadoDisponibilidad.MANTENIMIENTO

    def reactivar(self) -> None:
        """Reactiva el técnico."""
        self._activo = True
        self._estado = EstadoDisponibilidad.LIBRE

    def __repr__(self) -> str:
        return (
            f"PersonalTecnico("
            f"id={self._id_recurso}, "
            f"nombre={self._nombre}, "
            f"especialidad={self._especialidad}, "
            f"activo={self._activo})"
        )
