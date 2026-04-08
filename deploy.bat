@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ============================================
REM Script de Despliegue - Email Sender App
REM VPS: 187.124.224.233
REM Puerto: 1482
REM ============================================

set VPS_IP=187.124.224.233
set VPS_USER=root
set REMOTE_PATH=/opt/email_sender

echo ============================================
echo Desplegando Email Sender App en VPS
echo ============================================
echo IP: %VPS_IP%
echo Usuario: %VPS_USER%
echo Puerto: 1482
echo ============================================
echo.

REM Verificar conexion SSH
echo Verificando conexion SSH...
echo.

REM Crear directorio en el servidor
echo Creando directorios en el servidor...
ssh -o StrictHostKeyChecking=no %VPS_USER%@%VPS_IP% "mkdir -p %REMOTE_PATH%/data"
if %errorlevel% neq 0 (
    echo Error: No se pudo conectar al servidor. Verifica las credenciales.
    pause
    exit /b 1
)

REM Subir archivos usando scp
echo.
echo Subiendo archivos al VPS...
echo.

echo Subiendo docker-compose.yml...
scp -o StrictHostKeyChecking=no docker-compose.yml %VPS_USER%@%VPS_IP%:%REMOTE_PATH%/

echo Subiendo nginx-proxy.conf...
scp -o StrictHostKeyChecking=no nginx-proxy.conf %VPS_USER%@%VPS_IP%:%REMOTE_PATH%/

echo Subiendo carpeta backend...
scp -o StrictHostKeyChecking=no -r backend %VPS_USER%@%VPS_IP%:%REMOTE_PATH%/

echo Subiendo carpeta frontend...
scp -o StrictHostKeyChecking=no -r frontend %VPS_USER%@%VPS_IP%:%REMOTE_PATH%/

echo Subiendo carpeta data...
scp -o StrictHostKeyChecking=no -r data %VPS_USER%@%VPS_IP%:%REMOTE_PATH%/

echo.
echo Archivos subidos correctamente
echo.

REM Ejecutar comandos en el servidor
echo Configurando y levantando contenedores Docker...
echo.

echo Deteniendo contenedores existentes...
ssh -o StrictHostKeyChecking=no %VPS_USER%@%VPS_IP% "cd %REMOTE_PATH% && docker-compose down 2>/dev/null || true"

echo Construyendo contenedores (esto puede tomar unos minutos)...
ssh -o StrictHostKeyChecking=no %VPS_USER%@%VPS_IP% "cd %REMOTE_PATH% && docker-compose build --no-cache"

echo Iniciando contenedores...
ssh -o StrictHostKeyChecking=no %VPS_USER%@%VPS_IP% "cd %REMOTE_PATH% && docker-compose up -d"

echo Esperando a que los contenedores esten listos...
timeout /t 10 /nobreak >nul

echo.
echo Estado de los contenedores:
ssh -o StrictHostKeyChecking=no %VPS_USER%@%VPS_IP% "cd %REMOTE_PATH% && docker-compose ps"

echo.
echo Limpiando imagenes no utilizadas...
ssh -o StrictHostKeyChecking=no %VPS_USER%@%VPS_IP% "docker image prune -f"

echo.
echo ============================================
echo Despliegue completado!
echo ============================================
echo.
echo La aplicacion esta disponible en:
echo    http://%VPS_IP%:1482
echo.
echo Credenciales de acceso:
echo    Usuario: Admin1
echo    Contraseña: Admin123
echo.
echo Comandos utiles:
echo    Ver logs: ssh %VPS_USER%@%VPS_IP% "cd %REMOTE_PATH% ^&^& docker-compose logs -f"
echo    Reiniciar: ssh %VPS_USER%@%VPS_IP% "cd %REMOTE_PATH% ^&^& docker-compose restart"
echo    Detener: ssh %VPS_USER%@%VPS_IP% "cd %REMOTE_PATH% ^&^& docker-compose down"
echo ============================================
echo.

pause