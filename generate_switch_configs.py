"""Generate Layer 2 switch configurations for the lab."""

from pathlib import Path

OUT_DIR = Path(r"C:\Users\lukas\Downloads\CCNPlabs\configs")
OUT_DIR.mkdir(exist_ok=True)

VLANS = {
    21: "FINANZAS",
    22: "GESTION",
    23: "FUERZA-VENTAS",
    24: "RRHH",
    25: "ADM",
}

SWITCH_DATA = {
    "SWA": {
        "trunk_to_router": "E0/3",
        "portchannels": {
            6: {"mode": "active", "protocol": "lacp", "members": ["E1/0", "E1/1"]},
            5: {"mode": "on", "protocol": "static", "members": ["E1/2", "E1/3"]},
            4: {"mode": "desirable", "protocol": "pagp", "members": ["E0/0", "E0/1"]},
        },
        "access_ports": [],
    },
    "SWB": {
        "trunk_to_router": "E0/3",
        "portchannels": {
            6: {"mode": "active", "protocol": "lacp", "members": ["E1/0", "E1/1"]},
            2: {"mode": "active", "protocol": "lacp", "members": ["E0/0", "E0/1"]},
            3: {"mode": "on", "protocol": "static", "members": ["E1/2", "E1/3"]},
        },
        "access_ports": [],
    },
    "SWC": {
        "trunk_to_router": None,
        "portchannels": {
            5: {"mode": "on", "protocol": "static", "members": ["E1/2", "E1/3"]},
            2: {"mode": "active", "protocol": "lacp", "members": ["E0/0", "E0/1"]},
            1: {"mode": "desirable", "protocol": "pagp", "members": ["E1/0", "E1/1"]},
        },
        "access_ports": [
            {"intf": "E0/2", "vlan": 21},
            {"intf": "E0/3", "vlan": 22},
        ],
    },
    "SWD": {
        "trunk_to_router": None,
        "portchannels": {
            4: {"mode": "desirable", "protocol": "pagp", "members": ["E0/0", "E0/1"]},
            3: {"mode": "on", "protocol": "static", "members": ["E1/2", "E1/3"]},
            1: {"mode": "desirable", "protocol": "pagp", "members": ["E1/0", "E1/1"]},
        },
        "access_ports": [
            {"intf": "E0/2", "vlan": 23},
            {"intf": "E0/3", "vlan": 24},
        ],
    },
}


def generate_switch_config(name, data):
    lines = [
        f"hostname {name}",
        "!",
        "spanning-tree mode rapid-pvst",
        "spanning-tree extend system-id",
        "!",
    ]

    # VLANs
    for vid, vname in VLANS.items():
        lines.append(f"vlan {vid}")
        lines.append(f" name {vname}")
    lines.append("!")

    # Access ports with port-security and BPDU guard
    for ap in data["access_ports"]:
        intf = ap["intf"]
        vlan = ap["vlan"]
        lines.extend([
            f"interface {intf}",
            " switchport mode access",
            f" switchport access vlan {vlan}",
            " spanning-tree bpduguard enable",
            " spanning-tree portfast",
            " switchport port-security",
            " switchport port-security maximum 2",
            " switchport port-security violation shutdown",
            " switchport port-security mac-address sticky",
            "!",
        ])

    # Router trunk
    if data["trunk_to_router"]:
        lines.extend([
            f"interface {data['trunk_to_router']}",
            " switchport trunk encapsulation dot1q",
            " switchport mode trunk",
            " switchport trunk allowed vlan 21-25",
            " spanning-tree guard root",
            "!",
        ])

    # EtherChannels
    for po_id, po in data["portchannels"].items():
        # Member interfaces
        for member in po["members"]:
            lines.extend([
                f"interface {member}",
                " switchport trunk encapsulation dot1q",
                " switchport mode trunk",
                " switchport trunk allowed vlan 21-25",
                f" channel-group {po_id} mode {po['mode']}",
                " spanning-tree guard root",
                "!",
            ])
        # Port-channel interface
        lines.extend([
            f"interface Port-channel {po_id}",
            " switchport trunk encapsulation dot1q",
            " switchport mode trunk",
            " switchport trunk allowed vlan 21-25",
            "!",
        ])

    lines.append("end")
    return "\n".join(lines)


def main():
    for name, data in SWITCH_DATA.items():
        cfg = generate_switch_config(name, data)
        path = OUT_DIR / f"{name.lower()}_layer2.cfg"
        path.write_text(cfg, encoding="utf-8")
        print(f"Generated {path}")


if __name__ == "__main__":
    main()
