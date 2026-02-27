from __future__ import annotations

import argparse
import logging

from .bot import AdaptiveHyperliquidBot
from .config import load_config
from .setup_wizard import run_setup


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EgoTrading Hyperliquid Testnet Trading Bot")
    parser.add_argument("--config", default="egotrading/config.example.json", help="Pfad zur JSON-Konfiguration")
    parser.add_argument("--init-config", action="store_true", help="Interaktiven Assistenten zum Erstellen der Konfiguration starten")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
    args = parse_args()

    if args.init_config:
        run_setup(args.config)
        return

    config = load_config(args.config)
    bot = AdaptiveHyperliquidBot(config)
    bot.run_forever()


if __name__ == "__main__":
    main()
