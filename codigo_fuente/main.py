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

# Cargar variables de entorno desde el archivo .env principal
try:
    from dotenv import load_dotenv
    # Busca el archivo .env en la raíz del proyecto
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(env_path)
except ImportError:
    print("⚠️ python-dotenv no está instalado. Ejecuta: pip install python-dotenv")

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
