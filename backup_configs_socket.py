import socket
import time
import select
from pathlib import Path

HOST = "192.168.78.128"
DEVICES = [
    ("R1", 2001),
    ("R2", 2002),
    ("R3", 2003),
    ("ISP", 2004),
    ("SWA", 2005),
    ("SWB", 2006),
    ("SWC", 2007),
    ("SWD", 2008),
    ("BR", 2013),
]

BACKUP_DIR = Path(r"C:\Users\lukas\Downloads\CCNPlabs\backups")
BACKUP_DIR.mkdir(exist_ok=True)


def recv_all(sock, timeout=5):
    """Receive all available data within timeout."""
    data = b""
    start = time.time()
    while True:
        ready, _, _ = select.select([sock], [], [], 0.2)
        if ready:
            chunk = sock.recv(8192)
            if chunk:
                data += chunk
                start = time.time()
            else:
                break
        if time.time() - start > timeout:
            break
    return data


def wait_for_prompt(sock, markers=(b">", b"#"), timeout=10):
    """Read until we see a prompt ending with > or #."""
    data = b""
    start = time.time()
    while time.time() - start < timeout:
        ready, _, _ = select.select([sock], [], [], 0.2)
        if ready:
            chunk = sock.recv(8192)
            if chunk:
                data += chunk
                # Check if any line ends with prompt marker
                for line in data.split(b"\n"):
                    line = line.strip()
                    if line.endswith(markers):
                        return data
    return data


def send_line(sock, line, delay=0.5):
    sock.sendall((line + "\r\n").encode("ascii", errors="ignore"))
    time.sleep(delay)


def backup_device(name, port):
    print(f"[{name}] Connecting to {HOST}:{port} ...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    try:
        sock.connect((HOST, port))
    except Exception as e:
        print(f"[{name}] Connection error: {e}")
        return False

    # Give console time to settle and send CR to wake it
    time.sleep(1)
    send_line(sock, "", delay=1)
    banner = wait_for_prompt(sock, timeout=10)
    print(f"[{name}] Initial prompt: {banner.decode('utf-8', errors='replace').strip()[-80:]!r}")

    # Enter enable mode
    send_line(sock, "enable", delay=1)
    enable_out = wait_for_prompt(sock, timeout=10)
    prompt_text = enable_out.decode("utf-8", errors="replace").strip().split("\n")[-1]
    print(f"[{name}] After enable: {prompt_text[-80:]!r}")

    # Disable pagination and domain lookup
    send_line(sock, "terminal length 0", delay=0.5)
    send_line(sock, "no ip domain-lookup", delay=0.5)

    # Get running-config
    send_line(sock, "show running-config", delay=2)
    config = recv_all(sock, timeout=10)
    config_text = config.decode("utf-8", errors="replace")

    # Save raw capture
    raw_file = BACKUP_DIR / f"{name.lower()}_running-config_raw.txt"
    raw_file.write_text(banner.decode("utf-8", errors="replace") + "\n" + enable_out.decode("utf-8", errors="replace") + "\n" + config_text, encoding="utf-8")

    # Extract config body: from first line containing 'version ' or 'Current configuration'
    clean = config_text
    for marker in ["Building configuration...", "Current configuration", "version "]:
        idx = config_text.find(marker)
        if idx != -1:
            clean = config_text[idx:]
            break

    cfg_file = BACKUP_DIR / f"{name.lower()}_running-config.cfg"
    cfg_file.write_text(clean, encoding="utf-8")

    # Get version info
    send_line(sock, "show version", delay=2)
    version = recv_all(sock, timeout=8)
    ver_file = BACKUP_DIR / f"{name.lower()}_version.txt"
    ver_file.write_text(version.decode("utf-8", errors="replace"), encoding="utf-8")

    sock.close()
    print(f"[{name}] Saved config ({len(clean)} chars) -> {cfg_file}")
    return True


def main():
    for name, port in DEVICES:
        try:
            backup_device(name, port)
        except Exception as e:
            print(f"[{name}] ERROR: {type(e).__name__}: {e}")
        time.sleep(1)


if __name__ == "__main__":
    main()
