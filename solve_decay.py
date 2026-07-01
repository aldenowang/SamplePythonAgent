import math

# Given parameters
y0 = 200       # initial amount (grams)
k = -0.1       # decay constant
x = 10         # time

# Analytical solution: y(x) = y0 * e^(k * x)
y = y0 * math.exp(k * x)

print("=== Radioactive Decay Problem ===")
print(f"  ODE: dy/dx = {k} * y")
print(f"  Initial condition: y(0) = {y0} grams")
print(f"  Solution: y(x) = {y0} * e^({k} * x)")
print(f"  At x = {x}:")
print(f"    y({x}) = {y0} * e^({k * x})")
print(f"    y({x}) = {y0} * {math.exp(k * x):.10f}")
print(f"    y({x}) = {y:.6f} grams")
