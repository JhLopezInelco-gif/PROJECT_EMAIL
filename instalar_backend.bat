@echo off
echo ============================================
echo   Instalador del Backend - Sistema de Correos
echo ============================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH
    echo.
    echo Por favor instale Python 3.10 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    echo Asegúrese de marcar la opción "Add Python to PATH" durante la instalación.
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version
echo.

:: Crear entorno virtual
echo Creando entorno virtual...
cd backend
if not exist "venv" (
    python -m venv venv
    echo [OK] Entorno virtual creado
) else (
    echo [OK] El entorno virtual ya existe
)
echo.

:: Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo [OK] Entorno virtual activado
echo.

:: Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt
echo [OK] Dependencias instaladas
echo.

:: Crear archivo .env si no existe
if not exist ".env" (
    echo Creando archivo de configuracion...
    copy .env.example .env
    echo [OK] Archivo .env creado desde .env.example
    echo.
    echo [IMPORTANTE] Edite el archivo backend\.env con sus credenciales:
    echo   - DATABASE_URL: Cadena de conexion PostgreSQL
    echo   - SMTP_USER: Su correo electronico
    echo   - SMTP_PASSWORD: Su contrasena de aplicacion
    echo.
) else (
    echo [OK] El archivo .env ya existe
)
echo.

echo ============================================
echo   Instalacion completada!
echo ============================================
echo.
echo Para ejecutar el backend:
echo   1. cd backend
echo   2. venv\Scripts\activate
echo   3. uvicorn app.main:app --reload --port 8000
echo.
echo El backend estara disponible en: http://localhost:8000
echo Documentacion API: http://localhost:8000/docs
echo.
pause