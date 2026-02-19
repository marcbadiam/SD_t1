import sys
import pika
from core.logic import SaleFactory
from core.config import (
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, 
    RABBITMQ_PASS, EXCHANGE_NAME
)

def callback(ch, method, properties, body):
    # esta funcion se ejecuta cada vez que llega un mensaje a la cola
    # el cuerpo del mensaje viene como bytes, lo decodificamos
    mensaje = body.decode()
    params = mensaje.split()
    
    print(f"-> mensaje recibido: {mensaje}")
    
    try:
        # reutilizamos la factory y la logica que ya tenemos
        estrategia = SaleFactory.create_strategy(params)
        
        if len(params) == 4:
            client_id, seat_id, request_id = params[1], params[2], params[3]
        else:
            client_id, request_id = params[1], params[2]
            seat_id = None
            
        resultado = estrategia.execute(client_id, request_id, seat_id)
        print(f"resultado: {resultado}")
        
    except Exception as e:
        print(f"error procesando mensaje: {e}")

    # confirmamos a rabbitmq que el mensaje ha sido procesado
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker(worker_index):
    # configuracion de la conexion
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # declaramos el exchange de tipo 'direct' para el sharding
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='direct')

    # cada worker tiene su propia cola basada en su indice
    queue_name = f"queue_worker_{worker_index}"
    channel.queue_declare(queue=queue_name, durable=True)

    # vinculamos la cola al exchange con una routing key especifica
    # ej: el worker 0 solo escucha mensajes marcados como 'worker.0'
    routing_key = f"worker.{worker_index}"
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=routing_key)

    print(f"worker indirecto {worker_index} escuchando en cola {queue_name}...")
    
    # configuramos para que rabbitmq no mande mas de un mensaje a la vez a este worker
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    channel.start_consuming()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python3 -m indirect_arch.worker_consumer <numero_worker>")
        sys.exit(1)
        
    index = int(sys.argv[1])
    start_worker(index)