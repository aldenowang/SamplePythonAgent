import math
from decimal import Decimal, getcontext

# Set high precision
getcontext().prec = 50

kappa = math.sqrt(0.05 / 0.5)
a = 100.0
x = 75.0
b = kappa * (a - x)  # kappa * 25
c = kappa * a          # kappa * 100

# Stable approach: sinh(b)/sinh(c) = (e^b - e^-b)/(e^c - e^-c)
# For large c, denominator ~ e^c/2, so ratio ~ 2*(e^b - e^-b)*e^-c
# More precisely: ratio = (e^b - e^-b)/(e^c - e^-c) = (e^(b-c) - e^(-b-c))/(1 - e^(-2c))
ratio_stable = math.exp(b - c) - math.exp(-b - c)
denom_correction = 1.0 - math.exp(-2*c)
ratio_exact = ratio_stable / denom_correction

phi75_approx = 1e12 * ratio_stable
phi75_exact = 1e12 * ratio_exact

print("=== Float precision ===")
print(f"kappa = {kappa:.20f}")
print(f"b = kappa*25 = {b:.20f}")
print(f"c = kappa*100 = {c:.20f}")
print(f"b - c = {b-c:.20f}")
print(f"-b - c = {-b-c:.20f}")
print(f"e^(b-c) = {math.exp(b-c):.20e}")
print(f"e^(-b-c) = {math.exp(-b-c):.20e}")
print(f"ratio_stable (no denom correction) = {ratio_stable:.20e}")
print(f"denom_correction = 1 - e^(-2c) = {denom_correction:.20e}")
print(f"ratio_exact = {ratio_exact:.20e}")
print(f"phi75_approx = {phi75_approx:.15e}")
print(f"phi75_exact  = {phi75_exact:.15e}")

# Direct sinh approach
print("\n=== Direct sinh approach ===")
sinh_b = math.sinh(b)
sinh_c = math.sinh(c)
print(f"sinh(b) = {sinh_b:.20e}")
print(f"sinh(c) = {sinh_c:.20e}")
try:
    ratio_direct = sinh_b / sinh_c
    phi75_direct = 1e12 * ratio_direct
    print(f"ratio_direct = {ratio_direct:.20e}")
    print(f"phi75_direct = {phi75_direct:.15e}")
except Exception as e:
    print(f"Direct sinh ratio failed: {e}")

# High precision with Decimal
print("\n=== Decimal high precision ===")
getcontext().prec = 80
D = Decimal
kappa_d = (D('0.05') / D('0.5')).sqrt()
a_d = D('100')
x_d = D('75')
b_d = kappa_d * (a_d - x_d)
c_d = kappa_d * a_d

print(f"kappa = {kappa_d}")
print(f"b = {b_d}")
print(f"c = {c_d}")
print(f"b - c = {b_d - c_d}")

# Decimal exp via Taylor series
def decimal_exp(x, prec_terms=200):
    getcontext().prec = 80
    result = D(1)
    term = D(1)
    for i in range(1, prec_terms):
        term *= x / D(i)
        result += term
        if abs(term) < D(10) ** (-75):
            break
    return result

eb_mc = decimal_exp(b_d - c_d)
emb_mc = decimal_exp(-b_d - c_d)
e_m2c = decimal_exp(D(-2) * c_d)

ratio_num = eb_mc - emb_mc
ratio_den = D(1) - e_m2c
ratio_d = ratio_num / ratio_den

phi75_d = D('1e12') * ratio_d

print(f"e^(b-c) = {eb_mc}")
print(f"e^(-b-c) = {emb_mc}")
print(f"e^(-2c) = {e_m2c}")
print(f"ratio numerator = {ratio_num}")
print(f"ratio denominator = {ratio_den}")
print(f"ratio = {ratio_d}")
print(f"phi75 = {phi75_d}")

# Also compute sinh(b)/sinh(c) via exponentials in Decimal
print("\n=== Decimal sinh(b)/sinh(c) via full exponentials ===")
eb = decimal_exp(b_d)
emb = decimal_exp(-b_d)
ec = decimal_exp(c_d)
emc = decimal_exp(-c_d)
sinh_b_d = (eb - emb) / D(2)
sinh_c_d = (ec - emc) / D(2)
ratio_sinh_d = sinh_b_d / sinh_c_d
phi75_sinh_d = D('1e12') * ratio_sinh_d
print(f"e^b = {eb}")
print(f"e^(-b) = {emb}")
print(f"e^c = {ec}")
print(f"e^(-c) = {emc}")
print(f"sinh(b) = {sinh_b_d}")
print(f"sinh(c) = {sinh_c_d}")
print(f"sinh(b)/sinh(c) = {ratio_sinh_d}")
print(f"phi75 = {phi75_sinh_d}")

print("\n=== Summary ===")
print(f"phi(75) [float approx]   = {phi75_approx:.15e}")
print(f"phi(75) [float exact]    = {phi75_exact:.15e}")
print(f"phi(75) [Decimal stable] = {phi75_d}")
print(f"phi(75) [Decimal sinh]   = {phi75_sinh_d}")
