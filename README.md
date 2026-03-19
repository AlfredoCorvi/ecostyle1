# 🌿 EcoStyle — Plataforma de Moda Sostenible

Proyecto Django 4.2 + PostgreSQL + MercadoPago con arquitectura en 3 capas.

---

## 🗂️ Estructura del proyecto

```
ecostyle/
├── ecostyle/                  # Config principal del proyecto
│   ├── settings/
│   │   ├── base.py            # Configuración compartida
│   │   ├── development.py     # Debug=True, email en consola
│   │   └── production.py      # HTTPS, Redis, email real
│   ├── urls.py                # URL raíz
│   ├── wsgi.py
│   └── celery.py              # Tareas asíncronas
├── apps/
│   ├── accounts/              # Usuarios y perfiles
│   ├── products/              # Catálogo, categorías, reseñas
│   ├── cart/                  # Carrito + CartService
│   ├── orders/                # Órdenes y checkout
│   ├── payments/              # MercadoPago + PaymentService
│   └── inventory/             # Signals de stock automático
├── templates/                 # Capa de presentación
├── static/                    # CSS + JS
├── media/                     # Uploads (avatars, imágenes)
└── requirements/
    ├── base.txt
    ├── development.txt
    └── production.txt
```

---

## ⚙️ Instalación paso a paso

### 1. Requisitos previos
Instala Python 3.11+, PostgreSQL 15 y Git en tu sistema.

---

### 2. Clonar el repositorio (después de subir a GitHub)

```bash
git clone https://github.com/TU_USUARIO/ecostyle.git
cd ecostyle
```

---

### 3. Crear y activar entorno virtual

```bash
# En macOS / Linux
python3 -m venv venv
source venv/bin/activate

# En Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

---

### 4. Instalar dependencias

```bash
pip install -r requirements/development.txt
```

---

### 5. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus valores:

```env
DJANGO_SECRET_KEY=una-clave-secreta-muy-larga-y-aleatoria
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=ecostyle_db
DB_USER=ecostyle_user
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

MERCADOPAGO_PUBLIC_KEY=TEST-xxxxxxxx
MERCADOPAGO_ACCESS_TOKEN=TEST-xxxxxxxx
```

---

### 6. Crear la base de datos en PostgreSQL

```bash
# Entra al shell de PostgreSQL
psql -U postgres

# Ejecuta estos comandos dentro de psql:
CREATE DATABASE ecostyle_db;
CREATE USER ecostyle_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE ecostyle_db TO ecostyle_user;
\q
```

---

### 7. Aplicar migraciones

```bash
python manage.py makemigrations accounts
python manage.py makemigrations products
python manage.py makemigrations cart
python manage.py makemigrations orders
python manage.py makemigrations payments
python manage.py makemigrations inventory
python manage.py migrate
```

---

### 8. Crear superusuario (admin)

```bash
python manage.py createsuperuser
```

---

### 9. Cargar datos de prueba (opcional)

```bash
python manage.py loaddata initial_data.json
```

---

### 10. Recopilar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

---

### 11. Correr el servidor de desarrollo

```bash
python manage.py runserver
```

Abre en tu navegador: **http://127.0.0.1:8000**

Panel de administración: **http://127.0.0.1:8000/admin**

---

## 🚀 Subir a GitHub

### Primera vez (repositorio nuevo)

```bash
# Dentro del directorio ecostyle/
git init
git add .
git commit -m "feat: initial commit - EcoStyle Django project"

# Crea el repositorio en github.com y luego:
git remote add origin https://github.com/TU_USUARIO/ecostyle.git
git branch -M main
git push -u origin main
```

### Actualizaciones posteriores

```bash
git add .
git commit -m "feat: descripción de los cambios"
git push
```

---

## 📋 Comandos frecuentes de Django

```bash
# Crear nueva migración después de cambiar modelos
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Abrir shell de Django (útil para pruebas)
python manage.py shell

# Ver todas las URLs registradas
python manage.py show_urls

# Correr tests
python manage.py test

# Limpiar sesiones expiradas
python manage.py clearsessions
```

---

## 🗃️ Arquitectura de capas

| Capa | Componentes Django | Archivos |
|------|--------------------|----------|
| **Presentación** | Templates + Static | `templates/`, `static/` |
| **Negocio** | Views + Forms + Services + Signals | `views.py`, `forms.py`, `services.py`, `signals.py` |
| **Datos** | Models + ORM | `models.py`, `migrations/` |

---

## 🔑 Variables de entorno requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Clave secreta Django | Cadena aleatoria larga |
| `DJANGO_DEBUG` | Modo debug | `True` (dev) / `False` (prod) |
| `DB_NAME` | Nombre de la BD | `ecostyle_db` |
| `DB_USER` | Usuario PostgreSQL | `ecostyle_user` |
| `DB_PASSWORD` | Contraseña BD | tu password |
| `MERCADOPAGO_PUBLIC_KEY` | Clave pública MP | `TEST-xxx` |
| `MERCADOPAGO_ACCESS_TOKEN` | Token de acceso MP | `TEST-xxx` |

---

## 📦 Apps del proyecto

| App | Modelos | Servicio |
|-----|---------|----------|
| `accounts` | `UserProfile` | — |
| `products` | `Category`, `Product`, `ProductImage`, `Review` | — |
| `cart` | `Cart`, `CartItem` | `CartService` |
| `orders` | `Order`, `OrderItem` | — |
| `payments` | `Payment` | `PaymentService` |
| `inventory` | `StockMovement` | Signals automáticos |

---

## 🛠️ Stack tecnológico

- **Backend:** Python 3.11+ · Django 4.2 LTS
- **Base de datos:** PostgreSQL 15
- **Frontend:** Bootstrap 5 · CSS personalizado · Vanilla JS
- **Pagos:** MercadoPago SDK v2
- **Autenticación:** django-allauth
- **Archivos estáticos:** WhiteNoise
- **Tareas asíncronas:** Celery + Redis

---

## 🌿 Reglas del proyecto (para desarrollo)

1. **Nunca** lógica de negocio en templates
2. **Nunca** acceso directo a BD en vistas (siempre ORM)
3. Modelos con `constraints` en `Meta`
4. Cada app tiene su `urls.py`
5. **Preferir CBV** sobre FBV
6. Servicios complejos en `services.py`
7. Tareas asíncronas en `tasks.py`
