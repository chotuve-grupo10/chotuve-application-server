# Chotuve-application-server

## Set up para correr el app server

1. Clonar el repo:  
```git clone https://github.com/chotuve-grupo10/chotuve-application-server.git```

2. En el directorio del repo, creamos el container de Docker:  
```docker build . -t application-server```

3. Corremos el docker y nos conectamos a través del puerto 8080:  
```docker run --name application-server -p 8080:5000 application-server```

## Server en heroku

- Actualmente el server esta corriendo en heroku en las siguientes direcciones:   
https://chotuve-app-server-production.herokuapp.com/
https://chotuve-app-server-dev.herokuapp.com/



