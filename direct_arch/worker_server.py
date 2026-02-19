import sys
import Pyro5.api
from core.logic import SaleFactory
from core.config import PYRO_WORKER_PREFIX

@Pyro5.api.expose
class TicketWorker:
    def execute_sale(self, params):
        # chivato para ver que esta pasando en la red
        print(f"-> peticion entrante: {params} | tipo: {type(params)} | len: {len(params)}")
        
        try:
            estrategia = SaleFactory.create_strategy(params)
            
            if len(params) == 4:
                client_id = params[1]
                seat_id = params[2]
                request_id = params[3]
            else:
                client_id = params[1]
                request_id = params[2]
                seat_id = None
                
            resultado = estrategia.execute(client_id, request_id, seat_id)
            return resultado
            
        except Exception as e:
            print(f"fallo al procesar ticket: {e}")
            return "ERROR"

def start_worker(worker_index):
    daemon = Pyro5.api.Daemon()
    ns = Pyro5.api.locate_ns()
    
    uri = daemon.register(TicketWorker)
    worker_name = f"{PYRO_WORKER_PREFIX}{worker_index}"
    ns.register(worker_name, uri)
    
    print(f"worker {worker_index} arrancado con exito y actualizado")
    print("esperando peticiones del balanceador...")
    daemon.requestLoop()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("error: falta el indice del worker")
        sys.exit(1)
        
    index = int(sys.argv[1])
    start_worker(index)