import string
import random
import struct
import pprint
import time

def udp_setup():
    print('Enter payload size:')
    pack_len = input()
    pckt_len=int(pack_len)
    print('Enter Packet(Bytes) per sec')
    pckt_rate=input()
    throughput=int(pckt_rate)

    ip_header  = "0x45000020"  # Version, IHL, Type of Service | Total Length
    ip_header += "abcd0000"  # Identification | Flags, Fragment Offset
    ip_header += "4011a6ec"  # TTL, Protocol | Header Checksum
    ip_header += "7f000001"  # Source Address
    ip_header += "7f000001"  # Destination Address

    udp_header  = "1f401f40" # Source Port | Destination Port
    udp_header += "ffff0000" # length | check_sum

    data_end="0000" #Type
    data_end+="0000"

    N=pckt_len*2
    time_exe=throughput//pckt_len
    # packet_header= ip_header+udp_header

    while 1:
        res = ''.join(random.choices( "ABCDEFGHIJKLMNOPQRSTUVWXYZ"+#string.ascii_uppercase +
                                     "0123456789"#string.digits
                                     , k = N))
        data=str(res)
        # data="Siddharth"
        print("The data sent: ",res)
        data_str=data.encode()
        data_hex=data_str.hex()
        packet=ip_header+udp_header+data_hex+data_end
        # test=packet.decode()
        print("UDP Packet sent:",packet)
        receive_PDCP_PDU(packet)
        # udp_downlink(packet)
        time.sleep(time_exe)
def udp_downlink(data_str):
        print("UDP packet received",data_str)
        payload_end=data_str[58:]
        payload=payload_end[:-8]
        print("The data received: ",''.join([chr(int(''.join(c), 16)) for c in zip(payload[0::2],payload[1::2])]))
        print()

#   ---------------UDP ENDS----------------




#   ---------------PDCP STARTS----------------

Num_SN_Bits = 0
SN_Bits = 0
Next_PDCP_TX_SN = 0
headerCompOn = 0

def PDCP_setup():
  global headerCompOn
  global SN_Bits
  global Next_PDCP_TX_SN
  global Num_SN_Bits
  Num_SN_Bits = [5, 7, 12, 15, 18]
  SN_Bits = Num_SN_Bits[2]
  Next_PDCP_TX_SN = 0
  headerCompOn = 1
  file = open("header.txt","w")
  file.write('')
  file.close()
  print('PDCP Initiated!')


def receive_PDCP_PDU(dataStream): #Receive PDCP_PDU, TO BE CALLED BY UDP ON SENDING SIDE
  global Next_PDCP_TX_SN
  global SN_Bits
  Max_PDCP_SN = 2**(SN_Bits)-1
  Next_PDCP_TX_SN += 1
  if Next_PDCP_TX_SN > Max_PDCP_SN:
    Next_PDCP_TX_SN = 1
  to_RLC = setHeader(dataStream, Next_PDCP_TX_SN, SN_Bits)
  print('PDCP SDU Sent: '+ to_RLC)
  RLC_Transmit(to_RLC)#RLC function to be called here


def headerCompression(dataStream, Next_PDCP_TX_SN):
  if Next_PDCP_TX_SN == 1:            # For first time transmission
    print('First Packet. Hence header not compressed!')
    return dataStream
  else:
    dataStream = dataStream[2:]
    out = '0xff' + dataStream[4:8] + dataStream[20:28] + dataStream[48:]
    #print('Header Compressed Data: '+ out)
    return out


def setHeader(dataStream, Next_PDCP_TX_SN, SN_Bits):
  if dataStream[:2]!='0x':
    dataStream = '0x'+ dataStream          #if '0x' not present in input

  if headerCompOn == 1:
    dataStream = headerCompression(dataStream, Next_PDCP_TX_SN)

  if SN_Bits == 5:              #FOR THE CASE OF SRB
    outputStream = hex(Next_PDCP_TX_SN)[2:].zfill(2) + str(dataStream[2:]) + '0CF36E17'
    return outputStream

  elif SN_Bits == 7:              #FOR THE CASE OF DRB-7
    outputStream = hex(0b10000000 | Next_PDCP_TX_SN) + str(dataStream[2:])
    return outputStream[2:]

  elif SN_Bits == 12:              #FOR THE CASE OF DRB-12
    outputStream = hex(0b1000000000000000 | Next_PDCP_TX_SN) + str(dataStream[2:])
    return outputStream[2:]

  elif SN_Bits == 15:              #FOR THE CASE OF DRB-15
    outputStream = hex(0b1000000000000000 | Next_PDCP_TX_SN) + str(dataStream[2:])
    return outputStream[2:]

  elif SN_Bits == 18:              #FOR THE CASE OF DRB-18
    outputStream = hex(0b100000000000000000000000 | Next_PDCP_TX_SN) + str(dataStream[2:])
    return outputStream[2:]

  if SN_Bits != 5 or SN_Bits != 7 or SN_Bits != 12 or SN_Bits != 15 or SN_Bits != 18:
    raise Exception("Supported SN Bits is limited to 5, 7, 12, 15 and 18!")


def send_PDCP_PDU(dataStream): #send PDCP_PDU, TO BE CALLED BY RLC ON RECEIVING SIDE
  print("PDCP SDU recvieved : ",dataStream)
  dataStream,SN = removeHeader(dataStream)
  #print('PDCP SDU (Receiver): ' + dataStream)
  dataStream =  '0x' + dataStream
  udp_downlink(dataStream)                            #CALL a function given by UDP team here


def removeHeader(PDCP_PDU):
  global SN_Bits
  if PDCP_PDU[:2]=='0x':
    PDCP_PDU = PDCP_PDU[2:]          #if '0x' present in input
  if SN_Bits == 5:              #FOR THE CASE OF SRB
    out1 = PDCP_PDU[2:]
    out = out1[:-8]
    hexSN = PDCP_PDU[:2]
    intSN = int(hexSN, 16)

  elif SN_Bits == 7:              #FOR THE CASE OF DRB-7
    out = PDCP_PDU[2:]
    hexSN = PDCP_PDU[:2]
    intSN = int(hexSN, 16) - 128

  elif SN_Bits == 12:              #FOR THE CASE OF DRB-12
    out = PDCP_PDU[4:]
    hexSN = PDCP_PDU[:4]
    intSN = int(hexSN, 16) - 32768

  elif SN_Bits == 15:              #FOR THE CASE OF DRB-15
    out = PDCP_PDU[4:]
    hexSN = PDCP_PDU[:4]
    intSN = int(hexSN, 16) - 32768

  elif SN_Bits == 18:              #FOR THE CASE OF DRB-18
    out = PDCP_PDU[6:]
    hexSN = PDCP_PDU[:6]
    intSN = int(hexSN, 16) - 8388608

  # elif DataChannel == 0:
  #   raise Exception("Control Channel not supported!")
  # if SN_Bits != 5 or SN_Bits != 7 or SN_Bits != 12 or SN_Bits != 15 or SN_Bits != 18:
  #   raise Exception("Supported SN Bits is limited to 5, 7, 12, 15 and 18!")

  if headerCompOn == 1:
    out = headerDecompression(out, intSN)
  return (out, intSN)

def headerDecompression(dataStream, Next_PDCP_TX_SN):
  if Next_PDCP_TX_SN == 1:            # For first time transmission
    header = dataStream[:56]
    file = open("header.txt","w")
    file.write(header)
    file.close()
    return dataStream
  elif dataStream[:2] == 'ff':
    dataStream = dataStream[2:]
    file = open("header.txt","r+")
    header = file.read()
    file.close()
    out = header[:4] + dataStream[:4] + header[8:20] + dataStream[4:12] + header[28:48] + dataStream[12:]
    return out

PDCP_setup()
#receive_PDCP_PDU('0x123456789abcdef123456789abcdef123456789abcdef123456789abcdef123456789abcdef123456789abcdef123456789abcdef')

#   ---------------PDCP ENDS----------------


#   ---------------RLC STARTS----------------
result = ''


# Field Indicator (00 = first and only packet;01= fragmented first packet;10=fragmented last packet;11= fragmented middle packet)


def checkFieldbits(Data):
    global result
    if Data[:2] == '00':
        out_string = removeHeader_RLC(Data)
        #print(out_string)
        send_PDCP_PDU(out_string)

    elif Data[:2] == '01':
        temp = removeHeader_RLC(Data)
        result += temp

    elif Data[:2] == '10':
        temp = removeHeader_RLC(Data)
        out_string = result + temp
        result = ''
        #print(out_string)
        send_PDCP_PDU(out_string)

    elif Data[:2] == '11':
        temp = removeHeader_RLC(Data)
        result += temp


def removeHeader_RLC(Data):
    temp = Data[8:]
    return temp


#input = ["01000000800", "11000001112", "11000010345", "11000011678", "110001009ab", "11000101cde","11000110f12", "11000111345", "11001000678", "110010019ab", "11001010cde", "11001011f12","11001100345", "11001101678", "110011109ab", "11001111cde", "11010000f12", "11010001345","11010010678", "10000100f","00000000ABC"]
def RLC_Receive(input_list):
        checkFieldbits(input_list)


Data = ''
RLC_SN = 0                                                                      # Sequence no.
SN_bit_length = [5, 10]                                                         # We have only used 5 bit SN
FI = ['00', '01', '10','11']                                                    # Field Indicator (00 = first and only packet;01= fragmented first packet;10=fragmented last packet;11= fragmented middle packet)
E = 0                              # E = [0,1]                                  # Extension bit
Max_RLC_SN = 2 ** (5) - 1                                                       # 5 bit header
TBS_size = 3                                                                    # size in bytes -- reference for segmentation; 1. + 8 for segmentation ;2. +8 + (N-1)*12 for concatanation, N= no. of packets joined
list1 = []
# For taking input strings

def rec_SDU(temp):
   Data = temp
   return Data


# Function for adding RLC header

def add_Header(seq_no, SN_bit, Data_in, Field):
   Ex = E                                         # Ex = E[0]                              # change when using concatanation
   global RLC_SN
   global list1
   if SN_bit == SN_bit_length[0]:                                                          # 5 bit sequence no.
       pet = RLC_SN%32                                                                     # Generating sequence no.
       temp = bin(pet).replace("0b", "")                                                   # Removing '0b' which is automatically generated after converting to binary
       while len(temp)<5:                                                                  # Keeping the sequence no. of 5 bits
           temp = '0' + temp
       outstream = Data_in
       outstream = temp + outstream
       outstream = str(Ex) + outstream
       outstream = (Field) + outstream
       list1.append(outstream)

# Function for Fragmentation of packets

def Segmentation(Data, i):
   global RLC_SN
   if len(Data) <= TBS_size:                                                    # check the size of string to see if it needs to be fragmented
       if (i == 0):
           add_Header(i, 5, Data, FI[0])                                        # No fragmentation
       else:
           add_Header(i, 5, Data, FI[2])                                        # Last fragmented packet
       i += 1
       #i = check_Sequence(i)
       RLC_SN += 1

   else:
       temp = Data[:TBS_size]                                                   # Part left after fragmenting the packet
       if (i == 0):
           add_Header(i, 5, temp, FI[1])                                        # First fragmented packet
       else:
           add_Header(i, 5, temp, FI[3])                                        # Middle fragmented packet
       RLC_SN += 1
       i += 1
       #i = check_Sequence(i)

       Segmentation(Data[TBS_size:], i)                                         # Recursively calling segmentation on the part left after fragmentation to see
                                                                                # if there are need of more fragments





def RLC_Transmit(data):
      global TBS_size
      global list1
      TBS_size = packet_size()
      list1 = []
      Segmentation(data,0)
      MAC_UL(list1)

#   ---------------RLC ENDS----------------

#---------------- MaC Layer--------------

## MAC SDU --> PDU
#import transmission
import numpy as np
#from TEMPO import * 

def packet_size():
    # This information is provided by eNode-Bglobal packet_size
    global TB_size
    TB_size=512
    SDU_size=60 #TB_size-16*3  # For sMAC subheaders
    return SDU_size

def str2bin_lis(s): 
  bin_conv = [] 
  size=0
  for val in s:
    bin_conv2 = [] 
    for c in val: 
      
      # convert each char to 
      # ASCII value 
      
      ascii_val = ord(c) 
      
      # Convert ASCII value to binary 
      binary_val = bin(ascii_val)[2:]
      binary_val= '0'*(7-len(binary_val))+ binary_val 
      bin_conv2.append(binary_val)
      
    # ''.join(bin_conv2) 
    bin_conv.append(''.join(bin_conv2)) 
    size+=len(bin_conv[-1])
  return (bin_conv),size

def convert_binary(data):
    binary= bin(data).replace("0b", "")
# ''.join(format(i, 'b') for i in str(data))
    if len(binary)<=7:
        F='0'
        binary= F +'0'*(7-len(binary))+binary
        return binary
    else:
        F='1'
        binary= F +'0'*(15-len(binary))+binary
        return binary

def join_header(_li):
    MAC_header=''
    ptr=0
    for i in _li:
        MAC_subheader=''
        data_length=len(i)
        if i!=_li[-1]:
          E='1'
        else:
          E='0'  
        LCID="11011"
        ptr=len(MAC_header)
        MAC_subheader="00"+E+LCID+ convert_binary(data_length)
        MAC_header+=MAC_subheader
    final_header=MAC_header+ ''.join(_li)
    if (len(final_header)<TB_size):
        MAC_header+='00011111'
        MAC_header=MAC_header[:ptr+2] +'1'+ MAC_header[ptr+3:]
    return MAC_header+''.join(_li)


def MAC_UL(packets):
    print(packets)
    for data in packets:
        _lis=[data]
        _lis,payload_size= str2bin_lis(_lis)
        no_pad=join_header(_lis)
        string=no_pad +'0'*(TB_size-len(no_pad))
        TB=np.array(list(map(int,string)))
        print(len(TB))
        transmission(TB[:512])
    return 1

def bin2digit_lis(_lis):
    lis=[]
    for i in _lis:
        lis.append(int(i,2))
    
    return lis

def data_unit(pdu):
    lis=[]
    for i in range(10):
        if pdu[2]=='1':
          if pdu[8]=='0':
            data_size=pdu[9:16]
            pdu=pdu[16:]
          else:
              data_size=pdu[9:24]
              pdu=pdu[24:]
          lis.append(data_size)
        else:
          
          if pdu[3:8]=="11111":
                pdu=pdu[8:]
          elif pdu[8]=='0':
                data_size=pdu[9:16]
                pduNBTY89YMDR0EA=pdu[16:]
                lis.append(data_size)
          else:
                data_size=pdu[9:24]
                pdu=pdu[24:]
                lis.append(data_size)
          break
    return  bin2digit_lis(lis), pdu



def string(_lis):
    data=[]
    for i in _lis:
        combined=[]
        while len(i)>=6:
            combined.append(i[0:7])
            i=i[7:]
        data.append("".join([chr(int(binary, 2)) for binary in combined]))
    return "".join(data)

def MAC_DL(pdu):
    pdu="".join(list(map(str,pdu)))
    size_lis,data=data_unit(pdu)
    sdu=[]
    for i in size_lis:
        sdu.append(data[:i])
        data=data[i:]
    k=string(sdu)
    print("packet sent to RLC layer : "+k)
    print("")
    #TEMPO.
    RLC_Receive( k)

#---------------- MaC Ends--------------
#---------Physical layer---------

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

def transmission(input_bits, qamNum=3):
    # qamNum = 3
    payloadBits_per_OFDM = 512
    mu = getModulation(qamNum)
    K = getCarriersNum(qamNum) # number of OFDM subcarriers
    log.info(f'K : {K}')
    CP = getCP(qamNum)  # length of the cyclic prefix: 25% of the block
    P = Pilot_Carr[mu] # number of pilot carriers per OFDM block
    pilotValue = 3+3j # The known value each pilot transmits
    allCarriers = getAllCarriers(qamNum)  # indices of all subcarriers ([0, 1, ... K-1])# Pilots is every (K/P)th carrier.
    #log.info(f'len(allCarriers) : {len(allCarriers)}')
    # For convenience of channel estimation, let's make the last carriers also be a pilot
    pilotCarriers = getPilotCarriers(qamNum)
    #log.info(f'len(pilotCarriers) : {len(pilotCarriers)}')
    # data carriers are all remaining carriers
    dataCarriers = getDataCarriers(qamNum)
    #log.info(f'len(dataCarriers) : {len(dataCarriers)}')

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

    #log.info(f'payloadBits_per_OFDM : {payloadBits_per_OFDM}')

    # bits = np.random.binomial(n=1, p=0.5, size=(payloadBits_per_OFDM, ))
    bits = input_bits
    #log.info (f"Bits count: {len(bits)}")
    old_bits = bits.copy()
    bits = padding.addPadding(bits, qamNum)
    CRC_polynomial="1001"
    #log.info(f'len(bits) :  {len(bits)}')
    #log.info(f"Before CRC length = {(len(bits))}")

    _,bits_with_crc=sender(''.join(bits.astype(str)),CRC_polynomial)
    bits_with_crc=np.array(list(bits_with_crc)).astype(np.uint8)
    #log.info(f"After CRC length = {(len(bits_with_crc))}")
    # log.info(f'Padded Bits: {padded_bits}')
    #log.info(f'bit_num : {bit_num}')

    #log.info(f'Remainder: {(len(bits)+3)%bit_num}')

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


    #log.info (f"Number of OFDM carriers in frequency domain: {len(OFDM_data)}")

    OFDM_time = np.fft.ifft(OFDM_data)
    #log.info (f"Number of OFDM samples in time-domain before CP: {len(OFDM_time)}")

    OFDM_withCP = addCP(OFDM_time, qamNum)
    #log.info (f"Number of OFDM samples in time domain with CP: {len(OFDM_withCP)}")

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
    #log.info("Bits est")
    #log.info(len(bits_est))
    #log.info(f"Miscalculated Bits: {np.sum(abs(bits_with_crc-bits_est))}/{len(bits_with_crc)}")
    #log.info(f"Obtained Bit error rate: {np.sum(abs(bits_with_crc-bits_est))/len(bits_with_crc)}")
    flag = False
    if reciever(''.join(bits_est.astype(str)),CRC_polynomial)==0:
        log.info("No error in data, CRC check passed.")
    else:
        flag = True
        log.error("Error, CRC Check Failed")

    num_CRC_bits=len(CRC_polynomial)-1
    bits_est=bits_est[::-1][num_CRC_bits:][::-1]
    bits_est_wo_padding = padding.removePadding(bits_est, len(old_bits),qamNum)
    #log.info(f"Miscalculated Bits: {np.sum(abs(old_bits-bits_est_wo_padding))}/{len(old_bits)}")
    #log.info(f"Obtained Bit error rate: {np.sum(abs(old_bits-bits_est_wo_padding))/len(old_bits)}")
    return reception(bits_est_wo_padding, flag=flag)

def reception(bits_output, flag=True):
    #print(bits_output)
    MAC_DL(bits_output)
    pass 

      
#   ---------------EXECUTION STARTS----------------
udp_setup()
