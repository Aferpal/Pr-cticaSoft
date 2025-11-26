from redis import Redis, RedisError
import os

def initDb():
    REDIS_HOST = os.getenv('REDIS_HOST', "localhost")
    redis = Redis(host=REDIS_HOST, db=0, socket_connect_timeout=2, socket_timeout=2)
    return redis

def addData(redis_conn : Redis, data):
    try:
        redis_conn.execute_command('TS.ADD', 'temperature', '*', data)
    except RedisError:
        print("Error al añadir")

def getLastMeasurements(redis_conn: Redis, n_measurements):
    try:
        muestras = redis_conn.execute_command('TS.REVRANGE', 'temperature', '-', '+', 'COUNT', n_measurements)
    except RedisError:
        muestras = []
    return muestras

def createCol(redis_conn: Redis, col_name):
    try:
        redis_conn.execute_command('TS.CREATE', col_name)
    except RedisError:
        print("La bbdd de redis ya existe")