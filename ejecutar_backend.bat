@echo off
echo ============================================
echo   Ejecutar Backend - Sistema de Correos
echo ============================================
echo.

cd backend

:: Verificar si el entorno virtual existe
if not exist "venv" (
    echo [ERROR] El entorno virtual no existe
    echo Ejecute primero instalar_backend.bat
    pause
    exit /b 1
)

:: Verificar si .env existe
if not exist ".env" (
    echo [ERROR] El archivo .env no existe
    echo Ejecute primero instalar_backend.bat
    pause
    exit /b 1
)

:: Activar entorno virtual
call venv\Scripts\activate.bat

:: Ejecutar servidor
echo Iniciando servidor backend...
echo El backend estara disponible en: http://localhost:7373
echo Documentacion API: http://localhost:7373/docs
echo.
echo Presione Ctrl+C para detener el servidor
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 7373
