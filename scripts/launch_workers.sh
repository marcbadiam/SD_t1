#!/bin/bash

# cargamos el numero de servidores desde el config o usamos 5 por defecto
NUM_SERVERS=5

echo "matando procesos previos de python para limpiar el entorno..."
pkill -f "direct_arch.worker_server"
pkill -f "direct_arch.proxy_lb"

echo "lanzando $NUM_SERVERS workers en segundo plano..."

for i in $(seq 0 $((NUM_SERVERS-1)))
do
    # lanzamos cada worker y redirigimos su salida a un log individual
    # el & al final los manda al background
    python3 -m direct_arch.worker_server $i > "worker_$i.log" 2>&1 &
    echo "worker $i arrancado (log en worker_$i.log)"
done

echo "todos los workers estan en marcha"