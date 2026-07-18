# **Smart Greenhouse**
An automated Smart Greenhouse system powered by Raspberry Pi 5 and ESP32. It features real-time environmental monitoring, automated controls, an integrated YOLO model for plant disease detection, and a Telegram bot for remote management.

- [Circuit Diagram](https://app.cirkitdesigner.com/project/183696b8-9d27-4965-9932-9f019460da95)
- [Documentation](https://drive.google.com/drive/folders/1LKRL6lX4Qb8MC_fYuJ-SylBiDjAKcroz?usp=drive_link)

---

## **Installation & Setup**

### 1. Clone the Repository
```bash
git clone <your-repository-link>
cd SmartGreenhouse

```

### 2. Setup Virtual Environment (Python)

Create a virtual environment named `venv` inside the root directory and install the required dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

> ⚠️ **Note:** Ensure your hardware configuration and dynamic credentials (like `credentials.json`) are correctly placed in the `Pi code` directory before running the scripts.

### 3. `credentials.json` Template

Create a file named `credentials.json` inside the `Pi code` directory with the following structure:

```json
{
    "telegram": {
        "api_id": 123456,
        "api_hash": "your_api_hash_here",
        "bot_token": "your_bot_token_here"
    }
}

```

---

## Deployment & Background Services

To ensure the greenhouse system and Telegram bot run automatically on every system boot, we use Linux `systemd` services.

### 1. Setup Main Core Service

```bash
sudo nano /etc/systemd/system/greenhouse_main.service

```

```ini
[Unit]
Description=Greenhouse ESP Core Service
After=network.target

[Service]
Type=simple
User=greenhouse
WorkingDirectory=/home/greenhouse/SmartGreenhouse
ExecStart=/home/greenhouse/SmartGreenhouse/venv/bin/python3 main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

```

### 2. Setup Telegram Bot Service

```bash
sudo nano /etc/systemd/system/greenhouse_bot.service

```

```ini
[Unit]
Description=Greenhouse Telegram Bot Service
After=network.target

[Service]
Type=simple
User=greenhouse
WorkingDirectory=/home/greenhouse/SmartGreenhouse
ExecStart=/home/greenhouse/SmartGreenhouse/venv/bin/python3 tlg_bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

```

### 3. Service Management Commands

```bash
# Reload systemd manager configuration to recognize new service files
sudo systemctl daemon-reload

# Enable services to launch automatically on system boot
sudo systemctl enable greenhouse_main.service greenhouse_bot.service

# Start services immediately in the background (Reboot recommended)
sudo systemctl start greenhouse_main.service greenhouse_bot.service

# Monitor live, real-time logs and prints from the application
journalctl -u greenhouse_main.service -f
journalctl -u greenhouse_bot.service -f

# Check the current operational status of the background services
sudo systemctl status greenhouse_main.service greenhouse_bot.service

# Restart services manually to apply updates or fix runtime issues
sudo systemctl restart greenhouse_main.service greenhouse_bot.service

# Stop services in the current session (Will still launch on next boot)
sudo systemctl stop greenhouse_main.service greenhouse_bot.service

# Disable services to prevent them from launching on future system boots
sudo systemctl disable greenhouse_main.service greenhouse_bot.service

```
