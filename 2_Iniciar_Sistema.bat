@echo off
REM Iniciador del sistema - Backstage-Core (Windows)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           INICIADOR DEL SISTEMA - BACKSTAGE-CORE               ║
echo ║    Sistema de Gestión de Recursos para Eventos Musicales      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Comprueba que Python esté disponible antes de intentar nada
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado
    echo    Ejecuta primero: 1_Instalar_Requisitos.bat
    pause
    exit /b 1
)

echo ✅ Iniciando sistema...
echo.

REM %~dp0 siempre es la ruta absoluta del bat, así el path al venv no se rompe con el cd de abajo
if exist "%~dp0.venv\Scripts\python.exe" (
    set PYTHON=%~dp0.venv\Scripts\python.exe
    echo    Usando entorno virtual ^(.venv^)
) else (
    set PYTHON=python
    echo    Usando Python del sistema - ejecuta 1_Instalar_Requisitos.bat si hay errores
)

cd "%~dp0codigo_fuente"
%PYTHON% main.py

if errorlevel 1 (
    echo.
    echo ❌ El sistema finalizó con un error
    pause
)
