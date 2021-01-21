# 32QAM
import matplotlib.pyplot as plt


bit_tuples = []
for b1 in [0, 1]:
    for b2 in [0, 1]:
        for b3 in [0, 1]:
            for b4 in [0, 1]:
                for b5 in [0, 1]:
                    bit_tuples.append((b1, b2, b3, b4, b5))
                        

                        
values = [i for i in range(-5, 6, 2)]
# print(values)

points = []
for real in values:
    for imag in values:
        points.append(complex(real, imag))

remPoints = [points[0], points[5], points[30], points[35]]
constel_points = [point for point in points if point not in remPoints]

print('len(constel_points) : ', len(constel_points))
print('len(bit_tuples) : ', len(bit_tuples))

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
    plt.xlim((-6, 6)); plt.ylim((-6,6)); plt.xlabel('Real part (I)'); plt.ylabel('Imaginary part (Q)')
    plt.title('32 QAM Constellation with Gray-Mapping');
    return plt

if __name__ == '__main__':
    plt = get_constellation_plot()
    plt.show()
    