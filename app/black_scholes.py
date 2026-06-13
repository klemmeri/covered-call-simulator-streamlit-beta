import math
from scipy.stats import norm


def call_price(stock_price, strike, time_to_expiration, risk_free_rate, volatility):
    """
    Black-Scholes European call price.
    """

    if time_to_expiration <= 0:
        return max(stock_price - strike, 0.0)

    if volatility <= 0:
        return max(stock_price - strike, 0.0)

    d1 = (
        math.log(stock_price / strike)
        + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiration
    ) / (volatility * math.sqrt(time_to_expiration))

    d2 = d1 - volatility * math.sqrt(time_to_expiration)

    price = stock_price * norm.cdf(d1) - strike * math.exp(
        -risk_free_rate * time_to_expiration
    ) * norm.cdf(d2)

    return price


def call_delta(stock_price, strike, time_to_expiration, risk_free_rate, volatility):
    """
    Black-Scholes European call delta.
    """

    if time_to_expiration <= 0:
        return 1.0 if stock_price > strike else 0.0

    if volatility <= 0:
        return 1.0 if stock_price > strike else 0.0

    d1 = (
        math.log(stock_price / strike)
        + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiration
    ) / (volatility * math.sqrt(time_to_expiration))

    return norm.cdf(d1)