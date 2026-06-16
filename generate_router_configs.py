"""Generate router configurations for R2 and R3 (subinterfaces, FHRP, OSPF)."""

from pathlib import Path

OUT_DIR = Path(r"C:\Users\lukas\Downloads\CCNPlabs\configs")
OUT_DIR.mkdir(exist_ok=True)

VLANS = {
    21: {"name": "FINANZAS", "v4": "10.0.21.0/24", "v6": "3001:ABCD:ABCD:A::/64"},
    22: {"name": "GESTION", "v4": "10.0.31.0/24", "v6": "3001:ABCD:ABCD:B::/64"},
    23: {"name": "FUERZA-VENTAS", "v4": "10.0.41.0/24", "v6": "3001:ABCD:ABCD:C::/64"},
    24: {"name": "RRHH", "v4": "10.0.51.0/24", "v6": "3001:ABCD:ABCD:D::/64"},
    25: {"name": "ADM", "v4": "10.0.61.0/24", "v6": "3001:ABCD:ABCD:E::/64"},
}


def last_octet(ip_with_prefix):
    return ip_with_prefix.split("/")[0].split(".")[-1]


def router_config(name, trunk_intf, ospf_area0_link, ospf_area0_intf, active_vlans, standby_vlans):
    rid = "2.2.2.2" if name == "R2" else "3.3.3.3"
    loop_num = 2 if name == "R2" else 3
    loop_v6 = f"3001:ABCD:ABCD:{loop_num}::{loop_num}/128"

    lines = [
        "ipv6 unicast-routing",
        "ipv6 cef",
        "!",
        f"interface Loopback{loop_num}",
        f" ipv6 address {loop_v6}",
        " ipv6 ospf 1 area 0",
        "!",
    ]

    # Map short to full interface names for consistency
    def full_name(short):
        return short.replace("E", "Ethernet")

    trunk_intf = full_name(trunk_intf)
    ospf_area0_intf = full_name(ospf_area0_intf)

    # Physical trunk to switch
    lines.extend([
        f"interface {trunk_intf}",
        " no ip address",
        " no shutdown",
        "!",
    ])

    # Subinterfaces + FHRP
    for vid, data in VLANS.items():
        v4_net = data["v4"]
        v6_net = data["v6"]
        third_octet = v4_net.split(".")[2]
        real_v4_host = "252" if name == "R2" else "253"
        real_v6_host = "252" if name == "R2" else "253"
        vip_v4 = v4_net.replace("0/24", "254")
        vip_v6 = v6_net.replace("::/64", "::FF")

        priority = 110 if vid in active_vlans else 100

        lines.extend([
            f"interface {trunk_intf}.{vid}",
            f" encapsulation dot1Q {vid}",
            f" ip address 10.0.{third_octet}.{real_v4_host} 255.255.255.0",
            f" ipv6 address {v6_net.replace('::/64', '::' + real_v6_host + '/64')}",
            " standby version 2",
            f" standby {vid} ip {vip_v4.split('/')[0]}",
            f" standby {vid} priority {priority}",
            f" standby {vid} preempt",
            f" standby {vid} ipv6 {vip_v6.split('/')[0]}",
            " ip ospf 1 area 100",
            " ip ospf 1 passive",
            " ipv6 ospf 1 area 100",
            "!",
        ])

    # OSPFv2
    lines.extend([
        "router ospf 1",
        f" router-id {rid}",
        " passive-interface default",
        f" no passive-interface {ospf_area0_intf}",
        " no passive-interface Tunnel0",
        f" network {ospf_area0_link} 0.0.0.255 area 0",
        f" network {rid} 0.0.0.0 area 0",
        " area 100 range 10.0.0.0 255.248.0.0",
    ])
    for vid, data in VLANS.items():
        third_octet = data["v4"].split(".")[2]
        lines.append(f" network 10.0.{third_octet}.0 0.0.0.255 area 100")
    lines.append("!")

    # OSPFv3
    lines.extend([
        "ipv6 router ospf 1",
        f" router-id {rid}",
        " area 100 range 3001:ABCD:ABCD::/48",
        "!",
        f"interface Loopback{loop_num}",
        " ipv6 ospf 1 area 0",
        "!",
        f"interface {ospf_area0_intf}",
        " ipv6 ospf 1 area 0",
        "!",
        "interface Tunnel0",
        " ipv6 ospf 1 area 100",
        "!",
    ])

    # OSPFv2
    rid = "2.2.2.2" if name == "R2" else "3.3.3.3"
    lines.extend([
        "router ospf 1",
        f" router-id {rid}",
        f" network {ospf_area0_link} 0.0.0.255 area 0",
        f" network {rid} 0.0.0.0 area 0",
        " area 100 range 10.0.0.0 255.248.0.0",
    ])
    for vid, data in VLANS.items():
        third_octet = data["v4"].split(".")[2]
        lines.append(f" network 10.0.{third_octet}.0 0.0.0.255 area 100")
    lines.append("!")

    # OSPFv3
    lines.extend([
        "ipv6 router ospf 1",
        f" router-id {rid}",
        " area 100 range 3001:ABCD:ABCD::/48",
        "!",
        f"interface Loopback{2 if name == 'R2' else 3}",
        " ipv6 ospf 1 area 0",
        "!",
        f"interface {ospf_area0_intf}",
        " ipv6 ospf 1 area 0",
        "!",
    ])

    lines.append("end")
    return "\n".join(lines)


def main():
    r2 = router_config(
        "R2",
        trunk_intf="E0/3",
        ospf_area0_link="192.168.12.0",
        ospf_area0_intf="E0/1",
        active_vlans=[21, 22],
        standby_vlans=[23, 24, 25],
    )
    (OUT_DIR / "r2_router.cfg").write_text(r2, encoding="utf-8")

    r3 = router_config(
        "R3",
        trunk_intf="E0/3",
        ospf_area0_link="192.168.13.0",
        ospf_area0_intf="E0/2",
        active_vlans=[23, 24, 25],
        standby_vlans=[21, 22],
    )
    (OUT_DIR / "r3_router.cfg").write_text(r3, encoding="utf-8")

    print("Generated r2_router.cfg and r3_router.cfg")


if __name__ == "__main__":
    main()
