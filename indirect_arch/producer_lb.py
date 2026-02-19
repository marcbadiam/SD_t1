import pika
import sys
from core.config import (
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, 
    RABBITMQ_PASS, EXCHANGE_NAME, NUM_SERVERS
)

class ProducerLB:
    def __init__(self):
        # conexion inicial con rabbitmq
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # declaramos el exchange para que exista antes de mandar mensajes
        self.channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='direct')
        self.rr_counter = 0

    def send_request(self, params):
        # logica de sharding para elegir el worker
        if len(params) == 4:
            # caso numerado: modulo del seat_id
            seat_id = int(params[2])
            worker_index = seat_id % NUM_SERVERS
        else:
            # caso no numerado: round robin
            worker_index = self.rr_counter % NUM_SERVERS
            self.rr_counter += 1

        # convertimos la lista de parametros en un string separado por espacios
        message = " ".join(params)
        routing_key = f"worker.{worker_index}"

        # publicamos el mensaje en el exchange
        self.channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # hace que el mensaje sea persistente
            )
        )

    def close(self):
        self.connection.close()

if __name__ == "__main__":
    # este main es solo para pruebas rapidas del producer
    if len(sys.argv) < 2:
        print("uso: python3 -m indirect_arch.producer_lb BUY user1 req1")
        sys.exit(1)
    
    lb = ProducerLB()
    lb.send_request(sys.argv[1:])
    lb.close()
    print("mensaje enviado a la cola")