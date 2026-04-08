# Instrucciones de Despliegue - Email Sender App

## Datos del Servidor
- **IP:** 187.124.224.233
- **Puerto:** 1482
- **Usuario:** root
- **Contraseña:** PK900old.ZaX@

---

## PASO 1: Conectar al servidor

Abre una terminal (PowerShell o CMD) y ejecuta:

```bash
ssh root@187.124.224.233
```

Cuando te pida la contraseña, ingresa: `PK900old.ZaX@`

---

## PASO 2: Crear directorio en el servidor

Una vez conectado al servidor, ejecuta:

```bash
mkdir -p /opt/email_sender/data
cd /opt/email_sender
```

---

## PASO 3: Subir archivos desde tu PC local

Abre **OTRA terminal** en tu PC local (en la carpeta del proyecto `c:\project_Email`) y ejecuta estos comandos uno por uno:

```bash
scp docker-compose.yml root@187.124.224.233:/opt/email_sender/
```

```bash
scp nginx-proxy.conf root@187.124.224.233:/opt/email_sender/
```

```bash
scp -r backend root@187.124.224.233:/opt/email_sender/
```

```bash
scp -r frontend root@187.124.224.233:/opt/email_sender/
```

```bash
scp -r data root@187.124.224.233:/opt/email_sender/
```

Te pedirá la contraseña cada vez: `PK900old.ZaX@`

---

## PASO 4: Construir y levantar contenedores

Vuelve a la terminal del servidor (donde estás conectado por SSH) y ejecuta:

```bash
cd /opt/email_sender
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose ps
```

---

## PASO 5: Verificar

La aplicación estará disponible en:
- **URL:** http://187.124.224.233:1482

**Credenciales de acceso:**
- Usuario: Admin1
- Contraseña: Admin123

---

## Comandos útiles

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Detener
docker-compose down

# Ver estado
docker-compose ps