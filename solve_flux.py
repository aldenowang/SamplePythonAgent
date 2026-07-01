import math

# Given parameters
a = 100.0       # cm, slab length
phi0 = 1e12     # neutrons/cm^2/s at x=0
D = 0.9         # cm, diffusion coefficient
sigma_a = 0.01  # cm^-1, macroscopic absorption cross section
x = 50.0        # cm, point of interest

# Compute inverse diffusion length
kappa = math.sqrt(sigma_a / D)
print(f"kappa = sqrt(Sigma_a / D) = sqrt({sigma_a}/{D}) = {kappa:.6f} cm^-1")

# Compute flux using analytical solution
# phi(x) = phi0 * sinh(kappa*(a-x)) / sinh(kappa*a)
kappa_a_minus_x = kappa * (a - x)
kappa_a = kappa * a

print(f"kappa*(a-x) = {kappa_a_minus_x:.6f}")
print(f"kappa*a     = {kappa_a:.6f}")

numerator = math.sinh(kappa_a_minus_x)
denominator = math.sinh(kappa_a)

print(f"sinh(kappa*(a-x)) = {numerator:.6e}")
print(f"sinh(kappa*a)     = {denominator:.6e}")

phi_50 = phi0 * numerator / denominator
print(f"\nphi(50) = {phi0:.2e} * {numerator:.6e} / {denominator:.6e}")
print(f"phi(50) = {phi_50:.6e} neutrons/cm^2/s")
