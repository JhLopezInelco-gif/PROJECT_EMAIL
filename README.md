# 📧 Sistema de Envío de Correos en Masa

Aplicación completa para gestión y envío masivo de correos electrónicos con frontend React y backend FastAPI.

## 🚀 Características

- **🔐 Autenticación JWT**: Sistema de login seguro con tokens
- **📤 Carga CSV**: Importar contactos desde archivos CSV
- **✉️ Envío Masivo**: Enviar correos a múltiples destinatarios
- **📊 Seguimiento**: Progreso en tiempo real de envíos
- **📝 Registro**: Historial completo de correos enviados
- **🗄️ PostgreSQL**: Base de datos robusta con creación automática

## 📋 Requisitos Previos

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (opcional, SQLite incluido por defecto)

## ⚙️ Configuración

### 1. Clonar y configurar Backend

```bash
# Ir al directorio del backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar archivo de configuración
copy .env.example .env
```

### 2. Configurar variables de entorno

Edite el archivo `backend/.env`:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/email_sender

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# SMTP Configuration (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_NAME=Sistema de Correos

# Admin Credentials
ADMIN_USER=Admin1
ADMIN_PASSWORD=Admin123
```

**Nota para Gmail**: Debe generar una "Contraseña de aplicación" en su cuenta de Google.

### 3. Configurar Frontend

```bash
# Ir al directorio del frontend
cd frontend

# Instalar dependencias
npm install
```

## 🏃 Ejecutar la Aplicación

### Backend

```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 7373
```

El backend estará disponible en: `http://localhost:7373`
Documentación API: `http://localhost:7373/docs`

### Frontend

```bash
cd frontend
npm start
```

El frontend estará disponible en: `http://localhost:7171`

## 🔑 Credenciales de Acceso

- **Usuario**: `Admin1`
- **Contraseña**: `Admin123`

## 📁 Estructura del Proyecto

```
project_Email/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Aplicación FastAPI
│   │   ├── config.py            # Configuración
│   │   ├── database.py          # Conexión PostgreSQL
│   │   ├── models.py            # Modelos SQLAlchemy
│   │   ├── schemas.py           # Esquemas Pydantic
│   │   ├── auth.py              # Autenticación JWT
│   │   ├── email_service.py     # Servicio SMTP
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py          # Rutas de autenticación
│   │       ├── correos.py       # Rutas de contactos
│   │       └── emails.py        # Rutas de envío
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.js
│   │   │   ├── Layout.js
│   │   │   ├── Dashboard.js
│   │   │   ├── Correos.js
│   │   │   ├── CargarCSV.js
│   │   │   ├── EnviarCorreos.js
│   │   │   ├── Campanas.js
│   │   │   └── Logs.js
│   │   ├── context/
│   │   │   └── AuthContext.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.js
│   │   ├── index.js
│   │   └── index.css
│   └── package.json
├── data/
│   └── contactos_ejemplo.csv
└── README.md
```

## 📊 Base de Datos

La aplicación crea automáticamente las siguientes tablas:

### Tabla: correos
| Campo | Tipo |
|-------|------|
| id | SERIAL PRIMARY KEY |
| codigo | VARCHAR(20) |
| razon_social | VARCHAR(255) |
| tipo_tercero | VARCHAR(100) |
| numero_identificacion | VARCHAR(50) |
| email | VARCHAR(255) |

### Tabla: email_logs
| Campo | Tipo |
|-------|------|
| id | SERIAL PRIMARY KEY |
| correo_id | INTEGER |
| email | VARCHAR(255) |
| subject | VARCHAR(500) |
| body | TEXT |
| status | VARCHAR(20) |
| error_message | TEXT |
| sent_at | TIMESTAMP |

### Tabla: email_campaigns
| Campo | Tipo |
|-------|------|
| id | SERIAL PRIMARY KEY |
| name | VARCHAR(255) |
| subject | VARCHAR(500) |
| body | TEXT |
| total_recipients | INTEGER |
| sent_count | INTEGER |
| failed_count | INTEGER |
| status | VARCHAR(20) |

## 📤 Formato CSV

El archivo CSV debe tener el siguiente formato:

```csv
Código,Razón social,Tipo de tercero,Numero identificacion,Email
800061260,EMPRESA SAS,Persona jurídica,800061260-1,correo@empresa.com
```

**Columnas reconocidas:**
- `Código` / `codigo` - Código del contacto
- `Razón social` / `razon_social` - Nombre o empresa
- `Tipo de tercero` / `tipo_tercero` - Persona jurídica/natural
- `Numero identificacion` / `numero_identificacion` - NIT o documento
- `Email` / `email` - Correo electrónico (requerido)

## 🔌 API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Usuario actual
- `POST /api/auth/verify` - Verificar token

### Contactos
- `GET /api/correos` - Listar contactos
- `GET /api/correos/{id}` - Obtener contacto
- `POST /api/correos` - Crear contacto
- `PUT /api/correos/{id}` - Actualizar contacto
- `DELETE /api/correos/{id}` - Eliminar contacto
- `POST /api/correos/upload-csv` - Cargar CSV

### Correos
- `POST /api/emails/send` - Enviar correos
- `GET /api/emails/progress/{id}` - Progreso de envío
- `GET /api/emails/campaigns` - Listar campañas
- `GET /api/emails/logs` - Registro de envíos
- `POST /api/emails/test` - Enviar correo de prueba
- `GET /api/emails/stats` - Estadísticas

## 🛡️ Seguridad

- Autenticación JWT con expiración configurable
- Validación de emails antes de enviar
- Sanitización de inputs
- Protección de rutas en frontend
- Contraseñas hasheadas (producción)

## 📧 Configuración SMTP

### Gmail
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Outlook
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
```

### SendGrid
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

## ⚠️ Notas Importantes

1. **Evitar SPAM**: Los correos se envían con un delay de 2 segundos entre cada uno
2. **Límites SMTP**: Revise los límites de su proveedor de correo
3. **Gmail**: Use contraseñas de aplicación, no su contraseña principal
4. **Producción**: Cambie SECRET_KEY y las credenciales admin

## 📝 Licencia

MIT License

## 👨‍💻 Autor

Generado para gestión de envío de correos masivos