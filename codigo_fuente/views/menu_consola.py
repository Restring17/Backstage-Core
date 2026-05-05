"""
Módulo de Interfaz de Usuario: Menú interactivo en consola
Empresa: Backstage-Core
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from models import Recurso, EquipoFisico, PersonalTecnico, Ambiente, ReservaEscenario
# Se asume que EstadoReserva está en models y se importa para usar los Enums en BD
from models.reserva import EstadoReserva 
from services import Tarificador, GestorReservas
from database import BaseDatos, DBSQLite, DBSupabase


class MenuConsola:
    """
    Interfaz de usuario interactiva en consola para Backstage-Core.
    Permite elegir entre modo Nube (Supabase) o Local (SQLite).
    """

    def __init__(self):
        """Inicializa el menú."""
        self._gestor_reservas: Optional[GestorReservas] = None
        self._tarificador: Optional[Tarificador] = None
        self._base_datos: Optional[BaseDatos] = None
        self._recursos_catalogo: dict = {}
        self._ambientes_catalogo: dict = {}
        self._salir = False

    def mostrar_banner(self) -> None:
        """Muestra el banner de bienvenida."""
        print("""
╔════════════════════════════════════════════════════════════════╗
║                     🎸 BACKSTAGE-CORE 🎸                       ║
║      Sistema de Gestión de Recursos para Festivales           ║
║                                                                ║
║         Empresa: Backstage-Core Producciones                   ║
║         Versión: 1.0 (POO Python)                              ║
╚════════════════════════════════════════════════════════════════╝
        """)

    def mostrar_menu_inicio(self) -> None:
        """Muestra el menú de selección de entorno."""
        print("\n📡 SELECCIONAR ENTORNO DE BD:")
        print("  [1] 🌐 Nube (Supabase - Requiere Internet)")
        print("  [2] 💾 Local (SQLite - Modo Offline/USB)")
        print("  [3] ❌ Salir")
        print()

    def seleccionar_entorno(self) -> bool:
        """
        Permite al usuario seleccionar el entorno (Nube o Local).

        Returns:
            True si se seleccionó un entorno, False si salir
        """
        while True:
            self.mostrar_menu_inicio()
            opcion = input("Ingresa tu opción: ").strip()

            match opcion:
                case "1":
                    print("\n🌐 Inicializando conexión a Supabase...")
                    self._base_datos = DBSupabase()
                    if self._base_datos.conectar():
                        self._inicializar_sistema()
                        return True
                    else:
                        print("❌ Error: No se pudo conectar a Supabase. ¿Credenciales configuradas?")
                        print("   (Asegúrate de establecer SUPABASE_URL y SUPABASE_KEY en variables de entorno)")
                        input("Presiona Enter para intentar de nuevo...")

                case "2":
                    print("\n💾 Inicializando SQLite (Modo Local)...")
                    self._base_datos = DBSQLite("backstage_core.db")
                    if self._base_datos.conectar():
                        self._inicializar_sistema()
                        self._cargar_datos_demo()
                        return True

                case "3":
                    print("👋 Hasta luego!")
                    return False

                case _:
                    print("❌ Opción no válida")

    def _inicializar_sistema(self) -> None:
        """Inicializa los servicios del sistema."""
        self._tarificador = Tarificador()
        self._gestor_reservas = GestorReservas(self._tarificador)

    def _cargar_datos_demo(self) -> None:
        """Carga datos de demostración (solo para SQLite)."""
        print("\n📦 Cargando datos de demostración...")

        # Crear ambientes de demo
        ambiente1 = Ambiente(
            id_ambiente="AMB-001",
            nombre="Escenario Principal",
            capacidad_personas=5000,
            precio_alquiler_hora=500.0,
            requiere_sonido=True,
            requiere_luces=True,
        )
        self._ambientes_catalogo["AMB-001"] = ambiente1

        ambiente2 = Ambiente(
            id_ambiente="AMB-002",
            nombre="Escenario Secundario",
            capacidad_personas=2000,
            precio_alquiler_hora=250.0,
            requiere_sonido=True,
            requiere_luces=True,
        )
        self._ambientes_catalogo["AMB-002"] = ambiente2

        # Crear equipos de demo
        consola = EquipoFisico(
            id_recurso="EQ-001",
            nombre="Consola Soundcraft Si Impact",
            precio_base_hora=150.0,
            categoria="Iluminación",
            marca="Soundcraft",
            requiere_conexion_electrica=True,
            peso_kg=45.5,
        )
        self._recursos_catalogo["EQ-001"] = consola

        guitarra = EquipoFisico(
            id_recurso="EQ-002",
            nombre="Guitarra Eléctrica Fender Stratocaster",
            precio_base_hora=50.0,
            categoria="Instrumento",
            marca="Fender",
            requiere_conexion_electrica=False,
            peso_kg=3.5,
        )
        self._recursos_catalogo["EQ-002"] = guitarra

        # Crear personal de demo
        tecnico_sonido = PersonalTecnico(
            id_recurso="PERS-001",
            nombre="Juan García - Ingeniero de Sonido",
            precio_base_hora=80.0,
            especialidad="Sonido",
            años_experiencia=10,
        )
        self._recursos_catalogo["PERS-001"] = tecnico_sonido

        tecnico_luces = PersonalTecnico(
            id_recurso="PERS-002",
            nombre="María López - Especialista en Iluminación",
            precio_base_hora=70.0,
            especialidad="Luces",
            años_experiencia=7,
        )
        self._recursos_catalogo["PERS-002"] = tecnico_luces

        print("✅ Datos de demostración cargados")
        print(f"   • {len(self._ambientes_catalogo)} ambientes")
        print(f"   • {len(self._recursos_catalogo)} recursos")

    def mostrar_menu_principal(self) -> None:
        """Muestra el menú principal."""
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║              📋 MENÚ PRINCIPAL BACKSTAGE-CORE                  ║")
        print("╚════════════════════════════════════════════════════════════════╝")
        print("\n  [1] 🎫 Crear Nueva Reserva")
        print("  [2] 🔍 Consultar Reserva")
        print("  [3] ✅ Confirmar Pago de Reserva")
        print("  [4] ❌ Cancelar Reserva (Rollback)")
        print("  [5] 📊 Ver Reporte de Ocupación")
        print("  [6] 💰 Ver Reporte de Ingresos")
        print("  [7] 📦 Listar Recursos Disponibles")
        print("  [8] 🛠️  Enviar Equipo a Mantenimiento") # [NUEVO] Opción de mantenimiento
        print("  [9] 🏛️  Listar Ambientes")
        print("  [10] ℹ️  Información de Conexión")
        print("  [0] 🚪 Salir")
        print()

    def ejecutar(self) -> None:
        """Ejecuta el menú principal."""
        self.mostrar_banner()

        # Selecciona entorno
        if not self.seleccionar_entorno():
            return

        # Menú principal - Reestructurado con match...case
        while not self._salir:
            self.mostrar_menu_principal()
            opcion = input("Selecciona una opción: ").strip()

            match opcion:
                case "1":
                    self._crear_reserva()
                case "2":
                    self._consultar_reserva()
                case "3":
                    self._confirmar_pago()
                case "4":
                    self._cancelar_reserva()
                case "5":
                    self._reporte_ocupacion()
                case "6":
                    self._reporte_ingresos()
                case "7":
                    self._listar_recursos()
                case "8":
                    self._gestionar_mantenimiento()
                case "9":
                    self._listar_ambientes()
                case "10":
                    self._info_conexion()
                case "0":
                    print("👋 Cierre de sesión. ¡Hasta pronto!")
                    self._salir = True
                case _:
                    print("❌ Opción no válida")

    def _crear_reserva(self) -> None:
        """Crea una nueva reserva interactivamente."""
        print("\n╔════════════════════════════════════════════════════════════════╗")
        print("║                    🎫 CREAR NUEVA RESERVA                      ║")
        print("╚════════════════════════════════════════════════════════════════╝")

        # Selecciona ambiente
        if not self._ambientes_catalogo:
            print("❌ No hay ambientes disponibles")
            return

        print("\nAmbientes disponibles:")
        for id_amb, amb in self._ambientes_catalogo.items():
            print(f"  {id_amb}: {amb.nombre} (S/.{amb.precio_alquiler_hora}/hora)")

        id_ambiente = input("\nSelecciona ID de ambiente: ").strip()
        if id_ambiente not in self._ambientes_catalogo:
            print("❌ Ambiente no encontrado")
            return

        ambiente = self._ambientes_catalogo[id_ambiente]

        # Datos de la banda
        nombre_banda = input("Nombre de la banda: ").strip()
        manager = input("Contacto del manager (teléfono): ").strip()

        # Horario
        try:
            fecha_str = input("Fecha de inicio (DD/MM/YYYY): ").strip()
            hora_str = input("Hora de inicio (HH:MM): ").strip()
            
            dia, mes, año = map(int, fecha_str.split("/"))
            hora_h, hora_m = map(int, hora_str.split(":"))
            
            hora_inicio = datetime(año, mes, dia, hora_h, hora_m, 0)
            
            # Valida que la hora sea en el futuro
            if hora_inicio <= datetime.now():
                print("❌ Error: La hora debe ser en el futuro")
                return

            duracion_minutos = int(input("Duración en minutos: ").strip())
            hora_fin = hora_inicio + timedelta(minutes=duracion_minutos)
        except ValueError:
            print("❌ Formato de hora no válido")
            return

        # Selecciona recursos
        print("\nRecursos disponibles:")
        for id_rec, rec in self._recursos_catalogo.items():
            print(f"  {id_rec}: {rec.nombre} - {rec.obtener_tipo_recurso()} (S/.{rec.precio_base_hora}/hora)")

        recursos_ids = input("\nIngresa IDs de recursos (separados por coma): ").strip().split(",")
        recursos = [
            self._recursos_catalogo[rid.strip()]
            for rid in recursos_ids
            if rid.strip() in self._recursos_catalogo
        ]

        if not recursos:
            print("❌ Selecciona al menos un recurso válido")
            return

        # Crea reserva
        reserva = self._gestor_reservas.crear_reserva(
            ambiente=ambiente,
            nombre_banda=nombre_banda,
            manager_contacto=manager,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            recursos_solicitados=recursos,
        )

        if reserva:
            print(f"\n✅ Reserva creada: {reserva.id_reserva}")
            print(f"   Estado: {reserva.estado.value}")
            print(f"   Monto a pagar: S/.{reserva.monto_total_con_igv:.2f}")
            # [NUEVO] Reflejamos el cambio de Minutos a Horas en la UI
            print(f"   ⏱️  Tienes {reserva.TIMEOUT_PAGO_HORAS} horas para confirmar el pago")

            # Muestra factura
            desglose = reserva.obtener_desglose_presupuesto()
            from services.tarificador import Tarificador
            factura = Tarificador().generar_factura(
                reserva.id_reserva, nombre_banda, desglose
            )
            print(factura)
            
            # [CORRECCIÓN] En lugar de acceder a la BD directo aquí, 
            # el GestorReservas debería hacerlo internamente. Pero para 
            # mantener la estructura actual, usamos el Enum y try/except.
            if self._base_datos:
                try:
                    self._base_datos.guardar_reserva({
                        "id_reserva": reserva.id_reserva,
                        "id_ambiente": ambiente.id_ambiente,
                        "nombre_banda": nombre_banda,
                        "manager_contacto": manager,
                        "hora_inicio": reserva.hora_inicio.isoformat(),
                        "hora_fin": reserva.hora_fin.isoformat(),
                        "estado": reserva.estado.value, # Se mantiene el uso de value del Enum
                        "monto_sin_igv": reserva.monto_sin_igv,
                        "monto_igv": reserva.monto_igv,
                        "monto_total": reserva.monto_total_con_igv
                    })        
                except Exception as e:
                    print(f"⚠️ Aviso: La reserva se creó en memoria, pero no se guardó en BD ({e})")

    def _consultar_reserva(self) -> None:
        """Consulta el estado de una reserva."""
        print("\n🔍 Consultar Reserva")
        id_reserva = input("ID de reserva: ").strip()

        reserva = self._gestor_reservas.obtener_reserva(id_reserva)
        if reserva:
            print(f"\n✅ Reserva encontrada:")
            print(f"   ID: {reserva.id_reserva}")
            print(f"   Banda: {reserva.nombre_banda}")
            print(f"   Ambiente: {reserva.ambiente.nombre}")
            print(f"   Estado: {reserva.estado.value}")
            print(f"   Monto: S/.{reserva.monto_total_con_igv:.2f}")
            print(f"   Hora: {reserva.hora_inicio.strftime('%H:%M')} - {reserva.hora_fin.strftime('%H:%M')}")
        else:
            print("❌ Reserva no encontrada")

    def _confirmar_pago(self) -> None:
        """Confirma el pago de una reserva."""
        print("\n✅ Confirmar Pago")
        id_reserva = input("ID de reserva: ").strip()

        reserva = self._gestor_reservas.obtener_reserva(id_reserva)
        if not reserva:
            print("❌ Reserva no encontrada")
            return

        print(f"   Monto a pagar: S/.{reserva.monto_total_con_igv:.2f}")
        
        # [CORRECCIÓN] Captura de excepciones al ingresar montos
        try:
            monto_ingresado = float(input("Monto ingresado: ").strip())
        except ValueError:
            print("❌ Error: Por favor ingresa un monto numérico válido.")
            return

        if self._gestor_reservas.confirmar_pago_reserva(id_reserva, monto_ingresado):
            print("✅ Pago confirmado. Reserva activada.")
            # [CORRECCIÓN] Uso del Enum en lugar de Magic String
            if self._base_datos:
                try:
                    self._base_datos.actualizar_reserva(id_reserva, {"estado": EstadoReserva.CONFIRMADA.value})
                except Exception as e:
                     print(f"⚠️ Aviso: Se actualizó en memoria, pero falló la BD ({e})")
        else:
            print("❌ Error al confirmar pago")

    def _cancelar_reserva(self) -> None:
        """Cancela una reserva y aplica penalidades si corresponde."""
        print("\n❌ Cancelar Reserva")
        id_reserva = input("ID de reserva: ").strip()
        razon = input("Razón de cancelación: ").strip()

        exito, mensaje = self._gestor_reservas.cancelar_reserva(id_reserva, razon)
        
        if exito:
            # [CORRECCIÓN] Uso del Enum en lugar de Magic String
            if self._base_datos:
                try:
                    self._base_datos.actualizar_reserva(id_reserva, {"estado": EstadoReserva.CANCELADA.value})
                except Exception as e:
                    print(f"⚠️ Aviso: Se canceló en memoria, pero falló la actualización en BD ({e})")
        else:
            print(f"❌ Fallo al cancelar: {mensaje}")

    def _gestionar_mantenimiento(self) -> None:
        """Flujo para enviar un equipo a mantenimiento."""
        print("\n🛠️ Enviar Equipo a Mantenimiento")
        id_recurso = input("Ingresa el ID del equipo: ").strip()

        if id_recurso not in self._recursos_catalogo:
            print("❌ Equipo no encontrado en el catálogo.")
            return

        recurso = self._recursos_catalogo[id_recurso]
        
        # Invocamos el método que acabamos de crear en recurso.py
        exito, mensaje = recurso.enviar_a_mantenimiento()
        print(mensaje)

    def _reporte_ocupacion(self) -> None:
        """Muestra reporte de ocupación."""
        print("\n📊 Reporte de Ocupación")
        for id_amb in self._ambientes_catalogo:
            reporte = self._gestor_reservas.generar_reporte_ocupacion_ambiente(id_amb)
            print(f"\n{reporte['id_ambiente']} - Ocupación:")
            print(f"   Reservas activas: {reporte['total_reservas_activas']}")
            print(f"   Pendientes de pago: {reporte['total_pendientes_pago']}")
            print(f"   Ingresos potenciales: S/.{reporte['ingresos_potenciales']:.2f}")

    def _reporte_ingresos(self) -> None:
        """Muestra reporte de ingresos."""
        print("\n💰 Reporte de Ingresos")
        reporte = self._gestor_reservas.generar_reporte_ingresos()
        print(f"   Reservas confirmadas: {reporte['total_reservas_confirmadas']}")
        print(f"   Subtotal (sin IGV): S/.{reporte['subtotal_sin_igv']:.2f}")
        print(f"   IGV 18%: S/.{reporte['total_igv_18']:.2f}")
        print(f"   Total: S/.{reporte['total_con_igv']:.2f}")
        print(f"   Promedio/reserva: S/.{reporte['promedio_por_reserva']:.2f}")

    def _listar_recursos(self) -> None:
        """Lista todos los recursos disponibles."""
        print("\n📦 Recursos Disponibles")
        for id_rec, rec in self._recursos_catalogo.items():
            print(f"   {id_rec}: {rec.nombre}")
            print(f"      Tipo: {rec.obtener_tipo_recurso()}")
            print(f"      Precio/hora: S/.{rec.precio_base_hora:.2f}")
            print(f"      Estado: {rec.estado.value}")

    def _listar_ambientes(self) -> None:
        """Lista todos los ambientes."""
        print("\n🏛️  Ambientes")
        for id_amb, amb in self._ambientes_catalogo.items():
            print(f"   {id_amb}: {amb.nombre}")
            print(f"      Capacidad: {amb.capacidad_personas} personas")
            print(f"      Precio/hora: S/.{amb.precio_alquiler_hora:.2f}")
            print(f"      Estado: {amb.estado.value}")

    def _info_conexion(self) -> None:
        """Muestra información de la conexión."""
        print("\nℹ️  Información de Conexión")
        if self._base_datos:
            info = self._base_datos.obtener_informacion_conexion()
            for clave, valor in info.items():
                print(f"   {clave}: {valor}")