#!/bin/bash
# Iniciador del Sistema - Backstage-Core para Linux
# Ejecuta este archivo para levantar la interfaz del sistema

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           INICIADOR DEL SISTEMA - BACKSTAGE-CORE               ║"
echo "║    Sistema de Gestión de Recursos para Eventos Musicales       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verifica si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 no está instalado"
    echo "   Por favor ejecuta: ./1_Instalar_Requisitos.sh"
    exit 1
fi

echo "✅ Iniciando sistema..."
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Selecciona el intérprete: usa .venv si existe, sino python3 del sistema
if [ -f "$PROJECT_DIR/.venv/bin/python3" ]; then
    PYTHON="$PROJECT_DIR/.venv/bin/python3"
    echo "   🔒 Usando entorno virtual (.venv)"
else
    PYTHON="python3"
    echo "   ⚠️  Usando Python del sistema (ejecuta 1_Instalar_Requisitos.sh si hay errores)"
fi

# Ejecuta main.py desde la carpeta codigo_fuente
cd "$PROJECT_DIR/codigo_fuente"
$PYTHON main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ El sistema finalizó con un error"
fi

