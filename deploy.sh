#!/bin/bash

# ============================================
# Script de Despliegue - Email Sender App
# VPS: 187.124.224.233
# Puerto: 1482
# ============================================

# Configuración
VPS_IP="187.124.224.233"
VPS_USER="root"
VPS_PASS="gUf7gXVfSGFXURzMbE36TuBeZNhTJzRqb0Sifkw9ede1235a"
REMOTE_PATH="/opt/email_sender"
LOCAL_PATH="$(pwd)"

echo "============================================"
echo "🚀 Desplegando Email Sender App en VPS"
echo "============================================"
echo "IP: $VPS_IP"
echo "Usuario: $VPS_USER"
echo "Puerto: 1482"
echo "Ruta remota: $REMOTE_PATH"
echo "============================================"

# Verificar si sshpass está instalado
if ! command -v sshpass &> /dev/null; then
    echo "⚠️  sshpass no está instalado. Instalando..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "Por favor instala sshpass manualmente o usa una conexión SSH manual."
        exit 1
    else
        sudo apt-get update && sudo apt-get install -y sshpass
    fi
fi

# Función para ejecutar comandos remotos
remote_exec() {
    sshpass -p "$VPS_PASS" ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_IP "$1"
}

# Función para subir archivos
upload_files() {
    echo "📤 Subiendo archivos al VPS..."
    
    # Crear directorio remoto
    remote_exec "mkdir -p $REMOTE_PATH"
    
    # Subir archivos usando scp
    sshpass -p "$VPS_PASS" scp -o StrictHostKeyChecking=no -r \
        docker-compose.yml \
        nginx-proxy.conf \
        backend \
        frontend \
        data \
        $VPS_USER@$VPS_IP:$REMOTE_PATH/ 2>/dev/null
    
    echo "✅ Archivos subidos correctamente"
}

# Crear estructura de directorios en el servidor
echo "📁 Creando estructura de directorios..."
remote_exec "mkdir -p $REMOTE_PATH/data"

# Subir archivos
upload_files

# Ejecutar comandos en el servidor
echo "🔧 Configurando servidor..."
remote_exec << 'ENDSSH'
cd /opt/email_sender

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "🐳 Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Instalando Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down 2>/dev/null

# Construir y levantar contenedores
echo "🔨 Construyendo contenedores..."
docker-compose build --no-cache

echo "🚀 Iniciando contenedores..."
docker-compose up -d

# Verificar que los contenedores estén corriendo
echo "⏳ Esperando a que los contenedores estén listos..."
sleep 10

# Mostrar estado de los contenedores
docker-compose ps

# Limpiar imágenes no utilizadas
docker image prune -f

ENDSSH

echo ""
echo "============================================"
echo "✅ Despliegue completado!"
echo "============================================"
echo "🌐 La aplicación está disponible en:"
echo "   http://$VPS_IP:1482"
echo ""
echo "📋 Credenciales de acceso:"
echo "   Usuario: Admin1"
echo "   Contraseña: Admin123"
echo ""
echo "📝 Comandos útiles:"
echo "   Ver logs: ssh $VPS_USER@$VPS_IP 'cd $REMOTE_PATH && docker-compose logs -f'"
echo "   Reiniciar: ssh $VPS_USER@$VPS_IP 'cd $REMOTE_PATH && docker-compose restart'"
echo "   Detener:   ssh $VPS_USER@$VPS_IP 'cd $REMOTE_PATH && docker-compose down'"
echo "============================================"