import redis
from abc import ABC, abstractmethod
from core.config import REDIS_HOST, REDIS_PORT, REDIS_DB

class RedisConnection:
    # patron singleton para conexion unica a redis
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = redis.Redis(
                host=REDIS_HOST, 
                port=REDIS_PORT, 
                db=REDIS_DB, 
                decode_responses=True
            )
        return cls._instance

class SaleStrategy(ABC):
    # interfaz base para ventas
    @abstractmethod
    def execute(self, client_id: str, request_id: str, seat_id: str = None) -> str:
        pass

class UnnumberedStrategy(SaleStrategy):
    # estrategia para tickets no numerados
    def __init__(self):
        self.redis = RedisConnection.get_instance()
        self.max_tickets = 20000

    def execute(self, client_id: str, request_id: str, seat_id: str = None) -> str:
        current_tickets = self.redis.incr("global_tickets_sold")
        if current_tickets <= self.max_tickets:
            return "SUCCESS"
        else:
            return "REJECT"

class NumberedStrategy(SaleStrategy):
    # estrategia para tickets numerados
    def __init__(self):
        self.redis = RedisConnection.get_instance()

    def execute(self, client_id: str, request_id: str, seat_id: str = None) -> str:
        success = self.redis.setnx(f"seat:{seat_id}", client_id)
        if success:
            return "SUCCESS"
        else:
            return "REJECT"

class SaleFactory:
    # factory para decidir que estrategia instanciar
    @staticmethod
    def create_strategy(params: list) -> SaleStrategy:
        if len(params) == 3:
            return UnnumberedStrategy()
        elif len(params) == 4:
            return NumberedStrategy()
        else:
            raise ValueError("formato de benchmark desconocido")