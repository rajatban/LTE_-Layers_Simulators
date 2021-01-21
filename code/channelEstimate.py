import subcarrier
import scipy.interpolate
import numpy as np
import matplotlib.pyplot as plt

def channelEstimate(OFDM_demod, qamNum, pilotValue, show_plot=False):
    pilotCarriers = subcarrier.getPilotCarriers(qamNum)
    allCarriers = subcarrier.getAllCarriers(qamNum)
    pilots = OFDM_demod[pilotCarriers]  # extract the pilot values from the RX signal
    Hest_at_pilots = pilots / pilotValue # divide by the transmitted pilot values
    
    # Perform interpolation between the pilot carriers to get an estimate
    # of the channel in the data carriers. Here, we interpolate absolute value and phase 
    # separately
    Hest_abs = scipy.interpolate.interp1d(pilotCarriers, abs(Hest_at_pilots), kind='linear')(allCarriers)
    Hest_phase = scipy.interpolate.interp1d(pilotCarriers, np.angle(Hest_at_pilots), kind='linear')(allCarriers)
    Hest = Hest_abs * np.exp(1j*Hest_phase)
    
    if show_plot:
        plt.plot(allCarriers, abs(H_exact), label='Correct Channel')
        plt.stem(pilotCarriers, abs(Hest_at_pilots), label='Pilot estimates')
        plt.plot(allCarriers, abs(Hest), label='Estimated channel via interpolation')
        plt.grid(True); plt.xlabel('Carrier index'); plt.ylabel('$|H(f)|$'); plt.legend(fontsize=10)
        plt.ylim(0,2)
        plt.show()
    
    return Hest