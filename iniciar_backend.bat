@echo off
title Backend - Sistema de Correos (Puerto 7373)
color 0A

echo ============================================
echo   Sistema de Envio de Correos - Backend
echo ============================================
echo.

cd /d "%~dp0backend"

:: Verificar si el entorno virtual existe
if not exist "venv" (
    echo [ERROR] El entorno virtual no existe
    echo Ejecute primero instalar_backend.bat
    echo.
    pause
    exit /b 1
)

:: Verificar si .env existe
if not exist ".env" (
    echo [ERROR] El archivo .env no existe
    echo Ejecute primero instalar_backend.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [INFO] Iniciando servidor backend...
echo.
echo ============================================
echo   Backend corriendo en: http://localhost:7373
echo   Documentacion API: http://localhost:7373/docs
echo ============================================
echo.
echo   PRESIONE CTRL+C PARA DETENER EL SERVIDOR
echo.
echo ============================================

:restart
echo [%date% %time%] Iniciando servidor...
uvicorn app.main:app --host 127.0.0.1 --port 7373

:: Si el servidor se detiene inesperadamente, reiniciarlo
echo.
echo [%date% %time%] El servidor se detuvo. Reiniciando en 3 segundos...
timeout /t 3 /nobreak >nul
goto restart