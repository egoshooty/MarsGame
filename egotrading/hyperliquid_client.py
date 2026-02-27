from __future__ import annotations

from dataclasses import dataclass
import logging

from .http_client import post_json

LOGGER = logging.getLogger(__name__)


@dataclass
class Position:
    side: str = "flat"
    size: float = 0.0


class HyperliquidClient:
    def __init__(self, symbol: str, testnet: bool = True, dry_run: bool = True, private_key: str = "", account_address: str = "") -> None:
        self.symbol = symbol
        self.testnet = testnet
        self.dry_run = dry_run
        self.private_key = private_key
        self.account_address = account_address
        self.base_url = "https://api.hyperliquid-testnet.xyz" if testnet else "https://api.hyperliquid.xyz"
        self.position = Position()

    def fetch_mark_price(self) -> float:
        all_mids = post_json(f"{self.base_url}/info", {"type": "allMids"}, timeout=8)
        if self.symbol not in all_mids:
            raise KeyError(f"Symbol {self.symbol} nicht in allMids enthalten")
        return float(all_mids[self.symbol])

    def place_market_order(self, side: str, size: float) -> None:
        if side not in {"buy", "sell"}:
            raise ValueError("side muss buy/sell sein")

        if self.dry_run:
            LOGGER.info("[DRY_RUN] %s %.6f %s", side.upper(), size, self.symbol)
            self._update_local_position(side, size)
            return

        try:
            from eth_account import Account
            from hyperliquid.exchange import Exchange
            from hyperliquid.utils import constants
        except ImportError as exc:
            raise RuntimeError(
                "Für Live-Trading installiere hyperliquid-python-sdk + eth-account und setze dry_run=false"
            ) from exc

        if not self.private_key:
            raise RuntimeError("private_key fehlt, Live-Trading ist nicht möglich")

        account = Account.from_key(self.private_key)
        api_url = constants.TESTNET_API_URL if self.testnet else constants.MAINNET_API_URL
        exchange = Exchange(account, api_url)

        px = self.fetch_mark_price()
        is_buy = side == "buy"
        slippage = 1.002 if is_buy else 0.998
        limit_px = round(px * slippage, 5)
        result = exchange.order(self.symbol, is_buy, size, limit_px, {"limit": {"tif": "Ioc"}})
        LOGGER.info("Order result: %s", result)
        self._update_local_position(side, size)

    def _update_local_position(self, side: str, size: float) -> None:
        if side == "buy":
            self.position.size += size
        elif side == "sell":
            self.position.size -= size

        if self.position.size > 0:
            self.position.side = "long"
        elif self.position.size < 0:
            self.position.side = "short"
        else:
            self.position.side = "flat"
