from collections import Counter

import numpy as np
import QAM16, QAM64, QAM32
import matplotlib.pyplot as plt
import logging
from logger import log

log.setLevel(logging.INFO)

Modulation={
    1: "64QAM",
    2: "32QAM",
    3: "16QAM",
}

Pilot_Gap = 8

Data_Carr={
    "64QAM": 86,
    "32QAM": 103,
    "16QAM": 129,
}

Pilot_Carr={
    "64QAM": 86//Pilot_Gap,
    "32QAM": 103//Pilot_Gap,
    "16QAM": 129//Pilot_Gap,
} 

Bits={
    "64QAM": 6,
    "32QAM": 5,
    "16QAM": 4,
}

# All_Carr = Counter(Data_Carr) + Counter(Pilot_Carr)

def getModulation(qamNum):
    mu = Modulation[qamNum]
    return mu

    
def getCarriersNum(qamNum):
    mu = Modulation[qamNum]
    carriersCount = Data_Carr[mu] + Pilot_Carr[mu] + 2
    return carriersCount

def getAllCarriers(qamNum): 
    allCarriers = np.arange(getCarriersNum(qamNum))
    return allCarriers


def getPilotCarriers(qamNum):
    mu = Modulation[qamNum]
    P = Pilot_Carr[mu]
    allCarriers = getAllCarriers(qamNum)
    K = getCarriersNum(qamNum)
    pilotCarriers = allCarriers[::K//P]
    # making the last carriers also a pilot
    pilotCarriers = np.hstack([pilotCarriers, np.array([allCarriers[-1]])])
    return pilotCarriers

def getDataCarriers(qamNum):
    allCarriers = getAllCarriers(qamNum)
    pilotCarriers = getPilotCarriers(qamNum)
    # log.warning(f'pilotCount : {len(pilotCarriers)}')
    # log.warning(f'allCarriers : {len(allCarriers)}')
    dataCarriers = np.delete(allCarriers, pilotCarriers)
    return dataCarriers

def getbit_num(qamNum):
    mu = Modulation[qamNum]
    return Bits[mu]

# def dataBits_per_OFDM(qamNum):
#     x = getDataCarriers(qamNum)
#     y = getbit_num(qamNum)
#     return len(x)*y 


def getQAM(qamNum):
    if qamNum==1:
        QAM = QAM64
    elif qamNum==2:
        QAM = QAM32
    elif qamNum==3:
        QAM = QAM16
    return QAM

def getCarrierPlot(qamNum):
    # print ("allCarriers:   %s" % allCarriers)
    # print ("pilotCarriers: %s" % pilotCarriers)
    # print ("dataCarriers:  %s" % dataCarriers)
    K = getCarriersNum(qamNum)
    allCarriers = getAllCarriers(qamNum)
    pilotCarriers = getPilotCarriers(qamNum)
    dataCarriers = getDataCarriers(qamNum)
    plt.figure(figsize=(8,0.8))
    plt.plot(pilotCarriers, np.zeros_like(pilotCarriers), 'bo', label='pilot')
    plt.plot(dataCarriers, np.zeros_like(dataCarriers), 'ro', label='data')
    plt.legend(fontsize=10, ncol=2)
    plt.xlim((-1,K)); plt.ylim((-0.1, 0.3))
    plt.xlabel('Carrier index')
    plt.yticks([])
    plt.grid(True);
    return plt
    # plt.show()

def getData(qamNum):
    mu = getModulation(qamNum)
    K = getCarriersNum(qamNum) # number of OFDM subcarriers
    CP = getCP(qamNum)  # length of the cyclic prefix: 25% of the block
    P = Pilot_Carr[mu] # number of pilot carriers per OFDM block
    pilotValue = 3+3j # The known value each pilot transmits

    allCarriers = getAllCarriers(qamNum)   # indices of all subcarriers ([0, 1, ... K-1])
    pilotCarriers = allCarriers[::K//P] # Pilots is every (K/P)th carrier.

    # For convenience of channel estimation, let's make the last carriers also be a pilot
    pilotCarriers = getPilotCarriers(qamNum)
    P = P+1

    # data carriers are all remaining carriers
    dataCarriers = getDataCarriers(qamNum)
    plt = getCarrierPlot(qamNum)
    bit_num = getbit_num(qamNum) # mu = 4 # bits per symbol (i.e. 16QAM)
    payloadBits_per_OFDM = dataBits_per_OFDM(qamNum)  # number of payload bits per OFDM symbol
