# Chotuve-application-server

## Set up para correr el app server

1. Clonar el repo:  
```git clone https://github.com/chotuve-grupo10/chotuve-application-server.git```

2. En el directorio del repo, creamos el virtual env (solo esta vez por ser la primera):  
```python3 -m venv my-venv```

3. Activamos el venv:  
```source my-venv/bin/activate```

4. Instalamos las dependencias de todo el proyecto:   
```pip install -e .```   

5. Hacemos export de ciertas variables (Acá hay que revisar esto, deberíamos mandarlo a un archivo de configuración si entendí bien lo que dijo ayer gonzalo. Por otro lado, no sé para qué sirve la variable development. Creo que es para avisarle a flask el modo en el que corre):
```export FLASK_APP=flaskr```   
```export FLASK_ENV=development```   

5. Corremos el server localmente:  
```flask run```

## Server en heroku

- Actualmente el server esta corriendo en heroku en la siguiente direccion:   
https://chotuve-app-server-production.herokuapp.com/
Por ahora esta corriendo en prod pero esta dentro de un pipeline para que podamos setear otros ambientes.


