#!/bin/bash

# Crear la imagen Docker de la base de datos PostgreSQL 16
echo "Construyendo la imagen Docker para PostgreSQL..."
docker build -t blacklist_db .

# Levantar el contenedor de la base de datos PostgreSQL
echo "Levantando el contenedor PostgreSQL en el puerto 5432..."
docker run --name blacklist_db_container -e POSTGRES_USER=$RDS_USERNAME -e POSTGRES_PASSWORD=$RDS_PASSWORD -e POSTGRES_DB=$RDS_DB_NAME -p 5432:5432 -d blacklist_db

# Esperar a que el contenedor de PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
sleep 10  # Puedes ajustar el tiempo de espera según sea necesario

# Verificar si el contenedor de PostgreSQL está corriendo
docker ps | grep blacklist_db_container
if [ $? -ne 0 ]; then
  echo "El contenedor de PostgreSQL no está corriendo. Abortando."
  exit 1
fi

echo "PostgreSQL Ok"
