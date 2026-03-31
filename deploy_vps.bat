@echo off
chcp 65001 >nul
echo ============================================
echo Desplegando Email Sender App en VPS
echo ============================================
echo IP: 187.124.224.233
echo Puerto: 1482
echo Usuario: root
echo ============================================
echo.

REM Crear directorio en el servidor
echo Creando directorios en el servidor...
ssh -o StrictHostKeyChecking=no -i orig\archi.jh root@187.124.224.233 "mkdir -p /opt/email_sender/data"

REM Subir archivos
echo Subiendo archivos al VPS...
scp -o StrictHostKeyChecking=no -i orig\archi.jh docker-compose.yml root@187.124.224.233:/opt/email_sender/
scp -o StrictHostKeyChecking=no -i orig\archi.jh nginx-proxy.conf root@187.124.224.233:/opt/email_sender/
scp -o StrictHostKeyChecking=no -i orig\archi.jh -r backend root@187.124.224.233:/opt/email_sender/
scp -o StrictHostKeyChecking=no -i orig\archi.jh -r frontend root@187.124.224.233:/opt/email_sender/
scp -o StrictHostKeyChecking=no -i orig\archi.jh -r data root@187.124.224.233:/opt/email_sender/

echo.
echo Archivos subidos correctamente.
echo.

REM Construir y levantar contenedores
echo Construyendo y levantando contenedores Docker...
ssh -o StrictHostKeyChecking=no -i orig\archi.jh root@187.124.224.233 "cd /opt/email_sender && docker-compose down 2>/dev/null; docker-compose build --no-cache && docker-compose up -d && docker-compose ps"

echo.
echo ============================================
echo Despliegue completado!
echo ============================================
echo La aplicacion esta disponible en:
echo http://187.124.224.233:1482
echo.
echo Credenciales de acceso:
echo Usuario: Admin1
echo Contraseña: Admin123
echo ============================================
pause