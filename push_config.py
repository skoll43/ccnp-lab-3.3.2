"""Push a configuration file to a device via console Telnet."""

from netmiko import ConnectHandler
from pathlib import Path
import sys
import time

HOST = "192.168.78.128"


def push_config(name, port, config_file):
    print(f"[{name}] Connecting to {HOST}:{port} ...")
    device = {
        "device_type": "cisco_ios_telnet",
        "host": HOST,
        "port": port,
        "username": "",
        "password": "",
        "secret": "",
        "fast_cli": False,
        "session_log": str(Path(config_file).with_suffix(".log")),
        "timeout": 30,
        "banner_timeout": 30,
        "conn_timeout": 30,
    }

    conn = ConnectHandler(**device)
    print(f"[{name}] Connected. Prompt: {conn.find_prompt()}")
    conn.enable()
    print(f"[{name}] Enabled. Prompt: {conn.find_prompt()}")

    print(f"[{name}] Sending config from {config_file} ...")
    output = conn.send_config_from_file(config_file)
    print(f"[{name}] Config applied.")

    # Save to unix: filesystem (IOL/IOU NVRAM workaround)
    output = conn.send_command(
        "copy running-config unix:config-00001",
        expect_string=r"Destination filename",
        read_timeout=20,
    )
    output += conn.send_command("\n", expect_string=r"#", read_timeout=20)
    print(f"[{name}] Config saved to unix:config-00001.")

    conn.disconnect()
    print(f"[{name}] Done.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python push_configs.py <NAME> <PORT> <CONFIG_FILE>")
        sys.exit(1)
    push_config(sys.argv[1], int(sys.argv[2]), sys.argv[3])
