@echo off
title Diagnostico del Sistema de Correos
color 0B

echo ============================================
echo   DIAGNOSTICO DEL SISTEMA DE CORREOS
echo ============================================
echo. 

:: 1. Verificar puerto del backend (7373)
echo [1] Verificando Backend (puerto 7373)...
netstat -an | findstr ":7373" >nul
if %errorlevel% equ 0 (
    echo     [OK] Backend esta ejecutandose en puerto 7373
) else (
    echo     [ERROR] Backend NO esta ejecutandose en puerto 7373
    echo     Solucion: Ejecute iniciar_backend.bat
)
echo.

:: 2. Verificar puerto del frontend (7171)
echo [2] Verificando Frontend (puerto 7171)...
netstat -an | findstr ":7171" >nul
if %errorlevel% equ 0 (
    echo     [OK] Frontend esta ejecutandose en puerto 7171
) else (
    echo     [ERROR] Frontend NO esta ejecutandose en puerto 7171
    echo     Solucion: Ejecute iniciar_frontend.bat
)
echo.

:: 3. Verificar que el backend responde
echo [3] Verificando respuesta del Backend...
curl -s -o nul -w "%%{http_code}" http://localhost:7373/health 2>nul > temp_response.txt
set /p response=<temp_response.txt
del temp_response.txt 2>nul
if "%response%"=="200" (
    echo     [OK] Backend responde correctamente (HTTP 200)
) else (
    echo     [ERROR] Backend no responde o devuelve error
    echo     Codigo HTTP: %response%
)
echo.

:: 4. Verificar archivos de configuracion
echo [4] Verificando archivos de configuracion...
if exist "backend\.env" (
    echo     [OK] backend\.env existe
) else (
    echo     [ERROR] backend\.env NO existe
)

if exist "frontend\.env" (
    echo     [OK] frontend\.env existe
    
    :: Verificar puerto configurado
    findstr /C:"REACT_APP_API_URL=http://localhost:7373" frontend\.env >nul
    if %errorlevel% equ 0 (
        echo     [OK] Frontend configurado para puerto 7373
    ) else (
        echo     [ADVERTENCIA] Frontend podria estar mal configurado
    )
) else (
    echo     [ERROR] frontend\.env NO existe
)
echo.

:: 5. Verificar node_modules
echo [5] Verificando dependencias de Frontend...
if exist "frontend\node_modules\bootstrap" (
    echo     [OK] Bootstrap instalado localmente
) else (
    echo     [ERROR] Bootstrap NO instalado - ejecute: cd frontend && npm install
)

if exist "frontend\node_modules\bootstrap-icons" (
    echo     [OK] Bootstrap Icons instalado localmente
) else (
    echo     [ERROR] Bootstrap Icons NO instalado - ejecute: cd frontend && npm install
)
echo.

:: 6. Verificar entorno virtual de Python
echo [6] Verificando entorno virtual de Backend...
if exist "backend\venv\Scripts\activate.bat" (
    echo     [OK] Entorno virtual existe
) else (
    echo     [ERROR] Entorno virtual NO existe - ejecute instalar_backend.bat
)
echo.

echo ============================================
echo   RESUMEN DE DIAGNOSTICO
echo ============================================
echo.
echo Si ve errores, siga estos pasos:
echo.
echo 1. Si el backend no esta corriendo:
echo    - Ejecute: iniciar_backend.bat
echo.
echo 2. Si el frontend no esta corriendo:
echo    - Ejecute: iniciar_frontend.bat
echo.
echo 3. Si hay problemas de puertos:
echo    - Backend debe usar puerto 7373
echo    - Frontend debe usar puerto 7171
echo    - REACT_APP_API_URL debe ser http://localhost:7373/api
echo.
echo 4. Para reiniciar todo desde cero:
echo    - Cierre todas las ventanas de terminal
echo    - Ejecute: iniciar_todo.bat
echo.
echo ============================================
echo.
pause