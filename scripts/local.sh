#!/bin/bash

# Navegar a la carpeta raíz del proyecto
cd "$(dirname "$0")/.."

# Verificar si se pasa por parámetros el puerto para Flask
FLASK_PORT=${1:-5000}

# Detener y eliminar cualquier contenedor existente de la base de datos o la aplicación
echo "Eliminando contenedores existentes..."
docker rm -f blacklist_db_container flask_app_blacklist 2>/dev/null || true

# Eliminar las imágenes anteriores si existen
echo "Eliminando imágenes de Docker anteriores..."
docker rmi -f blacklist_db blacklist_app 2>/dev/null || true

# Configurar variables de entorno
export RDS_USERNAME=postgres
export RDS_PASSWORD=postgres
export RDS_HOSTNAME=localhost
export RDS_DB_NAME=postgres
export RDS_PORT=5432

# Imprimir las variables de entorno
echo "Variables de entorno configuradas:"
echo "RDS_USERNAME=$RDS_USERNAME"
echo "RDS_PASSWORD=$RDS_PASSWORD"
echo "RDS_HOSTNAME=$RDS_HOSTNAME"
echo "RDS_DB_NAME=$RDS_DB_NAME"
echo "RDS_PORT=$RDS_PORT"

# Navegar a la carpeta /scripts para construir la base de datos
cd scripts

# Crear la imagen Docker de la base de datos PostgreSQL 16
echo "Construyendo la imagen Docker para PostgreSQL..."
docker build -t blacklist_db .

# Levantar el contenedor de la base de datos PostgreSQL
echo "Levantando el contenedor PostgreSQL en el puerto 5432..."
docker run --name blacklist_db_container -e POSTGRES_USER=$RDS_USERNAME -e POSTGRES_PASSWORD=$RDS_PASSWORD -e POSTGRES_DB=$RDS_DB_NAME -p 5432:5432 -d blacklist_db

# Esperar a que el contenedor de PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
sleep 10 

# Verificar si el contenedor de PostgreSQL está corriendo
docker ps | grep blacklist_db_container
if [ $? -ne 0 ]; then
  echo "El contenedor de PostgreSQL no está corriendo. Abortando."
  exit 1
fi

# Regresar a la carpeta raíz del proyecto para construir la aplicación Flask
cd ..

# Crear la imagen Docker de la aplicación Flask
echo "Construyendo la imagen Docker para la aplicación Flask..."
docker build -t blacklist_app .

# Levantar el contenedor de la aplicación Flask
echo "Levantando el contenedor de la aplicación Flask en el puerto $FLASK_PORT..."
docker run -d -p ${FLASK_PORT}:${FLASK_PORT} --name flask_app_blacklist -e FLASK_PORT=$FLASK_PORT blacklist_app

# Confirmar que el contenedor de la aplicación Flask está corriendo
docker ps | grep flask_app_blacklist
if [ $? -ne 0 ]; then
  echo "El contenedor de la aplicación Flask no está corriendo. Abortando."
  exit 1
fi

echo "Todos los contenedores están corriendo correctamente."
