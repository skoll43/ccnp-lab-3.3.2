"""
backup_lab16.py — Backup de running-config de los dispositivos del Lab 16 (vía netmiko).

IOU/IOU host: 192.168.119.129
Dispositivos routers/switches del lab 16:

  BR   port 2001
  ISP  port 2002
  RB   port 2003
  RA   port 2004
  MLS1 port 2005
  MLS2 port 2006
  ALS1 port 2007
  ALS2 port 2008

Uso:
    python backup_lab16.py                 # backup de todos
    python backup_lab16.py BR 2001         # backup de un solo dispositivo
"""

import sys
import time
from pathlib import Path
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException

HOST = "192.168.119.129"
BACKUP_DIR = Path(__file__).parent / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

# Routers y switches (los PCs devuelven configs vacías en IOL)
DEVICES = {
    "BR":   2001,
    "ISP":  2002,
    "RB":   2003,
    "RA":   2004,
    "MLS1": 2005,
    "MLS2": 2006,
    "ALS1": 2007,
    "ALS2": 2008,
}


def device_params(name, port):
    return {
        "device_type": "cisco_ios_telnet",
        "host": HOST,
        "port": port,
        "username": "",
        "password": "",
        "secret": "",
        "timeout": 60,
        "banner_timeout": 60,
        "auth_timeout": 60,
        "fast_cli": False,
        "session_log": str(BACKUP_DIR / f"{name.lower()}_session.log"),
    }


def backup_device(name, port):
    print(f"[{name}] Conectando a {HOST}:{port} ...", flush=True)
    try:
        conn = ConnectHandler(**device_params(name, port))
    except (NetMikoTimeoutException, NetMikoAuthenticationException) as e:
        print(f"[{name}] Error: {e}")
        return False
    except Exception as e:
        print(f"[{name}] Error inesperado: {e}")
        return False

    try:
        prompt = conn.find_prompt()
        print(f"[{name}] Conectado. Prompt: {prompt}")

        # Intentar entrar a enable (puede que no requiera password)
        try:
            conn.enable()
        except Exception:
            pass

        # Desactivar paginación y domain-lookup
        conn.send_command("terminal length 0")
        conn.send_command("no ip domain-lookup")

        # show running-config
        run_cfg = conn.send_command("show running-config", read_timeout=60)
        cfg_file = BACKUP_DIR / f"{name.lower()}_running-config.cfg"
        cfg_file.write_text(run_cfg, encoding="utf-8")
        print(f"[{name}] running-config -> {cfg_file.name} ({len(run_cfg)} chars)")

        # show version
        ver = conn.send_command("show version", read_timeout=30)
        ver_file = BACKUP_DIR / f"{name.lower()}_version.txt"
        ver_file.write_text(ver, encoding="utf-8")
        print(f"[{name}] version -> {ver_file.name} ({len(ver)} chars)")

        return True
    finally:
        try:
            conn.disconnect()
        except Exception:
            pass


def main():
    if len(sys.argv) == 3:
        name = sys.argv[1].upper()
        port = int(sys.argv[2])
        backup_device(name, port)
        return

    print(f"=== Backup Lab 16 ({len(DEVICES)} dispositivos) ===")
    print(f"Host: {HOST}")
    print(f"Destino: {BACKUP_DIR}\n")
    ok = 0
    for name, port in DEVICES.items():
        if backup_device(name, port):
            ok += 1
        time.sleep(1)
    print(f"\n=== Finalizado: {ok}/{len(DEVICES)} OK ===")


if __name__ == "__main__":
    main()
