
# 1D steady-state heat conduction with uniform heat generation
# d²T/dx² + Q/k = 0
# General solution: T(x) = -(Q/(2k)) * x^2 + C1*x + C2

L = 4.4       # rod length (m)
T0 = 5.1      # T at x=0 (°C)
TL = 403.0    # T at x=L (°C)
Q = 6600.0    # internal heat generation (W/m³)
k = 106.0     # thermal conductivity (W/m·K)

# From BC1: T(0) = C2 = T0
C2 = T0

# From BC2: T(L) = -(Q/(2k))*L^2 + C1*L + C2 = TL
# C1 = (TL - C2 + (Q/(2k))*L^2) / L
Q_over_2k = Q / (2.0 * k)
C1 = (TL - C2 + Q_over_2k * L**2) / L

print(f"Q/(2k) = {Q_over_2k}")
print(f"C1 = {C1}")
print(f"C2 = {C2}")

# Temperature at x = 1.8 m
x = 1.8
T_x = -Q_over_2k * x**2 + C1 * x + C2
print(f"\nT(x={x}) = {T_x:.4f} °C")
print(f"T(x={x}) = {round(T_x, 2)} °C")
