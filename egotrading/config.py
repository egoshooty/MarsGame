from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict


@dataclass
class StrategyConfig:
    symbol: str = "ETH"
    timeframe_seconds: int = 60
    fast_ema_period: int = 9
    slow_ema_period: int = 21
    rsi_period: int = 14
    rsi_buy_threshold: float = 55.0
    rsi_sell_threshold: float = 45.0
    risk_per_trade: float = 0.01
    max_position_size: float = 0.05


@dataclass
class OpenClawConfig:
    enabled: bool = True
    endpoint: str = ""
    instruction_file: str = "openclaw_instructions.json"
    poll_seconds: int = 15


@dataclass
class BotConfig:
    testnet: bool = True
    dry_run: bool = True
    private_key: str = ""
    account_address: str = ""
    loop_interval_seconds: int = 10
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    openclaw: OpenClawConfig = field(default_factory=OpenClawConfig)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "BotConfig":
        strategy_data = data.get("strategy", {})
        openclaw_data = data.get("openclaw", {})
        return BotConfig(
            testnet=bool(data.get("testnet", True)),
            dry_run=bool(data.get("dry_run", True)),
            private_key=str(data.get("private_key", "")),
            account_address=str(data.get("account_address", "")),
            loop_interval_seconds=int(data.get("loop_interval_seconds", 10)),
            strategy=StrategyConfig(
                symbol=str(strategy_data.get("symbol", "ETH")),
                timeframe_seconds=int(strategy_data.get("timeframe_seconds", 60)),
                fast_ema_period=int(strategy_data.get("fast_ema_period", 9)),
                slow_ema_period=int(strategy_data.get("slow_ema_period", 21)),
                rsi_period=int(strategy_data.get("rsi_period", 14)),
                rsi_buy_threshold=float(strategy_data.get("rsi_buy_threshold", 55.0)),
                rsi_sell_threshold=float(strategy_data.get("rsi_sell_threshold", 45.0)),
                risk_per_trade=float(strategy_data.get("risk_per_trade", 0.01)),
                max_position_size=float(strategy_data.get("max_position_size", 0.05)),
            ),
            openclaw=OpenClawConfig(
                enabled=bool(openclaw_data.get("enabled", True)),
                endpoint=str(openclaw_data.get("endpoint", "")),
                instruction_file=str(openclaw_data.get("instruction_file", "openclaw_instructions.json")),
                poll_seconds=int(openclaw_data.get("poll_seconds", 15)),
            ),
        )


def load_config(path: str | Path) -> BotConfig:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return BotConfig.from_dict(data)
