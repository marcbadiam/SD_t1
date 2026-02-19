### Instalación de dependencias
sudo apt update
sudo apt install redis-server rabbitmq-server python3-pip -y
pip3 install -r requirements.txt

### Ejecución de la Arquitectura Directa (Pyro5)

1. Iniciar el Pyro5 Name Server:
```bash
pyro5-ns
```
2. Limpiar Redis y lanzar los workers:
```bash
./scripts/flush_redis.sh
./scripts/launch_workers.sh
```
3. Lanzar el proxy:
```bash
python3 -m direct_arch.proxy_lb
```
4. Probar el sistema:
```bash
python3 -m client.benchmark_runner benchmarks/benchmark_unnumbered_20000.txt direct
```

### Ejecución de la Arquitectura Indirecta (RabbitMQ)

1. Limpiar Redis y lanzar los workers:
```bash
./scripts/flush_redis.sh
./scripts/launch_indirect_workers.sh
```
2. Lanzar el proxy:
```bash
python3 -m indirect_arch.proxy_lb
```
3. Probar el sistema:
```bash
python3 -m client.benchmark_runner benchmarks/benchmark_unnumbered_20000.txt indirect
```
4. Comprobar el numero de tickets vendidos:
```bash
redis-cli get global_tickets_sold
```