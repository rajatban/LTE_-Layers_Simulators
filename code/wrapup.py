import subcarrier
import numpy as np
def equalize(OFDM_demod, Hest):
    return OFDM_demod / Hest

def get_payload(equalized, qamNum):
    dataCarriers = subcarrier.getDataCarriers(qamNum)
    return equalized[dataCarriers]

def Demapping(QAM, qamNum):
    modulationQAM = subcarrier.getQAM(qamNum)
    demapping_table = modulationQAM.demapping_table
    constellation = np.array([x for x in demapping_table.keys()])
    dists = abs(QAM.reshape((-1,1)) - constellation.reshape((1,-1)))
    
    const_index = dists.argmin(axis=1)
    
    hardDecision = constellation[const_index]
    
    return np.vstack([demapping_table[C] for C in hardDecision]), hardDecision

def PS(bits):
    return bits.reshape((-1,))