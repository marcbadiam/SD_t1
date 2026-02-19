import Pyro5.api
from core.config import NUM_SERVERS, PROXY_HOST, PROXY_PORT, PYRO_WORKER_PREFIX

@Pyro5.api.expose
class LoadBalancer:
    def __init__(self):
        # contador simple para el round robin de tickets no numerados
        self.rr_counter = 0

    def process_request(self, params):
        # params es la linea del benchmark separada por espacios
        
        if len(params) == 4:
            # caso numerado: buy client_id seat_id request_id
            # extraemos el asiento y calculamos el modulo
            seat_id = int(params[2])
            worker_index = seat_id % NUM_SERVERS
        else:
            # caso no numerado: buy client_id request_id
            # usamos round robin para repartir la carga
            worker_index = self.rr_counter % NUM_SERVERS
            self.rr_counter += 1

        # construimos el nombre con el que el worker se registro en pyro
        worker_name = f"PYRONAME:{PYRO_WORKER_PREFIX}{worker_index}"
        
        try:
            # conectamos con el worker especifico y le pasamos el trabajo
            with Pyro5.api.Proxy(worker_name) as worker:
                resultado = worker.execute_sale(params)
                return resultado
        except Exception as e:
            # si el worker cae o no esta disponible
            print(f"error conectando al worker {worker_index}: {e}")
            return "ERROR"

def start_proxy():
    # iniciamos el demonio pyro para escuchar peticiones del cliente
    daemon = Pyro5.api.Daemon(host=PROXY_HOST, port=PROXY_PORT)
    uri = daemon.register(LoadBalancer, "ProxyLB")
    
    print(f"load balancer iniciado en {uri}")
    print(f"usando sharding para {NUM_SERVERS} servidores")
    
    # el proxy se queda escuchando
    daemon.requestLoop()

if __name__ == "__main__":
    start_proxy()