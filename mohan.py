import math

shapes = {
    'square':    [1.27, 2.07, 0.18, 0.13],
    'hexagonal': [1.09, 2.23, 0.00, 0.17],
    'octagonal': [1.07, 2.29, 0.00, 0.19],
    'circular':  [1.00, 2.46, 0.00, 0.20],
    }


names = list(shapes.keys())
for i, key in enumerate(names):
    print(i + 1, " ", key)
choice = names[int(input("Shape #: ")) - 1]
C1, C2, C3, C4 = shapes[choice]

m  = 4 * math.pi * 1e-7

n  = int(input("Turns: "))
dO = float(input("Outer diameter (mm): ")) / 1000   # mm -> m
w  = float(input("Trace width (mm): ")) / 1000
s  = float(input("Gap (mm): ")) / 1000

dI = dO - 2 * n * w - 2 * (n - 1) * s
dA = (dO + dI) / 2
p  = (dO - dI) / (dO + dI)

L = ((m * (n**2) * dA * C1) / 2) * (math.log(C2 / p) + C3*p + C4*p**2)


print(f"L = {L*1e6:.4f} µH")