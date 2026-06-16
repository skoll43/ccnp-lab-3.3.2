from netmiko import ConnectHandler
from pathlib import Path
import time

HOST = "192.168.78.128"
DEVICES = [
    {"name": "R1", "port": 2001},
    {"name": "R2", "port": 2002},
    {"name": "R3", "port": 2003},
    {"name": "ISP", "port": 2004},
    {"name": "SWA", "port": 2005},
    {"name": "SWB", "port": 2006},
    {"name": "SWC", "port": 2007},
    {"name": "SWD", "port": 2008},
    {"name": "BR", "port": 2013},
]

BACKUP_DIR = Path(r"C:\Users\lukas\Downloads\CCNPlabs\backups")
BACKUP_DIR.mkdir(exist_ok=True)


def backup_device(name, port):
    print(f"[{name}] Connecting to {HOST}:{port} ...")
    device = {
        "device_type": "cisco_ios_telnet",
        "host": HOST,
        "port": port,
        "username": "",
        "password": "",
        "secret": "",
        "fast_cli": False,
        "session_log": str(BACKUP_DIR / f"{name.lower()}_session.log"),
        "timeout": 20,
        "banner_timeout": 20,
        "conn_timeout": 20,
    }

    try:
        conn = ConnectHandler(**device)
        print(f"[{name}] Connected. Prompt: {conn.find_prompt()}")

        # Enter enable mode (no password expected)
        conn.enable()
        print(f"[{name}] Enabled. Prompt: {conn.find_prompt()}")

        # Disable pagination
        conn.send_command("terminal length 0")

        # Backup running-config
        config = conn.send_command("show running-config", read_timeout=60)
        cfg_file = BACKUP_DIR / f"{name.lower()}_running-config.cfg"
        cfg_file.write_text(config, encoding="utf-8")
        print(f"[{name}] Running-config saved ({len(config)} chars) -> {cfg_file}")

        # Backup version for parsing
        version = conn.send_command("show version")
        ver_file = BACKUP_DIR / f"{name.lower()}_version.txt"
        ver_file.write_text(version, encoding="utf-8")
        print(f"[{name}] Version saved -> {ver_file}")

        conn.disconnect()
        return True
    except Exception as e:
        print(f"[{name}] ERROR: {e}")
        return False


def main():
    for dev in DEVICES:
        backup_device(dev["name"], dev["port"])
        time.sleep(1)


if __name__ == "__main__":
    main()
