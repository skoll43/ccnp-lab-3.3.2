"""Verifica consistencia de configuraciones generadas para Lab 3.3.2.

Comprueba:
- Presencia de configuraciones clave (FHRP, OSPF, VPN, ACLs, BGP).
- Ausencia de errores comunes (tunnel mode gre multipoint, ip ospf passive invalido).
- Vecinos BGP correctos para cada router.
- Consistencia de HSRP priorities.
- VLAN names correctos.
"""

from pathlib import Path
import re
import sys

CONFIGS_DIR = Path(r"C:\Users\lukas\Downloads\CCNPlabs\configs")

REQUIRED = {
    "swc_layer2.cfg": [
        "ip access-group PACL_BLOCK_21_22 in",
        "ipv6 traffic-filter PACL6_BLOCK_21_22 in",
        "vlan filter VACL_BLOCK_23_24 vlan-list 23,24",
    ],
    "r1_base.cfg": [
        "ip dhcp pool VLAN21",
        "ipv6 dhcp pool VLAN21",
        "interface Ethernet0/3",
        "209.50.0.1",
    ],
    "r2_base.cfg": [
        "passive-interface default",
        "no passive-interface Ethernet0/1",
        "no passive-interface Tunnel0",
        "ip access-group ACL_BLOCK_23_24 in",
        "ipv6 traffic-filter ACL6_BLOCK_23_24 in",
        "standby 21 priority 110",
        "standby 23 priority 100",
    ],
    "r3_base.cfg": [
        "passive-interface default",
        "no passive-interface Ethernet0/2",
        "no passive-interface Tunnel0",
        "ip access-group ACL_BLOCK_23_24 in",
        "ipv6 traffic-filter ACL6_BLOCK_23_24 in",
        "standby 23 priority 110",
        "standby 21 priority 100",
    ],
    "r2_vpn.cfg": [
        "tunnel mode gre ip",
        "tunnel protection ipsec profile VPN-PROFILE",
        "tunnel destination 3.3.3.3",
    ],
    "r3_vpn.cfg": [
        "tunnel mode gre ip",
        "tunnel protection ipsec profile VPN-PROFILE",
        "tunnel destination 2.2.2.2",
    ],
    "r1_bgp.cfg": [
        "neighbor 209.50.0.2 remote-as 200",
        "neighbor 2.2.2.2 remote-as 100",
        "neighbor 3.3.3.3 remote-as 100",
        "redistribute ospf 1",
        "redistribute bgp 100",
    ],
    "r2_bgp.cfg": [
        "neighbor 1.1.1.1 remote-as 100",
        "neighbor 3.3.3.3 remote-as 100",
        "redistribute ospf 1",
        "redistribute bgp 100",
    ],
    "r3_bgp.cfg": [
        "neighbor 1.1.1.1 remote-as 100",
        "neighbor 2.2.2.2 remote-as 100",
        "redistribute ospf 1",
        "redistribute bgp 100",
    ],
    "isp.cfg": [
        "router bgp 200",
        "neighbor 209.50.0.1 remote-as 100",
        "neighbor 220.50.0.1 remote-as 300",
    ],
    "br.cfg": [
        "router bgp 300",
        "set as-path prepend 200",
        "set as-path prepend 200 200",
        "neighbor 220.50.0.2 remote-as 200",
    ],
}

FORBIDDEN = {
    "*.cfg": [
        "tunnel mode gre multipoint",
        "ip ospf 1 passive",
        "ip ospf passive",
    ],
}


def load_files():
    files = {}
    for f in CONFIGS_DIR.glob("*.cfg"):
        files[f.name] = f.read_text(encoding="utf-8")
    return files


def check_required(files):
    errors = []
    for fname, phrases in REQUIRED.items():
        if fname not in files:
            errors.append(f"Archivo faltante: {fname}")
            continue
        for phrase in phrases:
            if phrase not in files[fname]:
                errors.append(f"{fname}: falta '{phrase}'")
    return errors


def check_forbidden(files):
    errors = []
    for fname, text in files.items():
        for phrase in FORBIDDEN["*.cfg"]:
            if phrase in text:
                errors.append(f"{fname}: contiene '{phrase}' (no permitido)")
    return errors


def check_vlan_names(files):
    errors = []
    for sw in ["swa_layer2.cfg", "swb_layer2.cfg", "swc_layer2.cfg", "swd_layer2.cfg"]:
        text = files.get(sw, "")
        for vid, name in [(21, "FINANZAS"), (22, "GESTION"), (23, "FUERZA-VENTAS"), (24, "RRHH"), (25, "ADM")]:
            if f"vlan {vid}\n name {name}" not in text and f"vlan {vid}\r\n name {name}" not in text:
                errors.append(f"{sw}: VLAN {vid} '{name}' mal configurada")
    return errors


def check_bgp_consistency(files):
    errors = []
    # Cada iBGP AS100 debe tener exactamente los otros dos como vecinos
    ibgp_neighbors = {
        "r1_bgp.cfg": ["2.2.2.2", "3.3.3.3"],
        "r2_bgp.cfg": ["1.1.1.1", "3.3.3.3"],
        "r3_bgp.cfg": ["1.1.1.1", "2.2.2.2"],
    }
    for fname, expected in ibgp_neighbors.items():
        text = files.get(fname, "")
        for n in expected:
            if f"neighbor {n} remote-as 100" not in text:
                errors.append(f"{fname}: falta vecino iBGP {n}")
    return errors


def check_hsrp_consistency(files):
    errors = []
    # R2 active para 21/22; R3 active para 23/24/25
    for fname, active_vlans, standby_vlans in [
        ("r2_base.cfg", [21, 22], [23, 24, 25]),
        ("r3_base.cfg", [23, 24, 25], [21, 22]),
    ]:
        text = files.get(fname, "")
        for v in active_vlans:
            if f"standby {v} priority 110" not in text:
                errors.append(f"{fname}: VLAN{v} deberia tener priority 110 (activo)")
        for v in standby_vlans:
            if f"standby {v} priority 100" not in text:
                errors.append(f"{fname}: VLAN{v} deberia tener priority 100 (standby)")
    return errors


def main():
    files = load_files()
    print(f"Archivos encontrados: {len(files)}")

    errors = []
    errors.extend(check_required(files))
    errors.extend(check_forbidden(files))
    errors.extend(check_vlan_names(files))
    errors.extend(check_bgp_consistency(files))
    errors.extend(check_hsrp_consistency(files))

    if errors:
        print("\n[ERRORES]")
        for e in errors:
            print(f" - {e}")
        return 1
    print("\n[OK] Todas las verificaciones pasaron.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
