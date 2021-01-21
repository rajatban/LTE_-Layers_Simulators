import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate


def recieved_transmitted_signal_plot(OFDM_TX, OFDM_RX, show=False):
    if not show:
        return
    plt.figure(figsize=(8,2))
    plt.plot(abs(OFDM_TX), label='TX signal')
    plt.plot(abs(OFDM_RX), label='RX signal')
    plt.legend(fontsize=10)
    plt.xlabel('Time'); plt.ylabel('$|x(t)|$')
    plt.grid(True)
    plt.show()

def decision_mapping_plot(QAM_est, hardDecision, show=False):
    if not show:
        return
    for qam, hard in zip(QAM_est, hardDecision):
        plt.plot([qam.real, hard.real], [qam.imag, hard.imag], 'b-o');
        plt.plot(hardDecision.real, hardDecision.imag, 'ro')
    plt.grid(True)
    plt.xlabel('Real part')
    plt.ylabel('Imaginary part')
    plt.title('Hard Decision demapping')
    plt.show()
