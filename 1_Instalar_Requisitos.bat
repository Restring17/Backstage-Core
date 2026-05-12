@echo off
REM Instalador de dependencias - Backstage-Core (Windows)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║        INSTALADOR DE DEPENDENCIAS - BACKSTAGE-CORE             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Nos quedamos en el directorio del bat, no en codigo_fuente
cd /d "%~dp0"

REM Comprueba que Python esté disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo    Descárgalo desde python.org - asegúrate de marcar "Add Python to PATH"
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Crea el entorno virtual si no existe aún
if not exist ".venv\" (
    echo 🔧 Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Error al crear el entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
) else (
    echo ✅ Entorno virtual ya existe
)

echo.
echo 📦 Instalando dependencias...
echo.

REM Instala todo dentro del venv, no en el Python global
.venv\Scripts\python.exe -m pip install --upgrade pip -q

REM Pre-instala pyiceberg con wheel precompilado para evitar compilar C en Windows
REM (pyiceberg es dependencia transitiva de supabase y requiere MSVC si compila desde fuente)
.venv\Scripts\python.exe -m pip install --only-binary=:all: pyiceberg 2>nul || (
    echo ⚠️  Wheel de pyiceberg no disponible para esta versión de Python, intentando sin compilar extensión C...
    .venv\Scripts\python.exe -m pip install --no-build-isolation pyiceberg
)

.venv\Scripts\python.exe -m pip install -r codigo_fuente\requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ Error durante la instalación
    pause
    exit /b 1
)

echo.
echo ✅ ¡Instalación completada!
echo    Ahora ejecuta: 2_Iniciar_Sistema.bat
echo.
pause
