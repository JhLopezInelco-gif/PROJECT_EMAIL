@echo off
title Frontend - Sistema de Correos (Puerto 7171)
color 0B

echo ============================================
echo   Sistema de Envio de Correos - Frontend
echo ============================================
echo.

cd /d "%~dp0frontend"

:: Verificar si node_modules existe
if not exist "node_modules" (
    echo [INFO] Instalando dependencias de npm...
    npm install
    if errorlevel 1 (
        echo [ERROR] Error al instalar dependencias
        pause
        exit /b 1
    )
)

echo [INFO] Iniciando servidor frontend...
echo.
echo ============================================
echo   Frontend corriendo en: http://localhost:7171
echo ============================================
echo.
echo   PRESIONE CTRL+C PARA DETENER EL SERVIDOR
echo.
echo ============================================

:restart
echo [%date% %time%] Iniciando servidor...
npm start

:: Si el servidor se detiene inesperadamente, reiniciarlo
echo.
echo [%date% %time%] El servidor se detuvo. Reiniciando en 3 segundos...
timeout /t 3 /nobreak >nul
goto restart