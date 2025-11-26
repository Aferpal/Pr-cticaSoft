import datetime

def formatEntry(muestra):
    valor = float(muestra[1])
    timestamp= muestra[0]

    timestamp = timestamp / 1000

    return (valor, timestamp)

def formatInputReadable(muestras):
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
    return data
    
def formatInputJson(muestras):

    muestras_json = []
    
    for m in muestras:

        (valor, timestamp) = formatEntry(m)

        dt = datetime.datetime.fromtimestamp(timestamp)


        dt_str = dt.strftime('%d/%m/%Y %H:%M:%S')

        muestras_json.append({"time": dt_str, "medicion": valor})

    return muestras_json

def formatInputForModel(muestras):

    model_input = [[]]
    
    for m in muestras:

        (valor, timestamp) = formatEntry(m)

        model_input[0].append([valor])

    return [model_input[0][::-1]]