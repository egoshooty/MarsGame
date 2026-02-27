from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict

from .http_client import get_json


@dataclass
class OpenClawInstruction:
    fast_ema_period: int | None = None
    slow_ema_period: int | None = None
    rsi_period: int | None = None
    rsi_buy_threshold: float | None = None
    rsi_sell_threshold: float | None = None
    risk_per_trade: float | None = None
    max_position_size: float | None = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "OpenClawInstruction":
        return OpenClawInstruction(
            fast_ema_period=int(data["fast_ema_period"]) if "fast_ema_period" in data else None,
            slow_ema_period=int(data["slow_ema_period"]) if "slow_ema_period" in data else None,
            rsi_period=int(data["rsi_period"]) if "rsi_period" in data else None,
            rsi_buy_threshold=float(data["rsi_buy_threshold"]) if "rsi_buy_threshold" in data else None,
            rsi_sell_threshold=float(data["rsi_sell_threshold"]) if "rsi_sell_threshold" in data else None,
            risk_per_trade=float(data["risk_per_trade"]) if "risk_per_trade" in data else None,
            max_position_size=float(data["max_position_size"]) if "max_position_size" in data else None,
        )


class OpenClawBridge:
    def __init__(self, endpoint: str, instruction_file: str) -> None:
        self.endpoint = endpoint.strip()
        self.instruction_file = Path(instruction_file)

    def poll(self) -> OpenClawInstruction | None:
        if self.endpoint:
            payload = get_json(self.endpoint, timeout=5)
            return OpenClawInstruction.from_dict(payload)

        if self.instruction_file.exists():
            payload = json.loads(self.instruction_file.read_text(encoding="utf-8"))
            self.instruction_file.write_text("{}", encoding="utf-8")
            return OpenClawInstruction.from_dict(payload)

        return None
