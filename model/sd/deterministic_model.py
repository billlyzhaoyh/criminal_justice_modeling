import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import minimize

# Given mean and median durations (in days) for each compartment
mean_durations = {
    "U": 30,  # Under investigation
    "C": 10,  # Charged
    "Mb": 15,  # Magistrate backlog
    "M": 5,  # In magistrate court
    "Cb": 20,  # Crown court backlog
    "Cc": 10,  # In crown court
    "P": 365,  # Imprisoned (1 year)
}

# Compute transition rates: lambda = 1 / mean duration
transition_rates = {key: 1.0 / value for key, value in mean_durations.items()}

# Initial conditions (example values)
y0 = [
    5000,
    1000,
    800,
    600,
    400,
    300,
    200,
    0,
]  # Initial number of people in each compartment

# Time grid
t = np.linspace(0, 5, 6)  # Assume we have 6 time steps (e.g., months or weeks)


# Define the ODE system
def justice_system(y, t, lam):
    U, C, Mb, M, Cb, Cc, P, D = y
    lam1, lam2, lam3, lam4, lam5, lam6, lam7 = lam  # Extract transition rates

    dUdt = -lam1 * U
    dCdt = lam1 * U - lam2 * C
    dMbdt = lam2 * C - lam3 * Mb
    dMdt = lam3 * Mb - lam4 * M
    dCbdt = lam4 * M - lam5 * Cb
    dCcdt = lam5 * Cb - lam6 * Cc
    dPdt = lam6 * Cc - lam7 * P
    dDdt = (
        lam2 * C + lam3 * Mb + lam4 * M + lam5 * Cb + lam6 * Cc + lam7 * P
    )  # Dismissals

    return [dUdt, dCdt, dMbdt, dMdt, dCbdt, dCcdt, dPdt, dDdt]


# Solve ODE with initial estimates
lam_init = list(transition_rates.values())
solution = odeint(justice_system, y0, t, args=(lam_init,))

# Example observed data (replace with actual data)
observed_data = np.array(
    [
        [5000, 1000, 800, 600, 400, 300, 200, 0],
        [4900, 1100, 750, 580, 420, 320, 210, 10],
        [4800, 1150, 700, 550, 440, 340, 220, 30],
        [4700, 1200, 650, 530, 460, 360, 230, 50],
        [4600, 1250, 600, 500, 480, 380, 240, 80],
        [4500, 1300, 550, 480, 500, 400, 250, 110],
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
    "Under Investigation",
    "Charged",
    "Mag. Backlog",
    "In Mag.",
    "Crown Backlog",
    "In Crown",
    "Imprisoned",
    "Dismissed",
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
