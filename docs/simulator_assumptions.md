# Simulator Assumptions

## Version 1 Assumptions

- Stock paths are generated using geometric Brownian motion.
- Volatility is constant within a simulation run.
- Calls are priced using Black-Scholes.
- No dividends.
- No taxes.
- No commissions.
- One covered call is sold per cycle.
- Calls are held to expiration.
- If assigned, shares are immediately repurchased at market price.
- Strategy is compared against buy-and-hold.
