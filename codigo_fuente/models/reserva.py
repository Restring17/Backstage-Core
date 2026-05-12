"""
Módulo de Reservas: Define la clase ReservaEscenario (transaccional)
Empresa: Backstage-Core
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
from .recurso import Recurso
from .ambiente import Ambiente


class EstadoReserva(Enum):
    """Estados posibles de una reserva"""
    PENDIENTE_PAGO = "PENDIENTE_PAGO"  # Bloqueo de 3 minutos
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    COMPLETADA = "COMPLETADA"


class ReservaEscenario:
    """
    Reserva de escenario con todos sus recursos asociados.
    Maneja el ciclo de vida: pendiente → confirmada → completada / cancelada.
    """

    TIMEOUT_PAGO_HORAS = 24          # el cliente tiene 24h para pagar antes del rollback
    BUFFER_OPERATIVO_MINUTOS = 30     # tiempo de limpieza/desarme post-evento
    TASA_IGV = 0.18                   # IGV Perú

    def __init__(
        self,
        id_reserva: str,
        ambiente: Ambiente,
        nombre_banda: str,
        manager_contacto: str,
        hora_inicio: datetime,
        hora_fin: datetime,
        recursos_solicitados: List[Recurso],
    ):
        """
        Inicializa una reserva.

        Args:
            id_reserva: ID único de la reserva
            ambiente: Objeto Ambiente donde se realizará el evento
            nombre_banda: Nombre de la banda/artista
            manager_contacto: Contacto del manager (teléfono/email)
            hora_inicio: Hora de inicio del evento
            hora_fin: Hora de fin del evento
            recursos_solicitados: Lista de objetos Recurso (EquipoFisico, PersonalTecnico)
        """
        self._id_reserva = id_reserva
        self._ambiente = ambiente
        self._nombre_banda = nombre_banda
        self._manager_contacto = manager_contacto
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin

        # Calcula hora real de liberación (+ buffer)
        self._hora_liberacion_real = hora_fin + timedelta(minutes=self.BUFFER_OPERATIVO_MINUTOS)

        self._recursos_solicitados = recursos_solicitados
        self._estado = EstadoReserva.PENDIENTE_PAGO
        self._timestamp_creacion = datetime.now()
        self._timestamp_confirmacion: Optional[datetime] = None
        self._monto_total_sin_igv = 0.0
        self._monto_igv = 0.0
        self._monto_total_con_igv = 0.0

    # ===== PROPIEDADES (Getters) =====
    @property
    def id_reserva(self) -> str:
        return self._id_reserva

    @property
    def ambiente(self) -> Ambiente:
        return self._ambiente

    @property
    def nombre_banda(self) -> str:
        return self._nombre_banda

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def hora_inicio(self) -> datetime:
        return self._hora_inicio

    @property
    def hora_fin(self) -> datetime:
        return self._hora_fin

    @property
    def hora_liberacion_real(self) -> datetime:
        """Hora real en que se liberarán los recursos (+ buffer)"""
        return self._hora_liberacion_real

    @property
    def duracion_evento_horas(self) -> float:
        """Duración del evento en horas"""
        return (self._hora_fin - self._hora_inicio).total_seconds() / 3600

    @property
    def duracion_con_buffer_horas(self) -> float:
        """Duración total con buffer en horas"""
        return (self._hora_liberacion_real - self._hora_inicio).total_seconds() / 3600

    @property
    def recursos_asignados(self) -> List[Recurso]:
        return self._recursos_solicitados.copy()

    @property
    def monto_total_con_igv(self) -> float:
        return self._monto_total_con_igv

    @property
    def monto_sin_igv(self) -> float:
        return self._monto_total_sin_igv

    @property
    def monto_igv(self) -> float:
        return self._monto_igv

    @property
    def tiempo_bloqueado(self) -> int:
        """Horas que faltan para que expire el bloqueo de pago"""
        if self._estado != EstadoReserva.PENDIENTE_PAGO:
            return 0
        elapsed_hours = (datetime.now() - self._timestamp_creacion).total_seconds() / 3600
        remaining = self.TIMEOUT_PAGO_HORAS - elapsed_hours
        return max(0, int(remaining))

    # ===== MÉTODOS DE VALIDACIÓN =====
    def validar_reserva(self) -> tuple[bool, str]:
        """
        Valida si la reserva puede confirmarse.
        Verifica disponibilidad del ambiente y todos los recursos.

        Returns:
            Tupla (es_valida, mensaje_error)
        """
        # Valida disponibilidad del ambiente
        if not self._ambiente.verificar_disponibilidad(
            self._hora_inicio, self._hora_liberacion_real
        ):
            return False, f"Ambiente '{self._ambiente.nombre}' no disponible en ese horario"

        # Valida disponibilidad de todos los recursos
        for recurso in self._recursos_solicitados:
            if not recurso.verificar_disponibilidad(
                self._hora_inicio, self._hora_liberacion_real
            ):
                return (
                    False,
                    f"Recurso '{recurso.nombre}' no disponible en ese horario",
                )

        return True, "Reserva válida"

    # ===== MÉTODOS DE TRANSACCIÓN =====
    def confirmar_reserva(self, monto_a_pagar: float) -> bool:
        """
        Confirma la reserva (resuelve el bloqueo de 3 minutos).

        Args:
            monto_a_pagar: Monto que el cliente confirma pagar

        Returns:
            True si se confirmó, False si hay error
        """
        # Valida que se haya pagado lo correcto
        if abs(monto_a_pagar - self._monto_total_con_igv) > 0.01:
            print(
                f"❌ Error: Monto incorrecto. "
                f"Esperado: S/.{self._monto_total_con_igv:.2f}, "
                f"Recibido: S/.{monto_a_pagar:.2f}"
            )
            return False

        # Bloquea el ambiente
        if not self._ambiente.bloquear_ambiente(
            self._hora_inicio, self._hora_liberacion_real, self._id_reserva
        ):
            return False

        # Bloquea todos los recursos
        for recurso in self._recursos_solicitados:
            recurso.marcar_en_uso(self._hora_inicio, self._hora_liberacion_real)
            self._ambiente.asignar_equipo(recurso.id_recurso)

        self._estado = EstadoReserva.CONFIRMADA
        self._timestamp_confirmacion = datetime.now()
        return True

    def cancelar_reserva(self) -> bool:
        """
        Cancela la reserva (rollback automático).

        Returns:
            True si se canceló exitosamente
        """
        if self._estado == EstadoReserva.CONFIRMADA:
            # Libera el ambiente
            self._ambiente.liberar_bloque(self._id_reserva)

            # Libera todos los recursos
            for recurso in self._recursos_solicitados:
                recurso.remover_bloque_horario(self._hora_inicio, self._hora_liberacion_real)
                recurso.liberar()

            self._ambiente.limpiar_asignaciones()

        self._estado = EstadoReserva.CANCELADA
        return True

    def aplicar_timeout(self) -> bool:
        """
        Aplica timeout si han pasado 24 horas sin confirmar pago (rollback).

        Returns:
            True si expiró, False si aún está válido
        """
        if self._estado != EstadoReserva.PENDIENTE_PAGO:
            return False

        elapsed_hours = (datetime.now() - self._timestamp_creacion).total_seconds() / 3600
        if elapsed_hours > self.TIMEOUT_PAGO_HORAS:
            print(f"⏰ Timeout: Reserva {self._id_reserva} expirada tras {self.TIMEOUT_PAGO_HORAS} horas. Rollback automático.")
            self.cancelar_reserva()
            return True

        return False

    # ===== MÉTODOS DE PRESUPUESTO =====
    def calcular_presupuesto_total(self) -> float:
        """
        Calcula el presupuesto total de la reserva incluido IGV.

        Returns:
            Monto total con IGV en soles
        """
        duracion = self.duracion_con_buffer_horas

        # Costo del ambiente
        costo_ambiente = self._ambiente.precio_alquiler_hora * duracion

        # Costo de recursos
        costo_recursos = sum(
            recurso.precio_base_hora * duracion for recurso in self._recursos_solicitados
        )

        # Total sin IGV
        self._monto_total_sin_igv = costo_ambiente + costo_recursos

        # Cálculo de IGV
        self._monto_igv = self._monto_total_sin_igv * self.TASA_IGV

        # Total con IGV
        self._monto_total_con_igv = self._monto_total_sin_igv + self._monto_igv

        return self._monto_total_con_igv

    def obtener_desglose_presupuesto(self) -> dict:
        """
        Obtiene el desglose detallado del presupuesto.

        Returns:
            Diccionario con detalles de costos
        """
        return {
            "ambiente": {
                "nombre": self._ambiente.nombre,
                "precio_hora": self._ambiente.precio_alquiler_hora,
                "horas": round(self.duracion_con_buffer_horas, 2),
                "subtotal": round(self._ambiente.precio_alquiler_hora * self.duracion_con_buffer_horas, 2),
            },
            "recursos": [
                {
                    "nombre": recurso.nombre,
                    "tipo": recurso.obtener_tipo_recurso(),
                    "precio_hora": recurso.precio_base_hora,
                    "horas": round(self.duracion_con_buffer_horas, 2),
                    "subtotal": round(
                        recurso.precio_base_hora * self.duracion_con_buffer_horas, 2
                    ),
                }
                for recurso in self._recursos_solicitados
            ],
            "subtotal_sin_igv": round(self._monto_total_sin_igv, 2),
            "igv_18_porciento": round(self._monto_igv, 2),
            "total_con_igv": round(self._monto_total_con_igv, 2),
        }

    # ===== MÉTODOS DE REPORTES =====
    def generar_hoja_trabajo(self) -> dict:
        """
        Genera la hoja de trabajo para el equipo técnico.

        Returns:
            Diccionario con información de setup
        """
        return {
            "id_reserva": self._id_reserva,
            "banda": self._nombre_banda,
            "ambiente": self._ambiente.generar_hoja_trabajo(),
            "hora_inicio": self._hora_inicio.strftime("%Y-%m-%d %H:%M"),
            "hora_fin": self._hora_fin.strftime("%Y-%m-%d %H:%M"),
            "hora_liberacion": self._hora_liberacion_real.strftime("%Y-%m-%d %H:%M"),
            "recursos": [
                {
                    "id": recurso.id_recurso,
                    "nombre": recurso.nombre,
                    "tipo": recurso.obtener_tipo_recurso(),
                }
                for recurso in self._recursos_solicitados
            ],
        }

    def __repr__(self) -> str:
        return (
            f"ReservaEscenario("
            f"id={self._id_reserva}, "
            f"banda={self._nombre_banda}, "
            f"estado={self._estado.value}, "
            f"total=S/.{self._monto_total_con_igv:.2f})"
        )
