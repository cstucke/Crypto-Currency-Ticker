import numpy as np


def compute_returns(prices):
    """
    Compute simple returns from a sequence of prices.

    Parameter---------------
    prices: list or numpy.ndarray
                A sequence of prices from oldest to newest.

    Return------------------
        numpy.ndarray with length len(prices) - 1.

    This function assumes that all prices are positive and non-zero.
    """
    prices = np.array(prices)
    return (prices[1:] - prices[:-1]) / prices[:-1]


def vats_decision(prices, threshold=0.5, max_volatility=None, min_points=10):
    """
    Generate a BUY, SELL, or HOLD signal based on a volatility-adjusted trend score.

    The strategy computes the mean (mu) and standard deviation (sigma) of price
    returns and defines a trend score as mu / sigma. This score represents the
    strength of the trend relative to market volatility.

    A volatility filter is applied to avoid trading during highly
    chaotic market conditions.

    Parameters-------

    :param prices: list or numpy.ndarray
    :param threshold: minimum absolute trend score required to trigger a signal.
    :param max_volatility: maximum allowed standard deviation of returns.
    :param min_points: minimum number of price points required to compute a valid decision.

    Returns-------
    str
        One of the following trading signals:
        - "BUY"
        - "SELL"
        - "HOLD"
    """

    if len(prices) < min_points:
        return "HOLD"

    returns = compute_returns(prices)
    sigma = np.std(returns)

    if sigma == 0:
        return "HOLD"

    if max_volatility is not None and sigma > max_volatility:
        return "HOLD"

    mu = np.mean(returns)
    score = mu / sigma

    if score > threshold:
        return "BUY"
    elif score < -threshold:
        return "SELL"
    else:
        return "HOLD"
