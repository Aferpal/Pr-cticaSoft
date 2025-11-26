from flask import Flask, request, jsonify
from redis import Redis, RedisError
import os
import socket
from src.dbUtilsRedis import initDb, addData, getLastMeasurements, createCol

# aqui elegimos entre importar las funciones para serving o para la copia local
from src.modelUtilsServing import loadModel, predict, Model
#from src.modelUtilsLocal import loadModel, predict, Model

from src.formatUtils import formatInputForModel, formatInputReadable, formatInputJson


# aqui elegimos de nuevo para inicializar el modelo entre el caso base o el de serving

##serving
MODEL_HOST = os.getenv('MODEL_HOST', "localhost")
MODEL_BASE = 'http://'+MODEL_HOST+':8501/v1/models/modelo'

##base
#MODEL_BASE = './data/modelo.keras'

# Nos conectamos a Redis
redis = initDb()

# Añadimos una columna 
createCol(redis, 'temperature')


# Importamos el modelo 
model: Model = loadModel(MODEL_BASE, os.getcwd()+"/data/threshold.txt")

# Inicializamos la app
app = Flask(__name__)


# Ruta base de la aplicación
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


# Ruta para añadir nuevo dato
@app.route("/nuevo")
def nuevo():

    #recuperamos el dato
    dato = request.args.get("dato", default=0, type=float)

    #lo añadimos a redis
    addData(redis, dato)

    html = "<h3>Hello {name}!</h3>" \
           "<b>Hostname:</b> {hostname}<br/>" \
           "<b>Dato: </b> {dato}"
    return html.format(name=os.getenv("NAME", "world"), hostname=socket.gethostname(), dato=dato)



# Ruta para listar las entradas
@app.route("/listar")
def data():

    #recuperamos las ultimas 10 muestras
    muestras = getLastMeasurements(redis, 10)
    
    #las formateamos a input legible (html)
    data = formatInputReadable(muestras)

    html = "<h3> Hello World!</h3>" \
            "<b>Hostname:</b> {hostname}<br/>" \
            "<h4> Printing data...</h4>" \
            "<ul>{data}\n</ul>"

    return html.format(hostname=socket.gethostname(),data=data)


# Ruta para detectar anomalias
@app.route("/detectar")
def detectar():

    #recuperamos el dato a estudiar
    dato = request.args.get("dato", default=0, type=float)

    #añadimos el dato
    addData(redis, dato)

    #recuperamos los ultimos 11 datos
    muestras = getLastMeasurements(redis, 11)

    # organizamos las muestras
    
    #muestras para devolver por json
    muestras_json = formatInputJson(muestras[1:])
    prediccion = 0.0

    #muestras para el modelo
    model_input = formatInputForModel(muestras[1:])

    #valor a predecir
    valor = float(muestras[0][1])

    # entramos a la prediccion
    if len(muestras) != 11 :

        es_anomalia = "No hay suficientes datos"

    else:

        (prediccion, es_anomalia) = predict(model, (model_input), valor)

   

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
