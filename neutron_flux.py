import math

# Given parameters
a = 80.0       # cm, slab length
phi0 = 1e13    # neutrons/cm^2/s at x=0
D = 0.8        # cm, diffusion coefficient
sigma_a = 0.008  # cm^-1, macroscopic absorption cross section
x = 20.0       # cm, position of interest

# Compute kappa
kappa_sq = sigma_a / D
kappa = math.sqrt(kappa_sq)
print(f"kappa^2 = {kappa_sq} cm^-2")
print(f"kappa   = {kappa} cm^-1")

# Solution: phi(x) = phi0 * sinh(kappa*(a-x)) / sinh(kappa*a)
numerator = math.sinh(kappa * (a - x))
denominator = math.sinh(kappa * a)

print(f"\nsinh(kappa*(a-x)) = sinh({kappa*(a-x)}) = {numerator}")
print(f"sinh(kappa*a)     = sinh({kappa*a})  = {denominator}")

phi_20 = phi0 * numerator / denominator
ratio = numerator / denominator

print(f"\nRatio sinh(6)/sinh(8) = {ratio}")
print(f"\nphi(20) = {phi0} * {ratio}")
print(f"phi(20) = {phi_20:.6e} neutrons/cm^2/s")
