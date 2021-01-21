K = 64 # number of OFDM subcarriers

CP = K//4  # length of the cyclic prefix: 25% of the block

P = 8 # number of pilot carriers per OFDM block

pilotValue = 3+3j # The known value each pilot transmits

allCarriers = np.arange(K)  # indices of all subcarriers ([0, 1, ... K-1])

pilotCarriers = allCarriers[::K//P] # Pilots is every (K/P)th carrier.

# For convenience of channel estimation, let's make the last carriers also be a pilot
if pilotCarriers[-1] != (K-1):
    pilotCarriers = np.hstack([pilotCarriers, np.array([allCarriers[-1]])])
    P = P+1

# data carriers are all remaining carriers
dataCarriers = np.delete(allCarriers, pilotCarriers)


