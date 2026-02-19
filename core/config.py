import os

# configuracion del cluster y sharding
# numero de servidores para calcular el modulo
NUM_SERVERS = int(os.getenv("NUM_SERVERS", 5))

# configuracion de redis como backend de consistencia
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# variables para la arquitectura directa con pyro5
# ip y puerto del proxy que hace de balanceador
PROXY_HOST = os.getenv("PROXY_HOST", "localhost")
PROXY_PORT = int(os.getenv("PROXY_PORT", 9099))

# prefijo para registrar los workers en el servidor de nombres
PYRO_WORKER_PREFIX = "TicketWorker_"

# variables para la arquitectura indirecta con rabbitmq
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

# nombres del exchange y la cola para tickets no numerados
EXCHANGE_NAME = "ticket_exchange"
UNNUMBERED_QUEUE = "unnumbered_queue"
# las colas numeradas se crean luego dinamicamente