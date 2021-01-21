import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate
import logging
np.random.seed(420)
from channelEstimate import channelEstimate
from Channel import *
from cyclicPrefix import *
import QAM16, QAM64, QAM32
from subcarrier import *
from wrapup import *
import plots
import padding
from CRC_checker import *
from logger import log

log.setLevel(logging.INFO)

# qamNum = int(input("Enter the modulation for transmission: ")) #1-64QAM, 2-32QAM, 3-16QAM, 4-8QAM
qamNum = 3
payloadBits_per_OFDM = 512

mu = getModulation(qamNum)
K = getCarriersNum(qamNum) # number of OFDM subcarriers
log.info(f'K : {K}')
CP = getCP(qamNum)  # length of the cyclic prefix: 25% of the block
P = Pilot_Carr[mu] # number of pilot carriers per OFDM block
pilotValue = 3+3j # The known value each pilot transmits
allCarriers = getAllCarriers(qamNum)  # indices of all subcarriers ([0, 1, ... K-1])# Pilots is every (K/P)th carrier.
log.info(f'len(allCarriers) : {len(allCarriers)}')
# For convenience of channel estimation, let's make the last carriers also be a pilot
pilotCarriers = getPilotCarriers(qamNum)
log.info(f'len(pilotCarriers) : {len(pilotCarriers)}')
# data carriers are all remaining carriers
dataCarriers = getDataCarriers(qamNum)
log.info(f'len(dataCarriers) : {len(dataCarriers)}')

carrier_plt = getCarrierPlot(qamNum)
# carrier_plt.show()
bit_num = getbit_num(qamNum) # mu = 4 # bits per symbol (i.e. 16QAM)
# payloadBits_per_OFDM = dataBits_per_OFDM(qamNum)  # number of payload bits per OFDM symbol

if qamNum==1:
    QAM = QAM64
elif qamNum==2:
    QAM = QAM32
elif qamNum==3:
    QAM = QAM16

mapping_table =  QAM.mapping_table  
demapping_table = {v : k for k, v in mapping_table.items()}

H_exact = np.fft.fft(channelResponse, K)
plt.plot(allCarriers, abs(H_exact))
plt.xlabel('Subcarrier index'); plt.ylabel('$|H(f)|$'); plt.grid(True); plt.xlim(0, K-1)

log.info(f'payloadBits_per_OFDM : {payloadBits_per_OFDM}')


bits = np.random.binomial(n=1, p=0.5, size=(payloadBits_per_OFDM, ))
log.info (f"Bits count: {len(bits)}")
old_bits = bits.copy()
bits = padding.addPadding(bits, qamNum)
CRC_polynomial="1001"
log.info(f'len(bits) :  {len(bits)}')
log.info(f"Before CRC length = {(len(bits))}")

_,bits_with_crc=sender(''.join(bits.astype(str)),CRC_polynomial)
bits_with_crc=np.array(list(bits_with_crc)).astype(np.uint8)
log.info(f"After CRC length = {(len(bits_with_crc))}")
# log.info(f'Padded Bits: {padded_bits}')
log.info(f'bit_num : {bit_num}')

log.info(f'Remainder: {(len(bits)+3)%bit_num}')

def SP(bits):
    return bits.reshape((len(dataCarriers), bit_num))
bits_SP = SP(bits_with_crc)
# log.info ("First 5 bit groups")
# log.info (bits_SP[:5,:])

def Mapping(bits):
    return np.array([mapping_table[tuple(b)] for b in bits])
QAM = Mapping(bits_SP)

def OFDM_symbol(QAM_payload):
    symbol = np.zeros(K, dtype=complex) # the overall K subcarriers
    symbol[pilotCarriers] = pilotValue  # allocate the pilot subcarriers 
    symbol[dataCarriers] = QAM_payload  # allocate the pilot subcarriers
    return symbol
OFDM_data = OFDM_symbol(QAM)


log.info (f"Number of OFDM carriers in frequency domain: {len(OFDM_data)}")

OFDM_time = np.fft.ifft(OFDM_data)
log.info (f"Number of OFDM samples in time-domain before CP: {len(OFDM_time)}")

OFDM_withCP = addCP(OFDM_time, qamNum)
log.info (f"Number of OFDM samples in time domain with CP: {len(OFDM_withCP)}")

OFDM_TX = OFDM_withCP
OFDM_RX = channel(OFDM_TX) #######

rx_tx_plot = plots.recieved_transmitted_signal_plot(OFDM_TX, OFDM_RX)
# rx_tx_plot.show()

OFDM_RX_noCP = removeCP(OFDM_RX, qamNum)

OFDM_demod = np.fft.fft(OFDM_RX_noCP)
Hest = channelEstimate(OFDM_demod, qamNum, pilotValue)

equalized_Hest = equalize(OFDM_demod, Hest)

QAM_est = get_payload(equalized_Hest, qamNum)
plt.plot(QAM_est.real, QAM_est.imag, 'bo');
plt.grid(True); plt.xlabel('Real part'); plt.ylabel('Imaginary Part'); plt.title("Received constellation");

PS_est, hardDecision = Demapping(QAM_est, qamNum)

decision_mapping_plot = plots.decision_mapping_plot(QAM_est, hardDecision, show=False)


bits_est = PS(PS_est)
log.info("Bits est")
log.info(len(bits_est))
log.info(f"Miscalculated Bits: {np.sum(abs(bits_with_crc-bits_est))}/{len(bits_with_crc)}")
log.info(f"Obtained Bit error rate: {np.sum(abs(bits_with_crc-bits_est))/len(bits_with_crc)}")

flag = False
if reciever(''.join(bits_est.astype(str)),CRC_polynomial)==0:
    log.info("No error in data, CRC check passed.")
else:
    flag = True
    log.error("Error, CRC Check Failed")

num_CRC_bits=len(CRC_polynomial)-1
bits_est=bits_est[::-1][num_CRC_bits:][::-1]
bits_est_wo_padding = padding.removePadding(bits_est, len(old_bits), qamNum)
log.info(f"Miscalculated Bits: {np.sum(abs(old_bits-bits_est_wo_padding))}/{len(old_bits)}")
log.info(f"Obtained Bit error rate: {np.sum(abs(old_bits-bits_est_wo_padding))/len(old_bits)}")


