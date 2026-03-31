# ============================================
# INstrucciones de despliegue en el VPS
============================================

## Paso 1: Conectarse al servidor SSH

 Abre terminal y ejecuta:

```bash
ssh -o StrictHostKeyChecking=no root@187.124.224.233 "mkdir -p /opt/email_sender/data"
```

## Paso 2: subir archivos al VPS

Ahora vamos a ejecutar los comandos en el servidor:

. Si no hay de la contraseña de la complicada,, voy a http:// y con el servidor.

 con la contraseña "Configurar" y " el proceso.

## Paso 3: Ejecutar docker-compose

 el VPS

```bash
# 2. Crear directorio remoto
cd /remote_path
docker-compose build --no-cache
 docker-compose up -d
 echo "Despleiegue completado!"
 docker-compose ps
 echo "Estado de los contenedores"
 echo "Limpiando imagenes no utilizadas..."
docker image prune -f
 echo "Aplicacion disponible en"
 http://://$VPS_IP:1482