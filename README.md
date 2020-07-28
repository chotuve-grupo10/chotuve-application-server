# App server

## Estado del build
[![Build Status](https://travis-ci.com/chotuve-grupo10/chotuve-application-server.svg?branch=dev)](https://travis-ci.com/chotuve-grupo10/chotuve-application-server)

## Cobertura actual
[![codecov](https://codecov.io/gh/chotuve-grupo10/chotuve-application-server/branch/dev/graph/badge.svg)](https://codecov.io/gh/chotuve-grupo10/chotuve-application-server)

## Descripción
Este server será el responsable de conectar a los usuarios.
Se trata de una aplicación por consola destinada a mantenerse en ejecución por períodos prolongados de tiempo.
Este servidor se comunicará con los Shared servers ([Media server](https://github.com/chotuve-grupo10/chotuve-media-server) y [Auth server](https://github.com/chotuve-grupo10/chotuve-auth-server)). En el caso que la aplicación [Android](https://github.com/chotuve-grupo10/chotuve-android-app) necesite de algún servicio de los Shared Servers, el Application server actúa de fachada.

## Contenidos
1. [Correr el server localmente](#set-up-para-correr-el-app-server-localmente)
2. [Tests y linter](#tests-y-linter)
3. [CI/CD del server](#CI/CD)

## Set up para correr el app server localmente

Para poder correr el server localmente usaremos **Docker**. A continuación detallamos los comandos a ejecutar:

1. Buildear la imagen ejecutando en el directorio raiz del repo
```docker build . -t app-server```

2. Corremos el container ejecutando
    - ```docker run -e AUTH_SERVER_URL=https://chotuve-auth-server-dev.herokuapp.com -e MEDIA_SERVER_URL=https://chotuve-media-server-dev.herokuapp.com -e GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000" -p 8000:8000 --name app-server app-server```

    - Para hacer que las estadísticas se publiquen a Datadog, le agregamos al comando anterior la API key para el Datadog Agent: ```docker run -e AUTH_SERVER_URL=https://chotuve-auth-server-dev.herokuapp.com -e MEDIA_SERVER_URL=https://chotuve-media-server-dev.herokuapp.com -e DD_API_KEY=<DATADOG API KEY> -e GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000" -p 8000:8000 --name app-server app-server```

3. Si queremos eliminar el container creado
```docker rm -f app-server```

## Tests y linter

Tanto para ejecutar los tests y el linter, usaremos un **venv** para hacerlo. Debemos ejecutar los siguientes comandos:
1. En el directorio del repo, creamos el virtual env (solo esta vez por ser la primera):
```python3 -m venv my-venv```

2. Activamos el venv:
```source my-venv/bin/activate```

3. Instalamos las dependencias de todo el proyecto:
```pip install -e .```

### Ejecutar tests

1. Seteamos variables de entorno:
    - ```export AUTH_SERVER_URL=http://test```
    - ```export MEDIA_SERVER_URL=http://test```

2. Ejecutamos los tests:
```python -m pytest```

### Ejecutar linter

1. Ejecutar el linter en el modelo:
```PYTHONPATH=$(pwd) pylint app_server```

2. Ejecutar el linter en los tests:
```PYTHONPATH=$(pwd) pylint tests/*.py```


## CI/CD

### CI

Cada push que se haga al repo (sin importar la rama) lanzará un build en [Travis](https://travis-ci.com/).


### CD

Una vez que se haya terminado una tarea, se deberá crear un pull request para mergear a dev. Este pull request deberá ser revisado por al menos un miembro del equipo y deberá ser aprobado. Dejamos a continuación las direcciones del auth server tanto de desarrollo como productivo:

- [App server dev](https://chotuve-app-server-dev.herokuapp.com/)

- [App server prod](https://chotuve-app-server-production.herokuapp.com/)