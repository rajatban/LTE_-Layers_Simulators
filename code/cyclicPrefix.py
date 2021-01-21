import numpy as np
from subcarrier import *

def getCP(qamNum):
    mu = Modulation[qamNum]
    K = getCarriersNum(qamNum)
    return int(K//13.33)

def addCP(OFDM_time, qamNum):
    CP = getCP(qamNum)
    cp = OFDM_time[-CP:]               # take the last CP samples ...
    return np.hstack([cp, OFDM_time])  # ... and add them to the beginning

def removeCP(signal, qamNum):
    CP = getCP(qamNum)
    K = getCarriersNum(qamNum)
    return signal[CP:(CP+K)]
