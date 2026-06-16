import socket
import time
import re
from pathlib import Path

HOST = "192.168.78.128"
DEVICES = {
    "R1": 2001,
    "R2": 2002,
    "R3": 2003,
    "ISP": 2004,
    "SWA": 2005,
    "SWB": 2006,
    "SWC": 2007,
    "SWD": 2008,
    "BR": 2013,
}

BACKUP_DIR = Path(r"C:\Users\lukas\Downloads\CCNPlabs\backups")
PROMPT_RE = re.compile(rb"[>#]\s*$")


def read_until_prompt(sock, timeout=30):
    """Read data until we see a Cisco prompt ending in # or >."""
    sock.settimeout(timeout)
    buffer = b""
    last_data = time.time()
    while True:
        try:
            chunk = sock.recv(4096)
            if chunk:
                buffer += chunk
                last_data = time.time()
                # Check if last non-empty line ends with prompt
                lines = buffer.split(b"\n")
                last_line = lines[-1].strip()
                if last_line.endswith(b">") or last_line.endswith(b"#"):
                    return buffer
            else:
                # No data; if we've waited enough, return what we have
                if time.time() - last_data > 3:
                    return buffer
        except socket.timeout:
            return buffer


def send_command(sock, cmd, wait=2):
    sock.sendall((cmd + "\r\n").encode("ascii", errors="ignore"))
    time.sleep(wait)
    return read_until_prompt(sock, timeout=10)


def backup_device(name, port):
    print(f"[{name}] Connecting to {HOST}:{port} ...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect((HOST, port))
    except Exception as e:
        print(f"[{name}] Connection failed: {e}")
        return False

    # Wait for initial prompt
    banner = read_until_prompt(sock, timeout=15)
    print(f"[{name}] Banner received ({len(banner)} bytes)")

    # Send commands
    send_command(sock, "", wait=1)  # wake up
    send_command(sock, "terminal length 0", wait=1)
    output = send_command(sock, "show running-config", wait=3)

    # Try to extract just the config portion (from first line to end)
    text = output.decode("utf-8", errors="replace")

    # Save raw output
    BACKUP_DIR.mkdir(exist_ok=True)
    raw_file = BACKUP_DIR / f"{name.lower()}_show_run_raw.txt"
    raw_file.write_text(text, encoding="utf-8")

    # Try to clean up: find first occurrence of a config line and keep from there
    # Heuristic: Cisco configs usually start with 'Building configuration...' or 'Current configuration'
    clean = text
    for marker in ["Building configuration...", "Current configuration", "version "]:
        idx = text.find(marker)
        if idx != -1:
            clean = text[idx:]
            break

    clean_file = BACKUP_DIR / f"{name.lower()}_running-config.cfg"
    clean_file.write_text(clean, encoding="utf-8")

    sock.close()
    print(f"[{name}] Saved {len(text)} chars -> {clean_file}")
    return True


def main():
    for name, port in DEVICES.items():
        backup_device(name, port)


if __name__ == "__main__":
    main()
