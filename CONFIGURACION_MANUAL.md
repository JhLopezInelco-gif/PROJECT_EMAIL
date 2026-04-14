# Configuración Manual del Sistema de Envío de Correos Masivos

## Problemas Comunes y Soluciones

### 1. Error: "timeout: invalid time interval '/t'"
**Problema:** El comando `timeout` no es compatible con la versión de Windows.
**Solución:** Ya hemos corregido los scripts `iniciar_backend.bat` y `iniciar_todo.bat` para usar la sintaxis correcta.

### 2. Error: "solo se permite un uso de cada dirección de socket (protocolo/dirección de red/puerto)"
**Problema:** El puerto 7373 ya está en uso por otro proceso.
**Solución:** Ejecute el script `liberar_puerto.bat` para liberar el puerto.

## Pasos para Configuración Manual

### Paso 1: Liberar el Puerto 7373
Antes de iniciar el sistema, asegúrese de que el puerto 7373 esté libre:

```bash
# Ejecutar el script para liberar el puerto
liberar_puerto.bat
```

### Paso 2: Verificar Configuración SMTP
Revise el archivo `backend/.env` y asegúrese de que la configuración SMTP sea correcta:

```env
# SMTP Configuration
SMTP_HOST=mail.tablesa.com.co
SMTP_PORT=587
SMTP_USER=mesaayuda@tablesa.com.co
SMTP_PASSWORD=B^121587874931ux
SMTP_FROM=mesaayuda@tablesa.com.co
SMTP_FROM_NAME=Mesa de Ayuda Tablesa
SMTP_SECURITY=STARTTLS
SMTP_TIMEOUT=30
```

### Paso 3: Iniciar el Sistema
Opción A: Iniciar todo junto (recomendado):
```bash
iniciar_todo.bat
```

Opción B: Iniciar por separado:
```bash
# Iniciar backend primero
iniciar_backend.bat

# En otra terminal, iniciar frontend
iniciar_frontend.bat
```

### Paso 4: Verificar Funcionamiento
1. Abra su navegador y vaya a: `http://localhost:7171`
2. Inicie sesión con:
   - **Usuario:** Admin1
   - **Contraseña:** Admin123
3. Verifique que el backend esté funcionando: `http://localhost:7373/docs`

## Configuración SMTP Detallada

### Para Gmail:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=tu_contraseña_de_aplicacion
SMTP_FROM=tu_correo@gmail.com
SMTP_SECURITY=STARTTLS
```

### Para Outlook/Hotmail:
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=tu_correo@outlook.com
SMTP_PASSWORD=tu_contraseña
SMTP_FROM=tu_correo@outlook.com
SMTP_SECURITY=STARTTLS
```

### Para servidor empresarial (como Tablesa):
```env
SMTP_HOST=mail.tablesa.com.co
SMTP_PORT=587
SMTP_USER=mesaayuda@tablesa.com.co
SMTP_PASSWORD=contraseña_segura
SMTP_FROM=mesaayuda@tablesa.com.co
SMTP_SECURITY=STARTTLS
```

## Solución de Problemas

### 1. Si el backend no inicia:
- Ejecute `liberar_puerto.bat`
- Verifique que no haya otras instancias corriendo
- Reinicie su computadora si el problema persiste

### 2. Si hay problemas de conexión SMTP:
- Verifique las credenciales en `backend/.env`
- Confirme que el servidor SMTP esté accesible
- Pruebe con una conexión Telnet:
  ```bash
  telnet mail.tablesa.com.co 587
  ```

### 3. Si los correos no se envían:
- Verifique la configuración SMTP
- Revise los logs en la interfaz web
- Pruebe enviar un correo de prueba

### 4. Si el frontend no carga:
- Asegúrese de que el backend esté corriendo primero
- Verifique la configuración en `frontend/.env`
- Revise la consola del navegador para errores

## Comandos Útiles

### Diagnosticar el sistema:
```bash
diagnosticar.bat
```

### Liberar puertos:
```bash
liberar_puerto.bat
```

### Verificar logs:
- Los logs del backend se muestran en la terminal donde se ejecutó `iniciar_backend.bat`
- Los logs del frontend se muestran en la terminal donde se ejecutó `iniciar_frontend.bat`

## Configuración de Seguridad

### Cambiar credenciales por defecto:
En `backend/.env`, modifique estas líneas:
```env
ADMIN_USER=nuevo_usuario
ADMIN_PASSWORD=nueva_contraseña_segura
SECRET_KEY=nueva_clave_secreta_muy_larga_y_segura
```

### Configurar CORS para producción:
En `backend/app/main.py`, modifique la línea:
```python
allow_origins=["http://tu-dominio.com"]  # En lugar de ["*"]
```

## Envío de Correos Masivos

### 1. Preparar la lista de contactos:
- Crear un archivo CSV con las columnas: `email,nombre,apellido`
- Guardarlo en formato UTF-8

### 2. Cargar los contactos:
- Ir a la sección "Contactos" en la interfaz web
- Seleccionar el archivo CSV
- Esperar la confirmación de carga

### 3. Crear campaña:
- Ir a la sección "Campañas"
- Crear nueva campaña
- Seleccionar plantilla y contactos
- Programar envío o enviar inmediatamente

### 4. Monitorear envío:
- Revisar la sección "Logs" para ver el estado
- Verificar correos entregados, fallidos y pendientes

## Notas Importantes

1. **No cierre las ventanas de terminal** mientras el sistema esté en uso
2. **Para detener el sistema:** Cierre las ventanas de terminal o presione Ctrl+C
3. **Para reiniciar:** Cierre todas las terminales y ejecute `iniciar_todo.bat` nuevamente
4. **Mantenga segura su contraseña SMTP** - no comparta el archivo `.env`

Si necesita más ayuda, ejecute el script de diagnóstico y revise los mensajes de error.