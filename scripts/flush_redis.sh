#!/bin/bash

# script para limpiar la base de datos redis
# se debe ejecutar siempre antes de lanzar un benchmark nuevo

echo "limpiando todas las claves de redis local..."
redis-cli FLUSHALL
echo "redis esta vacio y listo para la siguiente prueba"