"""
push_lab16.py — Push de configuraciones a los routers del Lab 16 vía netmiko.

IOU/IOU host: 192.168.119.129
Los routers ya están corriendo. Aplica las configs generadas por
generate_router_configs.py y las guarda en NVRAM (unix:config-00001
porque IOL/IOU no soporta 'write memory').

Uso:
    python push_lab16.py                  # push a todos los routers en orden
    python push_lab16.py BR 2001 br.cfg   # push de un solo router
"""

import sys
import time
from pathlib import Path
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException

HOST = "192.168.119.129"
BASE = Path(__file__).parent
CONFIGS_DIR = BASE / "configs"
BACKUP_DIR = BASE / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

DEVICES = {
    "BR":  (2001, "br.cfg"),
    "ISP": (2002, "isp.cfg"),
    "RB":  (2003, "rb.cfg"),
    "RA":  (2004, "ra.cfg"),
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
        "session_log": str(BACKUP_DIR / f"{name.lower()}_push.log"),
    }


def _clean_config(path):
    """Lee un archivo .cfg, elimina comentarios (líneas '!') y líneas vacías.
    Devuelve una lista de comandos, sin las líneas 'end' ni 'write memory'
    (las maneja el script de push)."""
    cmds = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.lstrip().startswith("!"):
            continue
        if line.strip() in ("end", "write memory"):
            continue
        cmds.append(line)
    return cmds


def push_one(name, port, cfg_file):
    cfg_path = CONFIGS_DIR / cfg_file
    if not cfg_path.exists():
        print(f"[{name}] No existe {cfg_path}")
        return False

    print(f"[{name}] Conectando a {HOST}:{port} ...", flush=True)
    try:
        conn = ConnectHandler(**device_params(name, port))
    except Exception as e:
        print(f"[{name}] Error de conexión: {e}")
        return False

    try:
        print(f"[{name}] Conectado. Prompt: {conn.find_prompt()}")

        # Si el dispositivo fue recién limpiado, aparece el "initial
        # configuration dialog". Hay que descartarlo antes de cualquier otra
        # cosa, si no todos los comandos se pierden mientras el router sigue
        # preguntando yes/no.
        initial = conn.send_command_timing("\n\n", read_timeout=5)
        if "initial configuration" in initial.lower() or "yes/no" in initial.lower():
            print(f"[{name}] Detectado setup dialog, descartando ...")
            conn.send_command_timing("no", read_timeout=5)
            # seguir enviando CR hasta que aparezca un prompt valido
            for _ in range(30):
                conn.send_command_timing("\n", read_timeout=3)
                p = conn.find_prompt()
                if p and (p.endswith(">") or p.endswith("#")) and "yes/no" not in p:
                    break
            print(f"[{name}] Setup dialog descartado. Prompt: {conn.find_prompt()}")

        try:
            conn.enable()
            print(f"[{name}] Enabled. Prompt: {conn.find_prompt()}")
        except Exception:
            print(f"[{name}] enable no requerido / no disponible")

        # Paginación off
        conn.send_command("terminal length 0")

        # Aplicar la config filtrada con send_config_set (maneja config-mode
        # prompts correctamente). Las líneas '!' y vacías se eliminan en
        # _clean_config para evitar que IOL telnet confunda caracteres
        # Unicode (p.ej. em-dash) con bytes de control.
        cmds = _clean_config(cfg_path)
        print(f"[{name}] Aplicando {len(cmds)} comandos desde {cfg_path.name} ...",
              flush=True)
        out = conn.send_config_set(cmds, read_timeout=30)
        print(f"[{name}] Config aplicada ({len(out)} chars de output).")
        # NO enviar un 'end' extra aquí: send_config_set ya regresa a EXEC.
        # Un 'end' adicional en EXEC dispara DNS lookup ("Translating end...")
        # y deja la consola colgada.

        # Guardar en unix: (IOL no soporta 'write memory')
        try:
            # send_command_timing evita regex matching — más robusto en IOL
            conn.send_command_timing(
                "copy running-config unix:config-00001", read_timeout=15
            )
            time.sleep(1)
            conn.send_command_timing("\n", read_timeout=10)
            time.sleep(0.5)
            conn.send_command_timing("\n", read_timeout=10)
            print(f"[{name}] Guardado en unix:config-00001.")
        except Exception as e:
            print(f"[{name}] Aviso al guardar: {e}")

        return True
    finally:
        # Cierre explícito: disconnect cierra el socket telnet y libera el puerto
        try:
            if conn.is_alive():
                conn.disconnect()
        except Exception:
            try:
                conn.cleanup()
            except Exception:
                pass


def main():
    if len(sys.argv) == 4:
        name = sys.argv[1].upper()
        port = int(sys.argv[2])
        cfg = sys.argv[3]
        push_one(name, port, cfg)
        return

    print(f"=== Push Lab 16 ({len(DEVICES)} routers) ===")
    print(f"Host: {HOST}")
    print(f"Configs en: {CONFIGS_DIR}\n")
    ok = 0
    for name, (port, cfg) in DEVICES.items():
        if push_one(name, port, cfg):
            ok += 1
        time.sleep(1)  # pequeño respiro entre dispositivos
    print(f"\n=== Finalizado: {ok}/{len(DEVICES)} OK ===")


if __name__ == "__main__":
    main()
