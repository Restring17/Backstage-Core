"""
Módulo de Tarificación: Cálculo de precios e IGV
Empresa: Backstage-Core
"""

from typing import List
from datetime import datetime, timedelta
from models.recurso import Recurso, EquipoFisico, PersonalTecnico


class Tarificador:
    """
    Servicio especializado en el cálculo de presupuestos dinámicos.
    Gestiona tarificación de equipos, personal y ambientes.
    """

    # Constantes
    TASA_IGV = 0.18  # 18% IGV en Perú
    BUFFER_MINUTOS = 30
    RECARGO_EQUIPOS_DELICADOS = 0.15  # 15% si requiere electricidad
    RECARGO_EXPERIENCIA_TECNICA = 0.10  # 10% por cada 5 años de experiencia

    def __init__(self):
        """Inicializa el tarificador."""
        self._historial_calculos = []

    # ===== MÉTODOS DE TARIFICACIÓN =====
    def calcular_costo_recurso(
        self,
        recurso: Recurso,
        duracion_horas: float,
        aplicar_recargos: bool = True,
    ) -> float:
        """
        Calcula el costo de un recurso específico con recargos aplicables.

        Args:
            recurso: Objeto Recurso (EquipoFisico o PersonalTecnico)
            duracion_horas: Duración del alquiler en horas
            aplicar_recargos: Si aplicar recargos automáticos

        Returns:
            Costo total en soles
        """
        costo_base = recurso.precio_base_hora * duracion_horas

        if not aplicar_recargos:
            return costo_base

        # Aplica recargos específicos según tipo de recurso
        if isinstance(recurso, EquipoFisico):
            if recurso.requiere_conexion_electrica:
                costo_base *= 1 + self.RECARGO_EQUIPOS_DELICADOS

        elif isinstance(recurso, PersonalTecnico):
            if recurso.años_experiencia > 0:
                # 10% por cada 5 años de experiencia
                recargo_experiencia = (recurso.años_experiencia // 5) * self.RECARGO_EXPERIENCIA_TECNICA
                costo_base *= 1 + recargo_experiencia

        return costo_base

    def calcular_presupuesto_completo(
        self,
        precio_ambiente_hora: float,
        duracion_evento_horas: float,
        recursos: List[Recurso],
    ) -> dict:
        """
        Calcula el presupuesto completo de una reserva.

        Args:
            precio_ambiente_hora: Precio del ambiente por hora
            duracion_evento_horas: Duración del evento en horas
            recursos: Lista de recursos solicitados

        Returns:
            Diccionario con desglose de costos
        """
        # Suma duración del buffer
        duracion_total_horas = duracion_evento_horas + (self.BUFFER_MINUTOS / 60)

        # Costo del ambiente
        costo_ambiente = precio_ambiente_hora * duracion_total_horas

        # Costos de recursos
        costos_recursos = {
            recurso.id_recurso: {
                "nombre": recurso.nombre,
                "tipo": recurso.obtener_tipo_recurso(),
                "precio_hora": recurso.precio_base_hora,
                "costo": self.calcular_costo_recurso(recurso, duracion_total_horas),
            }
            for recurso in recursos
        }

        # Totales
        subtotal = costo_ambiente + sum(r["costo"] for r in costos_recursos.values())
        igv = subtotal * self.TASA_IGV
        total = subtotal + igv

        desglose = {
            "ambiente": {
                "precio_hora": precio_ambiente_hora,
                "duracion_horas": round(duracion_total_horas, 2),
                "costo": round(costo_ambiente, 2),
            },
            "recursos": costos_recursos,
            "subtotal_sin_igv": round(subtotal, 2),
            "igv": round(igv, 2),
            "total_con_igv": round(total, 2),
        }

        # Registra en historial
        self._historial_calculos.append(
            {
                "timestamp": datetime.now(),
                "desglose": desglose,
            }
        )

        return desglose

    # ===== MÉTODOS DE VALIDACIÓN DE PRECIOS =====
    def validar_precio_recurso(self, recurso: Recurso, precio_esperado: float) -> bool:
        """
        Valida si el precio de un recurso es correcto (validación contra cambios maliciosos).

        Args:
            recurso: Objeto Recurso
            precio_esperado: Precio esperado

        Returns:
            True si es válido, False si hay discrepancia
        """
        tolerancia = 0.01  # 1 céntimo de tolerancia
        return abs(recurso.precio_base_hora - precio_esperado) <= tolerancia

    # ===== MÉTODOS DE REPORTE =====
    def obtener_historial_calculos(self) -> list:
        """Retorna el historial de cálculos realizados."""
        return self._historial_calculos.copy()

    def obtener_promedio_presupuestos(self) -> float:
        """
        Calcula el promedio de presupuestos realizados.

        Returns:
            Promedio en soles
        """
        if not self._historial_calculos:
            return 0.0

        totales = [calc["desglose"]["total_con_igv"] for calc in self._historial_calculos]
        return sum(totales) / len(totales)

    def generar_factura(
        self,
        id_reserva: str,
        nombre_cliente: str,
        desglose: dict,
    ) -> str:
        """
        Genera una factura en formato texto.

        Args:
            id_reserva: ID de la reserva
            nombre_cliente: Nombre del cliente (banda)
            desglose: Diccionario con desglose de presupuesto

        Returns:
            String con la factura formateada
        """
        factura = f"""
╔════════════════════════════════════════════════════════════════╗
║             FACTURA BACKSTAGE-CORE                             ║
║        Sistema de Recursos para Eventos Musicales             ║
╚════════════════════════════════════════════════════════════════╝

REFERENCIA: {id_reserva}
CLIENTE: {nombre_cliente}
FECHA: {datetime.now().strftime("%d/%m/%Y %H:%M")}

────────────────────────────────────────────────────────────────

DESGLOSE DE COSTOS:

Ambiente:
  • Precio/hora: S/.{desglose['ambiente']['precio_hora']:.2f}
  • Horas (con buffer): {desglose['ambiente']['horas']}
  • Subtotal: S/.{desglose['ambiente']['subtotal']:.2f}

Recursos:
"""
        for recurso in desglose["recursos"]:
            factura += (
                f"  • {recurso['nombre']} ({recurso['tipo']})\n"
                f"    Precio/hora: S/.{recurso['precio_hora']:.2f}\n"
                f"    Subtotal: S/.{recurso['subtotal']:.2f}\n"
            )

        factura += f"""
────────────────────────────────────────────────────────────────

SUBTOTAL (sin IGV):           S/.{desglose['subtotal_sin_igv']:>10.2f}
IGV 18%:                      S/.{desglose['igv_18_porciento']:>10.2f}
────────────────────────────────────────────────────────────────
TOTAL A PAGAR:                S/.{desglose['total_con_igv']:>10.2f}

════════════════════════════════════════════════════════════════
"""
        return factura

    # ===== MÉTODOS DE PENALIDAD POR CANCELACIÓN =====
    def calcular_penalidad(self, monto_total: float, dias_faltantes: int) -> tuple[float, float]:
        """
        Calcula la penalidad corporativa por cancelación de último minuto.
        
        Args:
            monto_total: Monto total de la reserva confirmada
            dias_faltantes: Días restantes para el evento
            
        Returns:
            Tupla con (monto_penalidad, porcentaje_aplicado)
        """
        if dias_faltantes <= 14:
            porcentaje = 1.0   # 100% de penalidad (No hay devolución)
        elif 15 <= dias_faltantes <= 29:
            porcentaje = 0.50  # 50% de penalidad
        else:
            porcentaje = 0.10  # 10% por gastos administrativos
            
        monto_penalidad = monto_total * porcentaje
        return round(monto_penalidad, 2), porcentaje

    def generar_factura_penalidad(
        self, 
        id_reserva: str, 
        nombre_cliente: str, 
        monto: float, 
        porcentaje: float
    ) -> str:
        """Genera una nota de débito/factura por penalidad de cancelación."""
        return f"""
╔════════════════════════════════════════════════════════════════╗
║             NOTA DE PENALIDAD - CANCELACIÓN                    ║
║        Sistema de Recursos para Eventos Musicales              ║
╚════════════════════════════════════════════════════════════════╝

REFERENCIA: {id_reserva}
CLIENTE: {nombre_cliente}
FECHA DE CANCELACIÓN: {datetime.now().strftime("%d/%m/%Y %H:%M")}

────────────────────────────────────────────────────────────────
MOTIVO: Cancelación de reserva confirmada fuera de plazo.
TASA DE PENALIDAD APLICADA: {porcentaje * 100}%
────────────────────────────────────────────────────────────────

TOTAL A RETENER / FACTURAR:   S/.{monto:>10.2f}

════════════════════════════════════════════════════════════════
"""
    
    def __repr__(self) -> str:
        return f"Tarificador(tasa_igv={self.TASA_IGV*100}%, buffer={self.BUFFER_MINUTOS}min)"
