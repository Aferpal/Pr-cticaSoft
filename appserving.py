from flask import Flask, request, jsonify
from redis import Redis, RedisError
import json
import os
import socket
import datetime
import numpy as np
import requests

# Connect to Redis
REDIS_HOST = os.getenv('REDIS_HOST', "localhost")
URL_SERVING = 'http://localhost:8501/v1/models/modelo'

print("REDIS_HOST: "+REDIS_HOST)
redis = Redis(host=REDIS_HOST, db=0, socket_connect_timeout=2, socket_timeout=2)
try:
    redis.execute_command('TS.CREATE', 'temperature')
except RedisError:
    print("La bbdd de redis ya existe")

thresholdfile = open(r"./data/threshold.txt", "r")

try:
    threshold = float(thresholdfile.read())
except TypeError:
    #default t
    threshold = 0

print("DEBUG: el threshold es ", threshold)


app = Flask(__name__)





def addData(redis_conn, data):
    try:
        redis_conn.execute_command('TS.ADD', 'temperature', '*', data)
    except RedisError:
        print("Error al añadir")



def getLastMeasurements(redis_conn, n_measurements):
    try:
        muestras = redis_conn.execute_command('TS.REVRANGE', 'temperature', '-', '+', 'COUNT', n_measurements)
    except RedisError:
        muestras = []
    return muestras




def getPrediction(input):
    serving_function = ':predict'

    URL = URL_SERVING + serving_function

    payload_json = {"instances": input}

    response_json = requests.post(URL, json=payload_json)

    return json.loads(response_json.text)["predictions"][0][0]




# API ENDPOINTS

@app.route("/")
def hello():
    try:
        visits = redis.incr("counter")
    except RedisError:
        visits = "<i>cannot connect to Redis, counter disabled</i>"

    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>" \
           "<b>Visits:</b> {visits}"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), visits=visits)


@app.route("/nuevo")
def nuevo():
    dato = request.args.get("dato", default=0, type=float)
    addData(redis, dato)

    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>" \
           "<b>Dato: </b> {dato}"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), dato=dato)

@app.route("/listar")
def data():
    muestras = getLastMeasurements(redis, 10)
    html = "<h3> Hello World!</h3>" \
            "<b>Hostname:</b> {hostname}<br/>" \
            "<h4> Printing data...</h4>" \
            "<ul>{data}\n</ul>"
    
    data = ""
    # Recorrer la lista de muestras
    for m in muestras:
        # Extraer el valor y el timestamp
        valor = float(m[1])
        timestamp = m[0]

        # Dividir el timestamp por 1000 para obtener los segundos
        timestamp = timestamp / 1000

        dt = datetime.datetime.fromtimestamp(timestamp)


        dt_str = dt.strftime('%d/%m/%Y %H:%M:%S')

        # Imprimir el valor y la fecha y hora
        data = data + f'\n<li>Temperatura: {valor} °C - Fecha y hora: {dt_str}</li>'

    return html.format(hostname=socket.gethostname(),data=data)

@app.route("/detectar")
def detectar():

    #recuperamos el param
    dato = request.args.get("dato", default=0, type=float)

    #añadimos el dato
    addData(redis, dato)

    #recuperamos los ultimos 11 datos
    muestras = getLastMeasurements(redis, 11)

    # vemos las muestras

    muestras_json = []
    prediccion = 0.0
    model_input = [[]]

    for m in muestras[1:]:
        valor = float(m[1])
        timestamp= m[0]

        timestamp = timestamp / 1000

        dt = datetime.datetime.fromtimestamp(timestamp)


        dt_str = dt.strftime('%d/%m/%Y %H:%M:%S')

        muestras_json.append({"time": dt_str, "medicion": valor})

        model_input[0].append([valor, dt.hour])

    # entramos a la prediccion
    if len(muestras) != 11 :
        es_anomalia = "No hay suficientes datos"
    else:

        pred = getPrediction(model_input)
        prediccion=pred
        #esto está hardcodeado por ahora, pero comprobamos si está muy lejos de la predicción
        if( abs(pred-dato) > threshold ):
            es_anomalia = "si"
        else: 
            es_anomalia = "no"

   

    json_obj = {
        "mediciones": muestras_json,
        "anomalia": es_anomalia,
        "prediccion": prediccion
    }

    return jsonify(json_obj)

if __name__ == "__main__":
    PORT = os.getenv('PORT', 80)
    print("PORT: "+str(PORT))
    app.run(host='0.0.0.0', port=PORT)
