# AVS-mark-register-API-backend
Backend from AVS to register timeline marks to edit videos

## Pasos para correr el proyecto del app en local
```
    cd CarpetaDelProyecto
```
- Configure un entorno virtual en un directorio llamado venv con el comando:
```
    linux:
    virtualenv -p /usr/bin/python3.8 venv
    windows:
    virtualenv venv
```
- Activar el entorno virtual con:
``` 
    #para windows
        venv\Scripts\activate
    #para linux
        source venv/bin/activate
    pip install -r requirements.txt
    #para windows
        set FLASK_APP=app.py
    #para linux
        export FLASK_APP=app.py
    pip install -r requirements.txt
    flask db init
    flask db migrate
    flask db upgrade
    #Para Linux:
        python $FLASK_APP
    #Para Windows:
        python %FLASK_APP%
```
- Con eso podremos probar la aplicación de manera local
## Pasos para correr el test del app en local
```
    cd CarpetaDelProyecto
```
- Ejecutar el test
``` 
pytest --cov=app/src > test_evidence.txt
```
## Para tener un listado completo de tus librerías de python usa el comando:
```
pip freeze > requirements.txt
```
- Con eso tendrás en tu archivo requirements.txt las librerías con las versiones exactas que se instalarán en el docker image.
