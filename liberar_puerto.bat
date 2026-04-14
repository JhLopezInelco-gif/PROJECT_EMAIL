@echo off
title Liberar Puerto 7373
color 0C

echo ============================================
echo   LIBERAR PUERTO 7373
echo ============================================
echo.

echo [INFO] Buscando procesos usando el puerto 7373...
echo.

:: Buscar procesos usando el puerto 7373
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":7373" ^| findstr "LISTENING"') do (
    echo [INFO] Encontrado proceso con PID: %%a
    echo [INFO] Terminando proceso...
    taskkill /F /PID %%a
    if %errorlevel% equ 0 (
        echo     [OK] Proceso terminado exitosamente
    ) else (
        echo     [ERROR] No se pudo terminar el proceso
    )
)

echo.
echo [INFO] Verificando si el puerto esta libre...
netstat -an | findstr ":7373" >nul
if %errorlevel% equ 0 (
    echo     [ERROR] El puerto 7373 sigue en uso
    echo     Posibles soluciones:
    echo     1. Reinicie su computadora
    echo     2. Verifique si hay otra aplicacion usando este puerto
) else (
    echo     [OK] El puerto 7373 esta libre
)

echo.
echo ============================================
echo   PROCESO COMPLETADO
echo ============================================
echo.
pause