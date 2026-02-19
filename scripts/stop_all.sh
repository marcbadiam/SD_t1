#!/bin/bash

# script para limpiar todo el entorno distribuido
echo "deteniendo workers, proxy y servidor de nombres..."

pkill -f "direct_arch.worker_server"
pkill -f "direct_arch.proxy_lb"
pkill -f "pyro5-ns"

echo "limpieza completada"