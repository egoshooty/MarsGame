from __future__ import annotations

import logging
import time

from .config import BotConfig
from .hyperliquid_client import HyperliquidClient
from .openclaw_bridge import OpenClawBridge
from .strategy import EmaRsiMomentumStrategy

LOGGER = logging.getLogger(__name__)


class AdaptiveHyperliquidBot:
    def __init__(self, config: BotConfig) -> None:
        self.config = config
        self.client = HyperliquidClient(
            symbol=config.strategy.symbol,
            testnet=config.testnet,
            dry_run=config.dry_run,
            private_key=config.private_key,
            account_address=config.account_address,
        )
        self.strategy = EmaRsiMomentumStrategy(
            fast_ema_period=config.strategy.fast_ema_period,
            slow_ema_period=config.strategy.slow_ema_period,
            rsi_period=config.strategy.rsi_period,
            rsi_buy_threshold=config.strategy.rsi_buy_threshold,
            rsi_sell_threshold=config.strategy.rsi_sell_threshold,
        )
        self.risk_per_trade = config.strategy.risk_per_trade
        self.max_position_size = config.strategy.max_position_size

        self.openclaw = OpenClawBridge(
            endpoint=config.openclaw.endpoint,
            instruction_file=config.openclaw.instruction_file,
        )
        self._last_openclaw_poll = 0.0

    def run_forever(self) -> None:
        LOGGER.info("Starte Bot für %s (testnet=%s, dry_run=%s)", self.config.strategy.symbol, self.config.testnet, self.config.dry_run)
        while True:
            try:
                self._tick()
            except Exception:
                LOGGER.exception("Fehler im Tick")
            time.sleep(self.config.loop_interval_seconds)

    def _tick(self) -> None:
        price = self.client.fetch_mark_price()
        signal = self.strategy.on_price(price)
        LOGGER.info("Price=%.4f Signal=%s Pos=%s %.4f", price, signal, self.client.position.side, self.client.position.size)

        if signal in {"buy", "sell"}:
            size = min(self.risk_per_trade, self.max_position_size)
            self.client.place_market_order(signal, size)

        if self.config.openclaw.enabled:
            now = time.time()
            if now - self._last_openclaw_poll >= self.config.openclaw.poll_seconds:
                self._apply_openclaw_changes()
                self._last_openclaw_poll = now

    def _apply_openclaw_changes(self) -> None:
        instruction = self.openclaw.poll()
        if not instruction:
            return

        if (
            instruction.fast_ema_period is not None
            or instruction.slow_ema_period is not None
            or instruction.rsi_period is not None
            or instruction.rsi_buy_threshold is not None
            or instruction.rsi_sell_threshold is not None
        ):
            self.strategy.update_params(
                fast_ema_period=instruction.fast_ema_period,
                slow_ema_period=instruction.slow_ema_period,
                rsi_period=instruction.rsi_period,
                rsi_buy_threshold=instruction.rsi_buy_threshold,
                rsi_sell_threshold=instruction.rsi_sell_threshold,
            )
            LOGGER.info(
                "OpenClaw update: fast=%s slow=%s rsi_period=%s buy_th=%s sell_th=%s",
                self.strategy.fast_ema_period,
                self.strategy.slow_ema_period,
                self.strategy.rsi_period,
                self.strategy.rsi_buy_threshold,
                self.strategy.rsi_sell_threshold,
            )

        if instruction.risk_per_trade is not None:
            self.risk_per_trade = max(0.0001, min(instruction.risk_per_trade, 1.0))
            LOGGER.info("OpenClaw update: risk_per_trade=%s", self.risk_per_trade)

        if instruction.max_position_size is not None:
            self.max_position_size = max(0.0001, instruction.max_position_size)
            LOGGER.info("OpenClaw update: max_position_size=%s", self.max_position_size)
