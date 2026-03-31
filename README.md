Intrucciones para clonar repositorio

REQUISITOS
Tener instalado Python, PostgreeSQL, Git y un IDE.

PASOS PARA CLONAR Y CONFIGURAR PROYECTO
1. Crea una carpeta para el proyecto y entra en ella
2. Abre esa carpeta en el cmd y ejecuta el comando: code .
3. En tu IDE presiona el comando: ctrl + ñ para abrir la terminal del IDE
4. En la terminal ejecuta el siguiente comando: git clone https://github.com/AlfredoCorvi/ecostyle1.git
5. Ejecutar comando: cd ecostyle1
6. Ejecutar comandos para activar entorno virtual e instalar librerías:\\
python -m venv venv\\
venv\Scripts\activate    (esperar a que se active el prefijo venv de color varde antes de ejecutar el sig comando)\\
pip install -r requirements.txt\\

7. Ejecutar los siguientes comandos para inicializar la base de datos \\
psql -U postgres\\
CREATE DATABASE ecostyle_db;\\
CREATE USER ecostyle_user WITH PASSWORD '' \\
GRANT ALL PRIVILEGES ON DATABASE ecostyle_db TO ecostyle_user;\\

8. Ejecutar los siguientes comandos para crear las migraciones en la base de datos:\\
python manage.py migrate\\
python manage.py createsuperuser  (acuerdate de la contraseña y usuario que pongas)\\

9. Editar variables de entorno según tus credenciales.
