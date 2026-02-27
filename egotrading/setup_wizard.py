from __future__ import annotations

import getpass
import json
from pathlib import Path

from .config import BotConfig


def _ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def _ask_bool(prompt: str, default: bool) -> bool:
    default_text = "y" if default else "n"
    value = _ask(f"{prompt} (y/n)", default_text).lower()
    return value in {"y", "yes", "1", "true", "t"}


def run_setup(config_path: str) -> Path:
    target = Path(config_path)
    cfg = BotConfig()

    print("=== EgoTrading Konfigurationsassistent ===")
    cfg.testnet = _ask_bool("Hyperliquid Testnet verwenden", True)
    cfg.dry_run = _ask_bool("Dry-Run (keine echten Orders)", True)

    if not cfg.dry_run:
        cfg.private_key = getpass.getpass("API Private Key (wird nicht angezeigt): ").strip()
        cfg.account_address = _ask("Wallet/Konto-Adresse (public address)")

    cfg.strategy.symbol = _ask("Symbol", cfg.strategy.symbol)
    cfg.strategy.fast_ema_period = int(_ask("Fast EMA Periode", str(cfg.strategy.fast_ema_period)))
    cfg.strategy.slow_ema_period = int(_ask("Slow EMA Periode", str(cfg.strategy.slow_ema_period)))
    cfg.strategy.rsi_period = int(_ask("RSI Periode", str(cfg.strategy.rsi_period)))
    cfg.strategy.rsi_buy_threshold = float(_ask("RSI Buy Threshold", str(cfg.strategy.rsi_buy_threshold)))
    cfg.strategy.rsi_sell_threshold = float(_ask("RSI Sell Threshold", str(cfg.strategy.rsi_sell_threshold)))
    cfg.strategy.risk_per_trade = float(_ask("Risk per trade", str(cfg.strategy.risk_per_trade)))
    cfg.strategy.max_position_size = float(_ask("Max position size", str(cfg.strategy.max_position_size)))

    cfg.openclaw.enabled = _ask_bool("OpenClaw aktivieren", cfg.openclaw.enabled)
    if cfg.openclaw.enabled:
        cfg.openclaw.endpoint = _ask("OpenClaw Endpoint URL (optional)", cfg.openclaw.endpoint)
        cfg.openclaw.instruction_file = _ask("OpenClaw Instruction-Datei", cfg.openclaw.instruction_file)

    payload = {
        "testnet": cfg.testnet,
        "dry_run": cfg.dry_run,
        "private_key": cfg.private_key,
        "account_address": cfg.account_address,
        "loop_interval_seconds": cfg.loop_interval_seconds,
        "strategy": {
            "symbol": cfg.strategy.symbol,
            "timeframe_seconds": cfg.strategy.timeframe_seconds,
            "fast_ema_period": cfg.strategy.fast_ema_period,
            "slow_ema_period": cfg.strategy.slow_ema_period,
            "rsi_period": cfg.strategy.rsi_period,
            "rsi_buy_threshold": cfg.strategy.rsi_buy_threshold,
            "rsi_sell_threshold": cfg.strategy.rsi_sell_threshold,
            "risk_per_trade": cfg.strategy.risk_per_trade,
            "max_position_size": cfg.strategy.max_position_size,
        },
        "openclaw": {
            "enabled": cfg.openclaw.enabled,
            "endpoint": cfg.openclaw.endpoint,
            "instruction_file": cfg.openclaw.instruction_file,
            "poll_seconds": cfg.openclaw.poll_seconds,
        },
    }

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Konfiguration gespeichert: {target}")
    return target
