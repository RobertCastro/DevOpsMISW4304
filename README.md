``` bash
/
│
├── app/
│   ├── __init__.py        # Inicialización del paquete Flask
│   ├── models.py          # Definición de modelos (SQLAlchemy)
│   ├── routes.py          # Definición de rutas (endpoints RESTful)
│   └── utils.py           # Funciones auxiliares (ej. manejo de JWT, validaciones)
├── coleccion-postman      # .json con la colección de postman con la documentación del API
├── application.py         # Script principal para correr la aplicación
├── Dockerfile             # Dockerfile para empaquetar la app en un contenedor
├── requirements.txt       # Dependencias de la aplicación
├── .ebextensions/         # Configuraciones adicionales para Elastic Beanstalk
│   └── flask.config        # Configuración personalizada para Elastic Beanstalk
├── .gitignore             # Archivos y directorios a ignorar por git
└── README.md              # Instrucciones y documentación del proyecto

```


Descripción de los archivos y carpetas:
- **/app/**: Contiene la lógica de la aplicación Flask, incluyendo modelos, rutas, y utilidades.
- **application.py**: Archivo principal de la aplicación que define la lógica para Flask.
- **Dockerfile**: Definición de la imagen Docker para empaquetar y desplegar la aplicación en AWS.
- **requirements.txt**: Las dependencias necesarias para correr la aplicación.
- **runtime.txt**: Define la versión de Python que se usará en Elastic Beanstalk.
- **.ebextensions/**: Contiene archivos de configuración para ajustar el entorno en Elastic Beanstalk.
- **README.md**: Instrucciones y detalles del proyecto.

Esta estructura está pensada para facilitar el despliegue en Elastic Beanstalk, además de organizar adecuadamente el código.


## Despliegue manual en Elastic Beanstalk

- Comprimir en un zip: /app application.py requirements.txt .ebextensions
- Cargar e implementar en Elastic Beanstalk
- Configurar variables de entorno en Elastic Beanstalk

## Despliegue con imagen de Docker Elastic Beanstalk

### Autenticar Docker CLI con el Amazon Elastic Container Registry
``` bash
aws --profile [perfil-aws] ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 061039766984.dkr.ecr.us-east-2.amazonaws.com
```

### Crear y subir imagen

``` bash
docker build -t blacklist_app .
docker tag blacklist_app:latest 061039766984.dkr.ecr.us-east-2.amazonaws.com/blacklistservice:latest
docker push 061039766984.dkr.ecr.us-east-2.amazonaws.com/blacklistservice:latest

```
### Desplegar en Elastic Beanstalk

``` bash
- Crear entorno Elastic Beanstalk con Docker
- Agregar variables de entorno
- Copiar URI de imagen de ECR en Dockerrun.aws.json
- Cargar e implementar Elastic Beanstalk subiendo Dockerrun.aws.json

```

## Ejecutar local

### Iniciar todos los servicios en el puerto por defecto
``` bash
 chmod +x scripts/local.sh
 ./scripts/local.sh

```

### Iniciar todos los servicios con un puerto personalizado (ejemplo 3000)
``` bash
 chmod +x scripts/local.sh
 ./scripts/local.sh 3000

```

### Iniciar unicamente base de datos
``` bash
 chmod +x scripts/db.sh
 ./scripts/db.sh

```

### Ejecutar unicamente aplicación

``` bash
 docker build -t blacklist_app .
 docker run -d -p 5000:5000 --name flask_app blacklist_app

```

### Token necesario en los requests

Los requests necesitan un token el cual es estatico por ahora y seria:

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.3J-lwqipiMTiRzWCEjuey3v-n7pjDTBV1FZBpHx6plI
```

## Ejecutar Tests

``` bash
export FLASK_ENV=testing
pytest tests/
```


test ci/cd 1
test ci/cd 2
test ci/cd 3


