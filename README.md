# ego_trading

Python-basiertes Trading-Projekt für automatisches Trading auf dem **Hyperliquid Testnet** mit **OpenClaw-Überwachung**.

## Schnellinstallation auf VPS (ohne GitHub-Login)

Da das Repo public ist, kannst du direkt per Script installieren:

```bash
sudo apt update && sudo apt install -y curl python3 python3-venv python3-pip
curl -fsSL https://raw.githubusercontent.com/<DEIN_USER>/ego_trading/main/scripts/install_vps.sh | bash
```

Optional mit Parametern:

```bash
curl -fsSL https://raw.githubusercontent.com/<DEIN_USER>/ego_trading/main/scripts/install_vps.sh | \
  bash -s -- --repo <DEIN_USER>/ego_trading --ref main --dir /root/ego_trading
```

Danach:

```bash
source ~/ego_trading/.venv/bin/activate
python -m egotrading.main --init-config --config egotrading/config.json
python -m egotrading.main --config egotrading/config.json
```

## Klassische Installation per git clone

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip

git clone https://github.com/<DEIN_USER>/ego_trading.git
cd ego_trading

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r egotrading/requirements.txt
```

## Konfiguration

Interaktiv (empfohlen):

```bash
python -m egotrading.main --init-config --config egotrading/config.json
```

Manuell:

```bash
cp egotrading/config.example.json egotrading/config.json
nano egotrading/config.json
```

Wichtige Felder:
- `private_key`: dein API/Signer Private Key
- `account_address`: deine öffentliche Wallet/Konto-ID
- `dry_run`: für echte Orders auf `false`

## systemd (Autostart)

`/etc/systemd/system/egotrading.service`:

```ini
[Unit]
Description=ego_trading Hyperliquid Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ego_trading
Environment=PYTHONUNBUFFERED=1
ExecStart=/root/ego_trading/.venv/bin/python -m egotrading.main --config /root/ego_trading/egotrading/config.json
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Aktivieren:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now egotrading
sudo systemctl status egotrading
sudo journalctl -u egotrading -f
```

## Release bauen (für GitHub Releases)

Lokales Paket bauen:

```bash
./scripts/package_release.sh
```

Automatisch als GitHub Release (ohne Login auf VPS):
- Tag pushen: `git tag v0.2.0 && git push origin v0.2.0`
- GitHub Action erstellt automatisch ein `dist/*.tar.gz` Release-Asset.

## Sicherheit

```bash
chmod 600 egotrading/config.json
```

- Starte zuerst immer mit `dry_run: true`.
- Für Live-Orders `dry_run: false` + gültigen Private Key setzen.
