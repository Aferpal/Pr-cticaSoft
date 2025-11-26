from keras import models
from keras import Sequential
import numpy as np

class Model:
    def __init__(self, model, threshold):
        self.model: Sequential = model
        self.threshold: float = threshold

def loadModel(modelDir, thresholdDir):

    model : Sequential = models.load_model(modelDir)

    thresholdfile = open(rf"{thresholdDir}", "r")
    try:
        threshold = float(thresholdfile.read())
    except TypeError:
        threshold = 0.0


    return Model(model, threshold)

def predict(model: Model, input_data, expected_output):
    pred = model.model.predict(np.array(input_data))[0][0]

    es_anom = "no"
    if ( abs(pred - expected_output ) > model.threshold ):
        es_anom = "si"
    
    return (float(pred), es_anom)