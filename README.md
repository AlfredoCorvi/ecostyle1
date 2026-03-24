
--------------------------------------------------------------------------------
1. INSTALACIÓN Y CONFIGURACIÓN LOCAL
--------------------------------------------------------------------------------
  Prerrequisitos
  --------------
  · Python 3.14
  · PostgreSQL 15 corriendo localmente
  · Git
  . Crear una carpeta e ingresar a la carpeta para clonar el repo

  Pasos
  -----
  1. Clonar el repositorio
       git clone https://github.com/ecostyle/ecostyle-platform.git
       cd ecostyle-platform

  2. Crear y activar entorno virtual
       python -m venv .venv
       source .venv/bin/activate          # Linux / macOS
       .venv\Scripts\activate             # Windows

  3. Instalar dependencias
       pip install -r requirements.txt

  4. Configurar variables de entorno
       cp .env.example .env
       # Editar .env con tus valores locales (ver sección 11)

  5. Crear la base de datos en PostgreSQL
       createdb ecostyle_db

  6. Aplicar migraciones
       python manage.py migrate

  7. Crear superusuario
       python manage.py createsuperuser

  8. Cargar datos iniciales (fixtures de categorías y productos demo)
       python manage.py loaddata apps/products/fixtures/categories.json
       python manage.py loaddata apps/products/fixtures/demo_products.json

  9. Recolectar archivos estáticos (producción)
       python manage.py collectstatic

  10. Levantar servidor de desarrollo
        python manage.py runserver

  11. (Opcional) Iniciar worker de Celery
        celery -A config worker -l info

--------------------------------------------------------------------------------
2. COMANDOS ÚTILES
--------------------------------------------------------------------------------
  # Desarrollo
  python manage.py runserver                    Servidor local (puerto 8000)
  python manage.py shell_plus                   Shell interactivo (django-extensions)
  python manage.py makemigrations <app>         Crear migraciones para una app
  python manage.py migrate                      Aplicar todas las migraciones
  python manage.py createsuperuser             Crear admin
  python manage.py test apps.<app>             Ejecutar tests de una app
  python manage.py test                        Ejecutar todos los tests

  # Datos
  python manage.py dumpdata <app> --indent 2   Exportar datos a JSON
  python manage.py loaddata <fixture.json>     Importar datos desde JSON

  # Celery
  celery -A config worker -l info              Iniciar worker
  celery -A config beat -l info                Iniciar scheduler de tareas

  # Calidad de código
  flake8 apps/                                 Linter PEP8
  black apps/                                  Formateo automático
  isort apps/                                  Ordenar imports

--------------------------------------------------------------------------------
3. FLUJO DE TRABAJO GIT
--------------------------------------------------------------------------------
  Ramas principales
  -----------------
  · main          → Producción.
  · develop       → Rama de integración principal

  Convención de commits (Conventional Commits)
  --------------------------------------------
  feat(products): agregar filtro por material sostenible
  fix(cart): corregir cálculo de descuento con cupones
  docs(readme): actualizar sección de instalación
  refactor(orders): extraer lógica de totales a OrderService
  test(accounts): agregar tests para RegisterView

================================================================================