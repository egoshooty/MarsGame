from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal

Signal = Literal["buy", "sell", "hold"]


@dataclass
class StrategyState:
    prices: List[float]
    fast_ema: float | None = None
    slow_ema: float | None = None
    last_rsi: float | None = None


class EmaRsiMomentumStrategy:
    """
    Approximation of a common video strategy pattern:
    - Trend filter: fast EMA vs slow EMA
    - Momentum trigger: RSI crossing configurable levels
    """

    def __init__(
        self,
        fast_ema_period: int,
        slow_ema_period: int,
        rsi_period: int,
        rsi_buy_threshold: float,
        rsi_sell_threshold: float,
    ) -> None:
        if fast_ema_period >= slow_ema_period:
            raise ValueError("fast_ema_period muss kleiner als slow_ema_period sein")
        self.fast_ema_period = fast_ema_period
        self.slow_ema_period = slow_ema_period
        self.rsi_period = rsi_period
        self.rsi_buy_threshold = rsi_buy_threshold
        self.rsi_sell_threshold = rsi_sell_threshold
        self.state = StrategyState(prices=[])

    def update_params(
        self,
        fast_ema_period: int | None = None,
        slow_ema_period: int | None = None,
        rsi_period: int | None = None,
        rsi_buy_threshold: float | None = None,
        rsi_sell_threshold: float | None = None,
    ) -> None:
        if fast_ema_period is not None:
            self.fast_ema_period = fast_ema_period
        if slow_ema_period is not None:
            self.slow_ema_period = slow_ema_period
        if rsi_period is not None:
            self.rsi_period = rsi_period
        if rsi_buy_threshold is not None:
            self.rsi_buy_threshold = rsi_buy_threshold
        if rsi_sell_threshold is not None:
            self.rsi_sell_threshold = rsi_sell_threshold
        if self.fast_ema_period >= self.slow_ema_period:
            raise ValueError("Nach Anpassung gilt fast_ema_period >= slow_ema_period")

    def on_price(self, price: float) -> Signal:
        self.state.prices.append(price)
        max_keep = max(self.slow_ema_period * 4, self.rsi_period * 4)
        if len(self.state.prices) > max_keep:
            self.state.prices = self.state.prices[-max_keep:]

        self.state.fast_ema = self._next_ema(self.state.fast_ema, price, self.fast_ema_period)
        self.state.slow_ema = self._next_ema(self.state.slow_ema, price, self.slow_ema_period)

        if len(self.state.prices) < self.rsi_period + 1:
            return "hold"

        current_rsi = self._calc_rsi(self.state.prices, self.rsi_period)
        previous_rsi = self.state.last_rsi
        self.state.last_rsi = current_rsi

        if previous_rsi is None or self.state.fast_ema is None or self.state.slow_ema is None:
            return "hold"

        trend_up = self.state.fast_ema > self.state.slow_ema
        trend_down = self.state.fast_ema < self.state.slow_ema

        crossed_buy = previous_rsi <= self.rsi_buy_threshold < current_rsi
        crossed_sell = previous_rsi >= self.rsi_sell_threshold > current_rsi

        if trend_up and crossed_buy:
            return "buy"
        if trend_down and crossed_sell:
            return "sell"
        return "hold"

    @staticmethod
    def _next_ema(previous: float | None, price: float, period: int) -> float:
        alpha = 2 / (period + 1)
        if previous is None:
            return price
        return (price * alpha) + (previous * (1 - alpha))

    @staticmethod
    def _calc_rsi(prices: List[float], period: int) -> float:
        deltas = [prices[i] - prices[i - 1] for i in range(len(prices) - period, len(prices))]
        gains = [d for d in deltas if d > 0]
        losses = [-d for d in deltas if d < 0]

        avg_gain = sum(gains) / period if gains else 0.0
        avg_loss = sum(losses) / period if losses else 0.0
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
