from netmiko import ConnectHandler
from pathlib import Path
import sys

HOST = "192.168.78.128"
BACKUP_DIR = Path(r"C:\Users\lukas\Downloads\CCNPlabs\backups")
BACKUP_DIR.mkdir(exist_ok=True)


def backup_one(name, port):
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
        "timeout": 30,
        "banner_timeout": 30,
        "conn_timeout": 30,
    }

    conn = ConnectHandler(**device)
    print(f"[{name}] Connected. Prompt: {conn.find_prompt()}")

    conn.enable()
    print(f"[{name}] Enabled. Prompt: {conn.find_prompt()}")

    conn.send_command("terminal length 0")
    conn.send_command("no ip domain-lookup")

    config = conn.send_command("show running-config", read_timeout=60)
    cfg_file = BACKUP_DIR / f"{name.lower()}_running-config.cfg"
    cfg_file.write_text(config, encoding="utf-8")
    print(f"[{name}] Running-config saved ({len(config)} chars) -> {cfg_file}")

    version = conn.send_command("show version")
    ver_file = BACKUP_DIR / f"{name.lower()}_version.txt"
    ver_file.write_text(version, encoding="utf-8")
    print(f"[{name}] Version saved ({len(version)} chars) -> {ver_file}")

    conn.disconnect()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python backup_one_device.py <NAME> <PORT>")
        sys.exit(1)
    backup_one(sys.argv[1], int(sys.argv[2]))
