@echo off
REM Iniciador del Sistema - Backstage-Core
REM Ejecuta este archivo para levantar la interfaz del sistema

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           INICIADOR DEL SISTEMA - BACKSTAGE-CORE               ║
echo ║    Sistema de Gestión de Recursos para Eventos Musicales      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Verifica si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado
    echo    Por favor ejecuta: 1_Instalar_Requisitos.bat
    pause
    exit /b 1
)

echo ✅ Iniciando sistema...
echo.

REM Cambia al directorio del código fuente y ejecuta main.py
cd /d "%~dp0codigo_fuente"
python main.py

if errorlevel 1 (
    echo.
    echo ❌ El sistema finalizó con un error
    pause
)
