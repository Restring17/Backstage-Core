@echo off
REM Instalador de Dependencias - Backstage-Core
REM Ejecuta este archivo para instalar todas las librerías necesarias

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║        INSTALADOR DE DEPENDENCIAS - BACKSTAGE-CORE             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Verifica si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo    Por favor, instala Python 3.12+ desde python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.
echo 📦 Instalando dependencias...
echo.

cd /d "%~dp0codigo_fuente"

REM Instala las dependencias
pip install -r requirements.txt

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
