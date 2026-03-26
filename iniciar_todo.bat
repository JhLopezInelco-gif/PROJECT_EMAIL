@echo off
title Sistema de Correos - Iniciar Todo
color 0E

echo ============================================
echo   Sistema de Envio de Correos
echo   Iniciando Backend y Frontend
echo ============================================
echo.

cd /d "%~dp0"

echo [INFO] Iniciando Backend en ventana separada...
start "Backend - Puerto 7373" cmd /k "iniciar_backend.bat"

echo [INFO] Esperando 5 segundos para que inicie el backend...
timeout /t 5 /nobreak >nul

echo [INFO] Iniciando Frontend en ventana separada...
start "Frontend - Puerto 7171" cmd /k "iniciar_frontend.bat"

echo.
echo ============================================
echo   Servicios iniciados:
echo   - Backend:  http://localhost:7373
echo   - Frontend: http://localhost:7171
echo ============================================
echo.
echo   Cierre esta ventana cuando desee.
echo   Los servidores continuaran ejecutandose
echo   en sus ventanas separadas.
echo.
echo   Para detener todo, cierre las ventanas
echo   de Backend y Frontend.
echo ============================================
echo.

:: Abrir navegador con el frontend
echo [INFO] Abriendo navegador en 10 segundos...
timeout /t 10 /nobreak >nul
start http://localhost:7171

echo.
echo [INFO] Proceso completado. Puede cerrar esta ventana.
pause