import math

shapes = {
    'square':    [1.27, 2.07, 0.18, 0.13],
    'hexagonal': [1.09, 2.23, 0.00, 0.17],
    'octagonal': [1.07, 2.29, 0.00, 0.19],
    'circular':  [1.00, 2.46, 0.00, 0.20],
    }

m = 4 * math.pi * 1e-7

def inductance(n, dO, dI, shape='circular'):
    # Mohan current-sheet approximation, diameters in m, returns H
    C1, C2, C3, C4 = shapes[shape]
    dA  = (dO + dI) / 2
    rho = (dO - dI) / (dO + dI)     # fill ratio

    return ((m * (n**2) * dA * C1) / 2) * (math.log(C2 / rho) + C3*rho + C4*rho**2)

def from_spiral(r_in, p, n, w, shape='circular'):
    # Archimedean spiral (mm) -> Mohan diameters, using angle-averaged inner/outer turn radii
    if p <= w:
        raise ValueError(f'pitch {p} mm <= trace width {w} mm, turns would short')

    dI = (2 * (r_in + p/2) - w) / 1000              # mm -> m
    dO = (2 * (r_in + p*(n - 0.5)) + w) / 1000

    return inductance(n, dO, dI, shape)

if __name__ == '__main__':
    names = list(shapes.keys())
    for i, key in enumerate(names):
        print(i + 1, " ", key)
    choice = names[int(input("Shape #: ")) - 1]

    n  = int(input("Turns: "))
    dO = float(input("Outer diameter (mm): ")) / 1000   # mm -> m
    w  = float(input("Trace width (mm): ")) / 1000
    s  = float(input("Gap (mm): ")) / 1000

    dI = dO - 2 * n * w - 2 * (n - 1) * s

    L = inductance(n, dO, dI, choice)
    print(f"L = {L*1e6:.4f} µH")