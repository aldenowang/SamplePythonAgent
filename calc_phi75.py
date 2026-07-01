import math

kappa = math.sqrt(0.05 / 0.5)
b = kappa * 25
c = kappa * 100
ratio = math.sinh(b) / math.sinh(c)
phi75 = 1e12 * ratio

print(f"kappa = {kappa}")
print(f"b = {b}")
print(f"c = {c}")
print(f"sinh(b) = {math.sinh(b)}")
print(f"sinh(c) = {math.sinh(c)}")
print(f"ratio = {ratio}")
print(f"phi75 = {phi75}")
