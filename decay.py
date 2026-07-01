import math

N0 = 80.128
N = 21.447
t_half = 5730

# N = N0 * (1/2)^(t / t_half)
# N/N0 = (1/2)^(t / t_half)
# ln(N/N0) = (t / t_half) * ln(1/2)
# t = t_half * ln(N/N0) / ln(1/2)

t = t_half * math.log(N / N0) / math.log(0.5)
print(f"Time passed: {t} years")
print(f"Rounded: {round(t)} years")
