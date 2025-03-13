Let’s denote each state as a function of time:

- $U(t)$: Under Investigation
- $C(t)$: Charged
- $M_b(t)$: Magistrate Court Backlog
- $M(t)$: In Magistrate Court
- $C_b(t)$: Referred to Crown Court in Backlog
- $C(t)$: In Crown Court
- $P(t)$: In Prison
- $D(t)$: Dismissed

The flows between these compartments can be represented with differential equations. For instance:
$$\frac{dU}{dt} = -\lambda_1\, U(t)$$
$$\frac{dC}{dt} = \lambda_1\, U(t) - (\lambda_2 + \delta_C) \, C(t)$$
$$\frac{dM_b}{dt} = \lambda_2\, C(t) - (\lambda_3 + \delta_{M_b}) \, M_b(t)$$
$$\frac{dM}{dt} = \lambda_3\, M_b(t) - (\lambda_4 + \delta_M) \, M(t)$$
$$\frac{dC_b}{dt} = \lambda_4\, M(t) - (\lambda_5 + \delta_{C_b}) \, C_b(t)$$
$$\frac{dC_c}{dt} = \lambda_5\, C_b(t) - (\lambda_6 + \delta_{C_c}) \, C_c(t)$$
$$\frac{dP}{dt} = \lambda_6\, C_c(t) - \delta_P\, P(t)$$
$$\frac{dD}{dt} = \delta_C\, C(t) + \delta_{M_b}\, M_b(t) + \delta_M\, M(t) + \delta_{C_b}\, C_b(t) + \delta_{C_c}\, C_c(t) + \delta_P\, P(t)$$

Here:
- $\lambda_i$ are the flow rates between stages.
- $\delta_{*}$ are the rates at which cases are dismissed from that stage.

Critical thinking:

- The dismissal rate at each stage is crucial. In a real-world setting, these may be estimated from historical data (e.g., proportion of charged cases that end up being dismissed).
- Rates might change over time, so you might need to extend this to allow time-varying transition rates (analogous to time-varying $R_t$ in epidemiology).

