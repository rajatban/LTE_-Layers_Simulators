import matplotlib.pyplot as plt

# 64QAM
bit_tuples = []
for b1 in [0, 1]:
    for b2 in [0, 1]:
        for b3 in [0, 1]:
            for b4 in [0, 1]:
                for b5 in [0, 1]:
                    for b6 in [0, 1]:
                        bit_tuples.append((b1, b2, b3, b4, b5, b6))
                        
       
    
values = [i for i in range(-7, 8, 2)]
# print(values)

constel_points = []
for real in values:
    for imag in values:
        constel_points.append(complex(real, imag))
# print(constel_points[0])
# print(bit_tuples)


mapping_table = {}
for i in range(0, len(bit_tuples)):
    mapping_table[bit_tuples[i]] = constel_points[i]

    
demapping_table = {v : k for k, v in mapping_table.items()}

# print(mapping_table)
def get_constellation_plot():
    for bit_tuple in bit_tuples:
        B = bit_tuple
        Q = mapping_table[B]
        plt.plot(Q.real, Q.imag, 'bo')
        plt.text(Q.real, Q.imag+0.2, "".join(str(x) for x in B), ha='center')

        plt.grid(True)
        plt.xlim((-8, 8)); plt.ylim((-8,8)); plt.xlabel('Real part (I)'); plt.ylabel('Imaginary part (Q)')
        plt.title('64 QAM Constellation with Gray-Mapping');
    return plt
# plt.show()