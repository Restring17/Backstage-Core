"""
Módulo Gestor de Reservas: Orquestación de validaciones y control de transacciones
Empresa: Backstage-Core
"""

from datetime import datetime, timedelta
from typing import List, Optional, TYPE_CHECKING
from models.reserva import ReservaEscenario, EstadoReserva
from models.recurso import Recurso
from models.ambiente import Ambiente
from services.tarificador import Tarificador

if TYPE_CHECKING:
    from database.db_abstracta import BaseDatos


class GestorReservas:
    """
    Servicio principal que orquesta todas las operaciones de reserva.
    Maneja validaciones, confirmaciones y rollbacks.
    """

    def __init__(self, tarificador: Optional[Tarificador] = None, base_datos=None):
        self._tarificador = tarificador or Tarificador()
        self._base_datos = base_datos  # referencia opcional a la BD para persistencia
        self._reservas_activas: dict[str, ReservaEscenario] = {}
        self._reservas_historial: List[ReservaEscenario] = []
        self._contador_reservas = 0

    # ===== MÉTODOS DE CREACIÓN DE RESERVAS =====
    def crear_reserva(
        self,
        ambiente: Ambiente,
        nombre_banda: str,
        manager_contacto: str,
        hora_inicio: datetime,
        hora_fin: datetime,
        recursos_solicitados: List[Recurso],
    ) -> Optional[ReservaEscenario]:
        """
        Crea una nueva reserva en estado PENDIENTE_PAGO.

        Args:
            ambiente: Ambiente donde se realizará el evento
            nombre_banda: Nombre de la banda/artista
            manager_contacto: Contacto del manager
            hora_inicio: Hora de inicio
            hora_fin: Hora de fin
            recursos_solicitados: Lista de recursos solicitados

        Returns:
            ReservaEscenario si se creó exitosamente, None si hay error
        """
        # Genera ID único
        self._contador_reservas += 1
        id_reserva = f"RES-{datetime.now().strftime('%Y%m%d')}-{self._contador_reservas:04d}"

        # Crea la reserva
        reserva = ReservaEscenario(
            id_reserva=id_reserva,
            ambiente=ambiente,
            nombre_banda=nombre_banda,
            manager_contacto=manager_contacto,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            recursos_solicitados=recursos_solicitados,
        )

        # Calcula el presupuesto
        duracion = (hora_fin - hora_inicio).total_seconds() / 3600
        desglose = self._tarificador.calcular_presupuesto_completo(
            ambiente.precio_alquiler_hora,
            duracion,
            recursos_solicitados,
        )
        reserva._monto_total_sin_igv = desglose["subtotal_sin_igv"]
        reserva._monto_igv = desglose["igv"]
        reserva._monto_total_con_igv = desglose["total_con_igv"]

        # Guarda en activas
        self._reservas_activas[id_reserva] = reserva

        return reserva

    # ===== MÉTODOS DE VALIDACIÓN =====
    def validar_reserva(self, id_reserva: str) -> tuple[bool, str]:
        """
        Valida si una reserva PENDIENTE_PAGO puede confirmarse.

        Args:
            id_reserva: ID de la reserva a validar

        Returns:
            Tupla (es_valida, mensaje)
        """
        if id_reserva not in self._reservas_activas:
            return False, f"Reserva {id_reserva} no encontrada"

        reserva = self._reservas_activas[id_reserva]

        # Verifica timeout automático
        if reserva.aplicar_timeout():
            del self._reservas_activas[id_reserva]
            self._reservas_historial.append(reserva)
            return False, "Reserva expirada por timeout (3 minutos)"

        # Valida la reserva
        return reserva.validar_reserva()

    def validar_horario_ambiente(
        self,
        ambiente: Ambiente,
        hora_inicio: datetime,
        hora_fin: datetime,
        excluir_reserva_id: Optional[str] = None,
    ) -> bool:
        """
        Verifica si un ambiente está disponible en un horario (sin contar reservas propias).

        Args:
            ambiente: Ambiente a verificar
            hora_inicio: Hora de inicio
            hora_fin: Hora de fin
            excluir_reserva_id: ID de reserva propia a excluir de la validación

        Returns:
            True si está disponible, False si hay conflicto
        """
        return ambiente.verificar_disponibilidad(hora_inicio, hora_fin)

    def validar_recurso_disponible(
        self,
        recurso: Recurso,
        hora_inicio: datetime,
        hora_fin: datetime,
    ) -> bool:
        """
        Verifica si un recurso está disponible en un horario.

        Args:
            recurso: Recurso a verificar
            hora_inicio: Hora de inicio
            hora_fin: Hora de fin

        Returns:
            True si está disponible, False si hay conflicto
        """
        return recurso.verificar_disponibilidad(hora_inicio, hora_fin)

    # ===== MÉTODOS DE CONFIRMACIÓN =====
    def confirmar_pago_reserva(self, id_reserva: str, monto_pagado: float) -> bool:
        """
        Confirma el pago de una reserva pendiente.

        Args:
            id_reserva: ID de la reserva
            monto_pagado: Monto que el cliente pagó

        Returns:
            True si se confirmó, False si hay error
        """
        if id_reserva not in self._reservas_activas:
            print(f"❌ Reserva {id_reserva} no encontrada")
            return False

        reserva = self._reservas_activas[id_reserva]

        # Verifica timeout nuevamente
        if reserva.aplicar_timeout():
            del self._reservas_activas[id_reserva]
            self._reservas_historial.append(reserva)
            return False

        # Intenta confirmar
        if not reserva.confirmar_reserva(monto_pagado):
            print(f"❌ Error al confirmar pago de {id_reserva}")
            return False

        print(f"✅ Reserva {id_reserva} confirmada exitosamente")
        return True

    # ===== MÉTODOS DE CANCELACIÓN =====
    def cancelar_reserva(self, id_reserva: str, razon: str = "Cliente solicitó") -> tuple[bool, str]:
        """
        Cancela una reserva aplicando penalidades si ya estaba confirmada (rollback automático).

        Args:
            id_reserva: ID de la reserva
            razon: Razón de la cancelación

        Returns:
            Tupla (Éxito de la operación, Mensaje resultante)
        """
        if id_reserva not in self._reservas_activas:
            return False, f"Reserva {id_reserva} no encontrada."

        reserva = self._reservas_activas[id_reserva]

        # 1. Penalidad si la reserva ya estaba confirmada
        if reserva.estado == EstadoReserva.CONFIRMADA:
            dias_faltantes = (reserva.hora_inicio.date() - datetime.now().date()).days
            monto_penalidad, porcentaje = self._tarificador.calcular_penalidad(
                reserva.monto_total_con_igv, dias_faltantes
            )
            factura_penalidad = self._tarificador.generar_factura_penalidad(
                id_reserva, reserva.nombre_banda, monto_penalidad, porcentaje
            )
            print(factura_penalidad)
            mensaje = f"✅ Reserva cancelada. Penalidad aplicada: {porcentaje*100}% (S/. {monto_penalidad:.2f}). Razón: {razon}"

            # persiste penalidad y estado en BD
            if self._base_datos:
                self._base_datos.actualizar_reserva(id_reserva, {
                    "estado":                EstadoReserva.CANCELADA.value,
                    "monto_penalidad":       monto_penalidad,
                    "porcentaje_penalidad":  porcentaje,
                    "razon_cancelacion":     razon,
                    "fecha_cancelacion":     datetime.now().isoformat(),
                })
                self._base_datos.registrar_movimiento_caja({
                    "id_reserva":  id_reserva,
                    "tipo":        "PENALIDAD",
                    "monto":       monto_penalidad,
                    "descripcion": f"Penalidad {porcentaje*100}% - {reserva.nombre_banda} - {razon}",
                })
        else:
            mensaje = f"✅ Reserva pendiente cancelada sin penalidades. Razón: {razon}"
            if self._base_datos:
                self._base_datos.actualizar_reserva(id_reserva, {
                    "estado":            EstadoReserva.CANCELADA.value,
                    "razon_cancelacion": razon,
                    "fecha_cancelacion": datetime.now().isoformat(),
                })
                # auditória de reservas caídas sin pago (monto 0)
                self._base_datos.registrar_movimiento_caja({
                    "id_reserva":  id_reserva,
                    "tipo":        "TIMEOUT",
                    "monto":       0,
                    "descripcion": f"Reserva cancelada sin pago - {reserva.nombre_banda} - {razon}",
                })

        # 2. Rollback en los recursos (libera fechas)
        if not reserva.cancelar_reserva():
            return False, "Error al ejecutar el rollback en los recursos."

        # 3. Mueve al historial
        del self._reservas_activas[id_reserva]
        self._reservas_historial.append(reserva)

        print(mensaje)
        return True, mensaje

    # ===== MÉTODOS DE CONSULTA =====
    def obtener_reserva(self, id_reserva: str) -> Optional[ReservaEscenario]:
        """Obtiene una reserva activa por su ID."""
        return self._reservas_activas.get(id_reserva)

    def obtener_reservas_activas(self) -> List[ReservaEscenario]:
        """Retorna todas las reservas activas."""
        return list(self._reservas_activas.values())

    def obtener_reservas_por_estado(self, estado: EstadoReserva) -> List[ReservaEscenario]:
        """Retorna todas las reservas en un estado específico."""
        return [r for r in self._reservas_activas.values() if r.estado == estado]

    def obtener_reservas_por_ambiente(self, id_ambiente: str) -> List[ReservaEscenario]:
        """Retorna todas las reservas de un ambiente específico."""
        return [
            r
            for r in self._reservas_activas.values()
            if r.ambiente.id_ambiente == id_ambiente
        ]

    def obtener_historial_completo(self) -> List[ReservaEscenario]:
        """Retorna el historial completo de reservas (activas + completadas/canceladas)."""
        return list(self._reservas_activas.values()) + self._reservas_historial

    # ===== MÉTODOS DE REPORTING =====
    def generar_reporte_ocupacion_ambiente(self, id_ambiente: str) -> dict:
        """
        Genera un reporte de ocupación de un ambiente.

        Args:
            id_ambiente: ID del ambiente

        Returns:
            Diccionario con información de ocupación
        """
        reservas_ambiente = self.obtener_reservas_por_ambiente(id_ambiente)

        return {
            "id_ambiente": id_ambiente,
            "total_reservas_activas": len(
                [r for r in reservas_ambiente if r.estado == EstadoReserva.CONFIRMADA]
            ),
            "total_pendientes_pago": len(
                [r for r in reservas_ambiente if r.estado == EstadoReserva.PENDIENTE_PAGO]
            ),
            "ingresos_potenciales": sum(
                r.monto_total_con_igv
                for r in reservas_ambiente
                if r.estado == EstadoReserva.CONFIRMADA
            ),
            "cronograma": [
                {
                    "banda": r.nombre_banda,
                    "hora_inicio": r.hora_inicio.strftime("%H:%M"),
                    "hora_fin": r.hora_fin.strftime("%H:%M"),
                    "estado": r.estado.value,
                }
                for r in sorted(
                    reservas_ambiente, key=lambda x: x.hora_inicio
                )
            ],
        }

    def generar_reporte_ingresos(self) -> dict:
        """
        Genera un reporte de ingresos totales del sistema.

        Returns:
            Diccionario con información de ingresos
        """
        reservas_confirmadas = self.obtener_reservas_por_estado(EstadoReserva.CONFIRMADA)

        total_sin_igv = sum(r.monto_sin_igv for r in reservas_confirmadas)
        total_igv = sum(r.monto_igv for r in reservas_confirmadas)
        total_con_igv = sum(r.monto_total_con_igv for r in reservas_confirmadas)

        return {
            "total_reservas_confirmadas": len(reservas_confirmadas),
            "subtotal_sin_igv": round(total_sin_igv, 2),
            "total_igv_18": round(total_igv, 2),
            "total_con_igv": round(total_con_igv, 2),
            "promedio_por_reserva": (
                round(total_con_igv / len(reservas_confirmadas), 2)
                if reservas_confirmadas
                else 0
            ),
        }

    def __repr__(self) -> str:
        return (
            f"GestorReservas("
            f"activas={len(self._reservas_activas)}, "
            f"historial={len(self._reservas_historial)})"
        )
