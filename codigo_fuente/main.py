"""
PUNTO DE ENTRADA PRINCIPAL
EventResourceManager - Sistema de Gestión de Recursos para Eventos Musicales
Empresa: Backstage-Core

Ejecuta: python main.py
"""

import sys
import os

# Añade la carpeta actual al path de Python para importaciones relativas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.menu_consola import MenuConsola


def main():
    """Función principal."""
    try:
        menu = MenuConsola()
        menu.ejecutar()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
