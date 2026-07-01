
t = 43.51        # days elapsed
N_t = 3.529      # grams remaining
t_half = 8.02    # half-life in days

# N(t) = N0 * (1/2)^(t / t_half)
# N0 = N(t) / (1/2)^(t / t_half)

N0 = N_t / (0.5 ** (t / t_half))
print(f"Number of half-lives: {t / t_half}")
print(f"Initial quantity: {N0} grams")
print(f"Initial quantity (rounded to 2 decimal places): {round(N0, 2)} grams")
