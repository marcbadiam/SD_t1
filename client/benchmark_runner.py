import time
import sys
import Pyro5.api
from indirect_arch.producer_lb import ProducerLB
from core.config import PROXY_HOST, PROXY_PORT

def run_benchmark(file_path, mode):
    try:
        with open(file_path, 'r') as file:
            lineas = file.readlines()
    except FileNotFoundError:
        print(f"error: no se encuentra el archivo {file_path}")
        return

    # configuracion segun el modo elegido
    proxy_directo = None
    producer_indirecto = None

    if mode == "direct":
        uri_proxy = f"PYRO:ProxyLB@{PROXY_HOST}:{PROXY_PORT}"
        proxy_directo = Pyro5.api.Proxy(uri_proxy)
        print("modo: arquitectura directa (pyro5)")
    else:
        producer_indirecto = ProducerLB()
        print("modo: arquitectura indirecta (rabbitmq)")

    exitos = 0
    fallos = 0
    peticiones_procesadas = 0
    
    print(f"analizando archivo...")
    start_time = time.time()

    for linea in lineas:
        params = linea.strip().split()
        if not params or params[0] != "BUY":
            continue
            
        peticiones_procesadas += 1

        try:
            if mode == "direct":
                resultado = proxy_directo.process_request(params)
                if resultado == "SUCCESS": exitos += 1
                else: fallos += 1
            else:
                # en indirecto, el 'exito' es que el mensaje entre en la cola
                producer_indirecto.send_request(params)
                exitos += 1
                
        except Exception as e:
            print(f"error en peticion: {e}")
            fallos += 1

    if producer_indirecto:
        producer_indirecto.close()

    end_time = time.time()
    tiempo_total = end_time - start_time
    throughput = peticiones_procesadas / tiempo_total if tiempo_total > 0 else 0

    print("\n--- resultados del benchmark ---")
    print(f"modo: {mode} | archivo: {file_path}")
    print(f"tiempo total: {tiempo_total:.2f} segundos")
    print(f"throughput: {throughput:.2f} ops/segundo")
    if mode == "direct":
        print(f"exitos/fallos reales: {exitos}/{fallos}")
    else:
        print(f"mensajes encolados: {exitos}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("uso: python3 -m client.benchmark_runner <archivo> <direct|indirect>")
        sys.exit(1)
        
    run_benchmark(sys.argv[1], sys.argv[2])