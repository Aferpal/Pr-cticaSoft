import requests
import json

class Model:
    def __init__(self, url, threshold):
        self.url = url
        self.threshold: float = threshold

def loadModel(url, thresholdDir):

    thresholdfile = open(rf"{thresholdDir}", "r")
    try:
        threshold = float(thresholdfile.read())
    except TypeError:
        threshold = 0.0


    return Model(url, threshold)

def predict(model: Model, input_data, expected_output):
    serving_function = ':predict'

    URL = model.url + serving_function

    payload_json = {"instances": input_data}

    response_json = requests.post(URL, json=payload_json)

    pred = json.loads(response_json.text)["predictions"][0][0]

    es_anom = "no"

    if( abs(pred-expected_output) > model.threshold ):
        es_anom = "si"
    
    return (float(pred), es_anom)