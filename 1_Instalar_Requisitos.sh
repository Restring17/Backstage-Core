#!/bin/bash
# Instalador de Dependencias - Backstage-Core para Linux
# Ejecuta este archivo para instalar todas las librerías necesarias

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        INSTALADOR DE DEPENDENCIAS - BACKSTAGE-CORE             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verifica si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 no está instalado o no está en el PATH"
    echo "   Por favor, instala Python 3 usando tu gestor de paquetes (ej: sudo apt install python3)"
    exit 1
fi

echo "✅ Python 3 encontrado"
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Crea el entorno virtual si no existe
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "🔧 Creando entorno virtual (.venv)..."
    python3 -m venv "$PROJECT_DIR/.venv"
    if [ $? -ne 0 ]; then
        echo "❌ Error al crear el entorno virtual"
        exit 1
    fi
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe (.venv)"
fi

echo ""
echo "📦 Instalando dependencias..."
echo ""

# Activa el entorno virtual e instala dependencias
"$PROJECT_DIR/.venv/bin/python3" -m pip install --upgrade pip -q
"$PROJECT_DIR/.venv/bin/python3" -m pip install -r "$PROJECT_DIR/codigo_fuente/requirements.txt"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error durante la instalación"
    exit 1
fi

echo ""
echo "✅ ¡Instalación completada!"
echo "   Ahora ejecuta: ./2_Iniciar_Sistema.sh"
echo ""

