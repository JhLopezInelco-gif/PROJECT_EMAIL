# ============================================
# Script de Despliegue - Email Sender App
# VPS: 187.124.224.233
# Puerto: 1482
# ============================================

$VPS_IP = "187.124.224.233"
$VPS_USER = "root"
$VPS_PASS = "gUf7gXVfSGFXURzMbE36TuBeZNhTJzRqb0Sifkw9ede1235a"
$REMOTE_PATH = "/opt/email_sender"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Desplegando Email Sender App en VPS" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "IP: $VPS_IP"
Write-Host "Usuario: $VPS_USER"
Write-Host "Puerto: 1482"
Write-Host "Ruta remota: $REMOTE_PATH"
Write-Host "============================================" -ForegroundColor Cyan

# Funcion para ejecutar comando SSH con contraseña
function Invoke-SSHCommand {
    param(
        [string]$Command,
        [string]$Password
    )
    
    $secPassword = ConvertTo-SecureString $Password -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential ($VPS_USER, $secPassword)
    
    # Usar plink si esta disponible, sino usar ssh
    if (Get-Command plink -ErrorAction SilentlyContinue) {
        echo y | plink -ssh -batch -pw $Password "$VPS_USER@$VPS_IP" "$Command"
    } else {
        # Intentar con ssh directo
        ssh -o StrictHostKeyChecking=no -o PreferredAuthentications=password -o PubkeyAuthentication=no "$VPS_USER@$VPS_IP" "$Command" 2>&1
    }
}

# Crear directorio en el servidor
Write-Host "`nCreando directorios en el servidor..." -ForegroundColor Yellow

# Lista de archivos a subir
$filesToUpload = @(
    "docker-compose.yml",
    "nginx-proxy.conf",
    "backend",
    "frontend",
    "data"
)

# Mostrar instrucciones si no se puede conectar automaticamente
Write-Host @"

INSTRUCCIONES DE DESPLIEGUE MANUAL:
=====================================

1. Abre una nueva terminal y conectate al servidor:
   ssh root@187.124.224.233
   Contrasena: $VPS_PASS

2. Una vez conectado, ejecuta estos comandos:

   mkdir -p /opt/email_sender/data
   cd /opt/email_sender

3. Desde tu maquina local, sube los archivos (en otra terminal):
   scp -r docker-compose.yml nginx-proxy.conf backend frontend data root@187.124.224.233:/opt/email_sender/

4. En el servidor, ejecuta:
   cd /opt/email_sender
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   docker-compose ps

5. La aplicacion estara disponible en:
   http://187.124.224.233:1482

Credenciales de acceso:
   Usuario: Admin1
   Contrasena: Admin123

"@ -ForegroundColor White

Write-Host "Presiona cualquier tecla para intentar el despliegue automatico..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Intentar despliegue automatico
Write-Host "`nIntentando despliegue automatico..." -ForegroundColor Yellow

try {
    # Crear directorio
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$VPS_USER@$VPS_IP" "mkdir -p $REMOTE_PATH/data" 2>&1
    
    # Subir archivos
    Write-Host "Subiendo archivos..." -ForegroundColor Yellow
    
    # Subir cada archivo/carpeta
    scp -o StrictHostKeyChecking=no docker-compose.yml "$VPS_USER@$VPS_IP`:$REMOTE_PATH/" 2>&1
    scp -o StrictHostKeyChecking=no nginx-proxy.conf "$VPS_USER@$VPS_IP`:$REMOTE_PATH/" 2>&1
    scp -o StrictHostKeyChecking=no -r backend "$VPS_USER@$VPS_IP`:$REMOTE_PATH/" 2>&1
    scp -o StrictHostKeyChecking=no -r frontend "$VPS_USER@$VPS_IP`:$REMOTE_PATH/" 2>&1
    scp -o StrictHostKeyChecking=no -r data "$VPS_USER@$VPS_IP`:$REMOTE_PATH/" 2>&1
    
    Write-Host "Archivos subidos correctamente" -ForegroundColor Green
    
    # Ejecutar comandos Docker
    Write-Host "Construyendo y levantando contenedores..." -ForegroundColor Yellow
    
    ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" "cd $REMOTE_PATH && docker-compose down 2>/dev/null; docker-compose build --no-cache && docker-compose up -d && docker-compose ps" 2>&1
    
    Write-Host "`n============================================" -ForegroundColor Green
    Write-Host "Despliegue completado!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "Aplicacion disponible en: http://$VPS_IP`:1482" -ForegroundColor Cyan
    
} catch {
    Write-Host "`nError en el despliegue automatico. Por favor sigue las instrucciones manuales arriba." -ForegroundColor Red
    Write-Host $_.Exception.Message
}