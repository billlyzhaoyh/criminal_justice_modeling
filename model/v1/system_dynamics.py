import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import minimize

# Given mean and median durations (in days) for each compartment
mean_durations = {
    "I": -1,  # Innocent where people will stay here after being transitioned here
    "U": 40,  # Under investigation ref data/ccjs/processed/ccjs_annual_May-2025.csv Average (median) days taken for police to record a successful outcome in victim-based cases
    "C": 46,  # Charged Average (mean) days from police referring a case to the CPS and the CPS authorising a charge
    "Mb": 15,  # Magistrate backlog
    "M": 5,  # In magistrate court
    "Cb": 20,  # Crown court backlog
    "Cc": 10,  # In crown court
    "P": 365,  # Imprisoned (1 year)
}

# Compute transition rates: lambda = 1 / mean duration
transition_rates = {key: 1.0 / value for key, value in mean_durations.items()}
# Overwrite the transition rate from I to U since that is determined by crime rate
transition_rates["I"] = 0.01

# Initial conditions using the latest court data
y0 = [
    56489800,  # 2021 census
    5000,
    1000,
    800,
    600,
    400,
    300,
    200,
]  # Initial number of people in each compartment

# Time grid
t = np.linspace(0, 5, 6)  # Assume we have 6 time steps (e.g. weeks or months)


# Define the ODE system
def justice_system(y, t, lam):
    I, U, C, Mb, M, Cb, Cc, P = y
    lam0, lam1, lam2, lam3, lam4, lam5, lam6, lam7 = lam  # Extract transition rates

    dUdt = -lam1 * U + lam0 * I
    dCdt = lam1 * U - lam2 * C
    dMbdt = lam2 * C - lam3 * Mb
    dMdt = lam3 * Mb - lam4 * M
    dCbdt = lam4 * M - lam5 * Cb
    dCcdt = lam5 * Cb - lam6 * Cc
    dPdt = lam6 * Cc - lam7 * P
    dIdt = (
        -lam0 * I + lam2 * C + lam3 * Mb + lam4 * M + lam5 * Cb + lam6 * Cc + lam7 * P
    )  # return to innocent

    return [dIdt, dUdt, dCdt, dMbdt, dMdt, dCbdt, dCcdt, dPdt]


# Solve ODE with initial estimates
lam_init = list(transition_rates.values())
solution = odeint(justice_system, y0, t, args=(lam_init,))

# Example observed data (replace with actual data)
observed_data = np.array(
    [
        [10000, 5000, 1000, 800, 600, 400, 300, 200],  # Week 0
        [9850, 4800, 1100, 820, 620, 410, 320, 220],  # Week 1
        [9700, 4600, 1150, 850, 630, 420, 340, 240],  # Week 2
        [9550, 4400, 1180, 870, 640, 430, 360, 260],  # Week 3
        [9400, 4200, 1200, 880, 650, 440, 380, 280],  # Week 4
        [9250, 4000, 1220, 890, 660, 450, 400, 300],  # Week 5
    ]
)


# Define the objective function for optimization (least squares fit)
def objective(lam):
    sol = odeint(justice_system, y0, t, args=(lam,))
    error = np.sum((sol - observed_data) ** 2)  # Sum of squared errors
    return error


# Optimize the transition rates to best fit the observed data
result = minimize(objective, lam_init, method="Nelder-Mead")

# Best-fit transition rates
best_fit_lam = result.x
print("Optimized transition rates:", best_fit_lam)

# Solve ODE with optimized rates
solution_best_fit = odeint(justice_system, y0, t, args=(best_fit_lam,))

# Plot results
compartments = [
    "Innocent" "Under Investigation",
    "Charged",
    "Mag. Backlog",
    "In Mag.",
    "Crown Backlog",
    "In Crown",
    "Imprisoned",
]
fig, ax = plt.subplots(4, 2, figsize=(12, 10))
ax = ax.flatten()

for i in range(len(compartments)):
    ax[i].plot(t, solution_best_fit[:, i], label="Model Fit", linestyle="dashed")
    ax[i].scatter(t, observed_data[:, i], color="red", label="Observed", marker="o")
    ax[i].set_title(compartments[i])
    ax[i].legend()

plt.tight_layout()
plt.show()
