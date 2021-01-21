import subcarrier
import numpy as np
import logging

from logger import log

log.setLevel(logging.INFO)

def addPadding(data, qamNum):
    bitNum = subcarrier.getbit_num(qamNum)
    padding = bitNum-((len(data)+3)%bitNum)
    log.info(f'padding : {padding}')
    log.info(f'len(data) : {len(data)}')
    if padding != 0:
        data = np.concatenate((data , np.zeros(padding,dtype=np.int8)))
    log.info(f'len(data) : {len(data)}')
    return data

def removePadding(data, old_data_length, qamNum):
    bitNum = subcarrier.getbit_num(qamNum)
    padding = bitNum - ((old_data_length+3)%bitNum)
    return data[::-1][padding:][::-1]