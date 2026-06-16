"""Generador unificado de configuraciones para Lab 3.3.2.

Crea archivos .cfg en configs/ para:
  - Switches capa 2 (SWA, SWB, SWC, SWD) con PACL/VACL
  - Routers R1, R2, R3 (base + OSPF + DHCP relay)
  - VPN Site-to-Site R2/R3 (GRE sobre IPsec)
  - BGP (R1, R2, R3, ISP, BR) IPv4/IPv6 con redistribución
  - Configs base para ISP y BR (interfaces + loopbacks)
"""

from pathlib import Path

OUT_DIR = Path(r"C:\Users\lukas\Downloads\CCNPlabs\configs")
OUT_DIR.mkdir(exist_ok=True)

# -----------------------------------------------------------------------------
# Datos comunes
# -----------------------------------------------------------------------------
VLANS = {
    21: {"name": "FINANZAS", "v4": "10.0.21.0/24", "v6": "3001:ABCD:ABCD:A::/64"},
    22: {"name": "GESTION", "v4": "10.0.31.0/24", "v6": "3001:ABCD:ABCD:B::/64"},
    23: {"name": "FUERZA-VENTAS", "v4": "10.0.41.0/24", "v6": "3001:ABCD:ABCD:C::/64"},
    24: {"name": "RRHH", "v4": "10.0.51.0/24", "v6": "3001:ABCD:ABCD:D::/64"},
    25: {"name": "ADM", "v4": "10.0.61.0/24", "v6": "3001:ABCD:ABCD:E::/64"},
}


def host_ip(prefix_with_len, host):
    """Devuelve dirección IP con host dado conservando máscara."""
    prefix = prefix_with_len.split("/")[0]
    mask = prefix_with_len.split("/")[1]
    octets = prefix.split(".")
    if len(octets) == 4:
        octets[-1] = str(host)
        return "/".join([".".join(octets), mask])
    return prefix


def ipv6_host(prefix, host):
    """Reemplaza el último segmento ::/64 por ::host/64, etc."""
    base = prefix.replace("::/64", "")
    return f"{base}::{host}/64"


def third_octet(v4_net):
    return v4_net.split(".")[2]


# -----------------------------------------------------------------------------
# 1. Switches capa 2 con PACL y VACL
# -----------------------------------------------------------------------------
SWITCH_DATA = {
    "SWA": {
        "trunk_to_router": "E0/3",
        "portchannels": {
            6: {"mode": "active", "members": ["E1/0", "E1/1"]},
            5: {"mode": "on", "members": ["E1/2", "E1/3"]},
            4: {"mode": "desirable", "members": ["E0/0", "E0/1"]},
        },
        "access_ports": [],
    },
    "SWB": {
        "trunk_to_router": "E0/3",
        "portchannels": {
            6: {"mode": "active", "members": ["E1/0", "E1/1"]},
            2: {"mode": "active", "members": ["E0/0", "E0/1"]},
            3: {"mode": "on", "members": ["E1/2", "E1/3"]},
        },
        "access_ports": [],
    },
    "SWC": {
        "trunk_to_router": None,
        "portchannels": {
            5: {"mode": "on", "members": ["E1/2", "E1/3"]},
            2: {"mode": "active", "members": ["E0/0", "E0/1"]},
            1: {"mode": "desirable", "members": ["E1/0", "E1/1"]},
        },
        "access_ports": [
            {"intf": "E0/2", "vlan": 21},
            {"intf": "E0/3", "vlan": 22},
        ],
    },
    "SWD": {
        "trunk_to_router": None,
        "portchannels": {
            4: {"mode": "desirable", "members": ["E0/0", "E0/1"]},
            3: {"mode": "on", "members": ["E1/2", "E1/3"]},
            1: {"mode": "desirable", "members": ["E1/0", "E1/1"]},
        },
        "access_ports": [
            {"intf": "E0/2", "vlan": 23},
            {"intf": "E0/3", "vlan": 24},
        ],
    },
}


def switch_config(name, data):
    lines = [
        f"hostname {name}",
        "!",
        "no ip domain-lookup",
        "!",
        "spanning-tree mode rapid-pvst",
        "spanning-tree extend system-id",
        "!",
    ]

    for vid, vdata in VLANS.items():
        lines.append(f"vlan {vid}")
        lines.append(f" name {vdata['name']}")
    lines.append("!")

    # PACL IPv4 e IPv6: VLAN21 <-> VLAN22 en puertos de acceso de SWC
    if name == "SWC":
        lines.extend([
            "ip access-list extended PACL_BLOCK_21_22",
            " deny ip 10.0.21.0 0.0.0.255 10.0.31.0 0.0.0.255",
            " deny ip 10.0.31.0 0.0.0.255 10.0.21.0 0.0.0.255",
            " permit ip any any",
            "!",
            "ipv6 access-list PACL6_BLOCK_21_22",
            " deny ipv6 3001:ABCD:ABCD:A::/64 3001:ABCD:ABCD:B::/64",
            " deny ipv6 3001:ABCD:ABCD:B::/64 3001:ABCD:ABCD:A::/64",
            " permit ipv6 any any",
            "!",
        ])

    # VACL: VLAN23 <-> VLAN24 (en todos los switches que transportan esas VLANs)
    lines.extend([
        "ip access-list extended VACL_BLOCK_23_24",
        " deny ip 10.0.41.0 0.0.0.255 10.0.51.0 0.0.0.255",
        " deny ip 10.0.51.0 0.0.0.255 10.0.41.0 0.0.0.255",
        " permit ip any any",
        "!",
        "vlan access-map VACL_BLOCK_23_24 10",
        " match ip address VACL_BLOCK_23_24",
        " action drop",
        "!",
        "vlan access-map VACL_BLOCK_23_24 20",
        " action forward",
        "!",
        "vlan filter VACL_BLOCK_23_24 vlan-list 23,24",
        "!",
    ])

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
        ])
        # Aplicar PACL inbound en puertos de acceso de VLAN21 y VLAN22
        if name == "SWC":
            lines.append(" ip access-group PACL_BLOCK_21_22 in")
            lines.append(" ipv6 traffic-filter PACL6_BLOCK_21_22 in")
        lines.append("!")

    if data["trunk_to_router"]:
        lines.extend([
            f"interface {data['trunk_to_router']}",
            " switchport trunk encapsulation dot1q",
            " switchport mode trunk",
            " switchport trunk allowed vlan 21-25",
            " spanning-tree guard root",
            "!",
        ])

    for po_id, po in data["portchannels"].items():
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
        lines.extend([
            f"interface Port-channel {po_id}",
            " switchport trunk encapsulation dot1q",
            " switchport mode trunk",
            " switchport trunk allowed vlan 21-25",
            "!",
        ])

    lines.append("end")
    return "\n".join(lines)


def generate_switch_configs():
    for name, data in SWITCH_DATA.items():
        cfg = switch_config(name, data)
        (OUT_DIR / f"{name.lower()}_layer2.cfg").write_text(cfg, encoding="utf-8")
        print(f"Generated {name.lower()}_layer2.cfg")


# -----------------------------------------------------------------------------
# 2. Config base R1 (DHCP + OSPF + interfaces WAN)
# -----------------------------------------------------------------------------
def r1_base_config():
    lines = [
        "hostname R1",
        "!",
        "no ip domain-lookup",
        "!",
        "ipv6 unicast-routing",
        "ipv6 cef",
        "!",
        "interface Loopback1",
        " ip address 1.1.1.1 255.255.255.255",
        " ipv6 address 3001:ABCD:ABCD:1::1/128",
        " ip ospf 1 area 0",
        " ipv6 ospf 1 area 0",
        "!",
        "interface Ethernet0/1",
        " ip address 192.168.12.1 255.255.255.0",
        " ipv6 address 3001:ABCD:ABCD:12::1/64",
        " ip ospf 1 area 0",
        " ipv6 ospf 1 area 0",
        " no shutdown",
        "!",
        "interface Ethernet0/2",
        " ip address 192.168.13.1 255.255.255.0",
        " ipv6 address 3001:ABCD:ABCD:13::1/64",
        " ip ospf 1 area 0",
        " ipv6 ospf 1 area 0",
        " no shutdown",
        "!",
        "interface Ethernet0/3",
        " ip address 209.50.0.1 255.255.255.252",
        " ipv6 address 3001:ABCD:ABCD:209::1/112",
        " no shutdown",
        "!",
    ]

    # DHCPv4 pools
    for vid, data in VLANS.items():
        v4_net = data["v4"]
        gateway = v4_net.replace("0/24", "254")
        lines.extend([
            f"ip dhcp pool VLAN{vid}",
            f" network {v4_net.split('/')[0]} 255.255.255.0",
            f" default-router {gateway}",
            " dns-server 8.8.8.8",
            " domain-name ary5112.lab",
            "!",
        ])
    # Excluir gateway y routers reales
    lines.extend([
        "ip dhcp excluded-address 10.0.21.252 10.0.21.254",
        "ip dhcp excluded-address 10.0.31.252 10.0.31.254",
        "ip dhcp excluded-address 10.0.41.252 10.0.41.254",
        "ip dhcp excluded-address 10.0.51.252 10.0.51.254",
        "ip dhcp excluded-address 10.0.61.252 10.0.61.254",
        "!",
    ])

    # DHCPv6 pools
    for vid, data in VLANS.items():
        v6_prefix = data["v6"]
        lines.extend([
            f"ipv6 dhcp pool VLAN{vid}",
            f" address prefix {v6_prefix}",
            " dns-server 3001:ABCD:ABCD:8:8::8",
            " domain-name ary5112.lab",
            "!",
        ])

    lines.extend([
        "router ospf 1",
        " router-id 1.1.1.1",
        " network 1.1.1.1 0.0.0.0 area 0",
        " network 192.168.12.0 0.0.0.255 area 0",
        " network 192.168.13.0 0.0.0.255 area 0",
        "!",
        "ipv6 router ospf 1",
        " router-id 1.1.1.1",
        "!",
    ])

    lines.append("end")
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# 3. Config base R2 y R3 (subinterfaces, FHRP, OSPF, DHCP relay)
# -----------------------------------------------------------------------------
def router_base_config(name, trunk_intf, area0_intf, area0_link_v4, active_vlans):
    rid = "2.2.2.2" if name == "R2" else "3.3.3.3"
    loop_num = 2 if name == "R2" else 3
    area0_intf_other = "Ethernet0/1" if name == "R2" else "Ethernet0/2"
    # 192.168.12.0 -> 3001:ABCD:ABCD:12::/64 ; 192.168.13.0 -> 3001:ABCD:ABCD:13::/64
    area0_v6_prefix = area0_link_v4.replace("192.168.", "3001:ABCD:ABCD:").replace(".0", "::/64")

    lines = [
        f"hostname {name}",
        "!",
        "no ip domain-lookup",
        "!",
        "ipv6 unicast-routing",
        "ipv6 cef",
        "!",
        "! VACL no bloquea trafico inter-VLAN en switches L2; se refuerza en router",
        "ip access-list extended ACL_BLOCK_23_24",
        " deny ip 10.0.41.0 0.0.0.255 10.0.51.0 0.0.0.255",
        " deny ip 10.0.51.0 0.0.0.255 10.0.41.0 0.0.0.255",
        " permit ip any any",
        "!",
        "ipv6 access-list ACL6_BLOCK_23_24",
        " deny ipv6 3001:ABCD:ABCD:C::/64 3001:ABCD:ABCD:D::/64",
        " deny ipv6 3001:ABCD:ABCD:D::/64 3001:ABCD:ABCD:C::/64",
        " permit ipv6 any any",
        "!",
        f"interface Loopback{loop_num}",
        f" ip address {rid} 255.255.255.255",
        f" ipv6 address 3001:ABCD:ABCD:{loop_num}::{loop_num}/128",
        " ip ospf 1 area 0",
        " ipv6 ospf 1 area 0",
        "!",
        f"interface {area0_intf_other}",
        f" ip address {area0_link_v4.split('/')[0].replace('.0', '.')}{loop_num} 255.255.255.0",
        f" ipv6 address {area0_v6_prefix.replace('::/64', '::' + str(loop_num) + '/64')}",
        " ip ospf 1 area 0",
        " ipv6 ospf 1 area 0",
        " no shutdown",
        "!",
        f"interface {trunk_intf}",
        " no ip address",
        " no shutdown",
        "!",
    ]

    for vid, data in VLANS.items():
        v4_net = data["v4"]
        v6_net = data["v6"]
        real_host = "252" if name == "R2" else "253"
        gateway_v4 = v4_net.replace("0/24", "254")
        gateway_v6 = v6_net.replace("::/64", "::FF")
        priority = 110 if vid in active_vlans else 100

        lines.extend([
            f"interface {trunk_intf}.{vid}",
            f" encapsulation dot1Q {vid}",
            f" ip address 10.0.{third_octet(v4_net)}.{real_host} 255.255.255.0",
            f" ipv6 address {v6_net.replace('::/64', '::' + real_host + '/64')}",
            " standby version 2",
            f" standby {vid} ip {gateway_v4}",
            f" standby {vid} priority {priority}",
            f" standby {vid} preempt",
            f" standby {vid} ipv6 {gateway_v6}",
            " ip ospf 1 area 100",
            " ipv6 ospf 1 area 100",
            " ipv6 nd managed-config-flag",
            " ipv6 nd other-config-flag",
            " ip helper-address 1.1.1.1",
            " ipv6 dhcp relay destination 3001:ABCD:ABCD:1::1",
        ])
        if vid in (23, 24):
            lines.extend([
                " ip access-group ACL_BLOCK_23_24 in",
                " ipv6 traffic-filter ACL6_BLOCK_23_24 in",
            ])
        lines.append("!")

    lines.extend([
        "router ospf 1",
        f" router-id {rid}",
        " passive-interface default",
        f" no passive-interface {area0_intf_other}",
        " no passive-interface Tunnel0",
        f" network {rid} 0.0.0.0 area 0",
        f" network {area0_link_v4} 0.0.0.255 area 0",
        " area 100 range 10.0.0.0 255.248.0.0",
    ])
    for vid, data in VLANS.items():
        lines.append(f" network 10.0.{third_octet(data['v4'])}.0 0.0.0.255 area 100")
    lines.append("!")

    lines.extend([
        "ipv6 router ospf 1",
        f" router-id {rid}",
        " area 100 range 3001:ABCD:ABCD::/48",
        "!",
    ])

    lines.append("end")
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# 4. VPN Site-to-Site R2/R3 (GRE p2p sobre IPsec)
# -----------------------------------------------------------------------------
VPN_COMMON = """!
crypto isakmp policy 10
 encr aes 256
 authentication pre-share
 group 14
 hash sha256
!
crypto isakmp key cisco address 0.0.0.0
!
crypto ipsec transform-set VPN-TS esp-aes 256 esp-sha-hmac
 mode transport
!
crypto ipsec profile VPN-PROFILE
 set transform-set VPN-TS
!"""


def vpn_config(name, local_loop, remote_loop, local_tunnel_ip, remote_tunnel_ip_v4):
    # local_tunnel_ip es el IP del túnel; para IPv6 usamos ::1/::2 según nombre
    v6_host = "1" if name == "R2" else "2"
    return f"""hostname {name}
!
no ip domain-lookup
!
ipv6 unicast-routing
ipv6 cef
{VPN_COMMON}
!
interface Tunnel0
 ip address {local_tunnel_ip} 255.255.255.252
 ipv6 address 3001:ABCD:ABCD:100::{v6_host}/64
 tunnel source Loopback{local_loop}
 tunnel destination {remote_loop}
 tunnel mode gre ip
 tunnel protection ipsec profile VPN-PROFILE
 ip ospf 1 area 100
 ipv6 ospf 1 area 100
!
end
"""


# -----------------------------------------------------------------------------
# 5. BGP
# -----------------------------------------------------------------------------
def r1_bgp_config():
    return """hostname R1
!
no ip domain-lookup
!
ipv6 unicast-routing
ipv6 cef
!
router bgp 100
 bgp router-id 1.1.1.1
 bgp log-neighbor-changes
 no bgp default ipv4-unicast
 neighbor 2.2.2.2 remote-as 100
 neighbor 2.2.2.2 update-source Loopback1
 neighbor 2.2.2.2 next-hop-self
 neighbor 3.3.3.3 remote-as 100
 neighbor 3.3.3.3 update-source Loopback1
 neighbor 3.3.3.3 next-hop-self
 neighbor 209.50.0.2 remote-as 200
 !
 address-family ipv4
  network 1.1.1.1 mask 255.255.255.255
  network 192.168.12.0 mask 255.255.255.0
  network 192.168.13.0 mask 255.255.255.0
  network 209.50.0.0 mask 255.255.255.252
  redistribute ospf 1 match internal external 1 external 2
  neighbor 2.2.2.2 activate
  neighbor 3.3.3.3 activate
  neighbor 209.50.0.2 activate
 exit-address-family
 !
 address-family ipv6
  network 3001:ABCD:ABCD:1::1/128
  network 3001:ABCD:ABCD:12::/64
  network 3001:ABCD:ABCD:13::/64
  network 3001:ABCD:ABCD:209::/112
  redistribute ospf 1 include-connected
  neighbor 2.2.2.2 activate
  neighbor 3.3.3.3 activate
  neighbor 209.50.0.2 activate
 exit-address-family
!
router ospf 1
 redistribute bgp 100 subnets
!
ipv6 router ospf 1
 redistribute bgp 100
!
end
"""


def r2_bgp_config():
    return """hostname R2
!
no ip domain-lookup
!
ipv6 unicast-routing
ipv6 cef
!
router bgp 100
 bgp router-id 2.2.2.2
 bgp log-neighbor-changes
 no bgp default ipv4-unicast
 neighbor 1.1.1.1 remote-as 100
 neighbor 1.1.1.1 update-source Loopback2
 neighbor 1.1.1.1 next-hop-self
 neighbor 3.3.3.3 remote-as 100
 neighbor 3.3.3.3 update-source Loopback2
 neighbor 3.3.3.3 next-hop-self
 !
 address-family ipv4
  network 2.2.2.2 mask 255.255.255.255
  network 10.0.21.0 mask 255.255.255.0
  network 10.0.31.0 mask 255.255.255.0
  network 10.0.41.0 mask 255.255.255.0
  network 10.0.51.0 mask 255.255.255.0
  network 10.0.61.0 mask 255.255.255.0
  network 192.168.12.0 mask 255.255.255.0
  network 10.100.100.0 mask 255.255.255.252
  redistribute ospf 1 match internal external 1 external 2
  neighbor 1.1.1.1 activate
  neighbor 3.3.3.3 activate
 exit-address-family
 !
 address-family ipv6
  network 3001:ABCD:ABCD:2::2/128
  network 3001:ABCD:ABCD:A::/64
  network 3001:ABCD:ABCD:B::/64
  network 3001:ABCD:ABCD:C::/64
  network 3001:ABCD:ABCD:D::/64
  network 3001:ABCD:ABCD:E::/64
  network 3001:ABCD:ABCD:12::/64
  network 3001:ABCD:ABCD:100::/64
  redistribute ospf 1 include-connected
  neighbor 1.1.1.1 activate
  neighbor 3.3.3.3 activate
 exit-address-family
!
router ospf 1
 redistribute bgp 100 subnets
!
ipv6 router ospf 1
 redistribute bgp 100
!
end
"""


def r3_bgp_config():
    return """hostname R3
!
no ip domain-lookup
!
ipv6 unicast-routing
ipv6 cef
!
router bgp 100
 bgp router-id 3.3.3.3
 bgp log-neighbor-changes
 no bgp default ipv4-unicast
 neighbor 1.1.1.1 remote-as 100
 neighbor 1.1.1.1 update-source Loopback3
 neighbor 1.1.1.1 next-hop-self
 neighbor 2.2.2.2 remote-as 100
 neighbor 2.2.2.2 update-source Loopback3
 neighbor 2.2.2.2 next-hop-self
 !
 address-family ipv4
  network 3.3.3.3 mask 255.255.255.255
  network 10.0.21.0 mask 255.255.255.0
  network 10.0.31.0 mask 255.255.255.0
  network 10.0.41.0 mask 255.255.255.0
  network 10.0.51.0 mask 255.255.255.0
  network 10.0.61.0 mask 255.255.255.0
  network 192.168.13.0 mask 255.255.255.0
  network 10.100.100.0 mask 255.255.255.252
  redistribute ospf 1 match internal external 1 external 2
  neighbor 1.1.1.1 activate
  neighbor 2.2.2.2 activate
 exit-address-family
 !
 address-family ipv6
  network 3001:ABCD:ABCD:3::3/128
  network 3001:ABCD:ABCD:A::/64
  network 3001:ABCD:ABCD:B::/64
  network 3001:ABCD:ABCD:C::/64
  network 3001:ABCD:ABCD:D::/64
  network 3001:ABCD:ABCD:E::/64
  network 3001:ABCD:ABCD:13::/64
  network 3001:ABCD:ABCD:100::/64
  redistribute ospf 1 include-connected
  neighbor 1.1.1.1 activate
  neighbor 2.2.2.2 activate
 exit-address-family
!
router ospf 1
 redistribute bgp 100 subnets
!
ipv6 router ospf 1
 redistribute bgp 100
!
end
"""


def isp_config():
    return """hostname ISP
!
no ip domain-lookup
!
ipv6 unicast-routing
ipv6 cef
!
interface Loopback0
 ip address 8.8.8.8 255.255.255.255
 ipv6 address 3001:ABCD:ABCD:8:8::8/128
!
interface Ethernet0/2
 ip address 220.50.0.2 255.255.255.252
 ipv6 address 3001:ABCD:ABCD:220::2/112
 no shutdown
!
interface Ethernet0/3
 ip address 209.50.0.2 255.255.255.252
 ipv6 address 3001:ABCD:ABCD:209::2/112
 no shutdown
!
router bgp 200
 bgp router-id 8.8.8.8
 bgp log-neighbor-changes
 no bgp default ipv4-unicast
 neighbor 209.50.0.1 remote-as 100
 neighbor 220.50.0.1 remote-as 300
 !
 address-family ipv4
  network 8.8.8.8 mask 255.255.255.255
  network 209.50.0.0 mask 255.255.255.252
  network 220.50.0.0 mask 255.255.255.252
  neighbor 209.50.0.1 activate
  neighbor 220.50.0.1 activate
 exit-address-family
 !
 address-family ipv6
  network 3001:ABCD:ABCD:8:8::8/128
  network 3001:ABCD:ABCD:209::/112
  network 3001:ABCD:ABCD:220::/112
  neighbor 209.50.0.1 activate
  neighbor 220.50.0.1 activate
 exit-address-family
!
end
"""


def br_config():
    return """hostname BR
!
no ip domain-lookup
!
ipv6 unicast-routing
ipv6 cef
!
interface Loopback0
 ip address 192.168.100.1 255.255.255.255
 ipv6 address 3001:ABCD:ABCD:100::1/128
!
interface Ethernet0/2
 ip address 220.50.0.1 255.255.255.252
 ipv6 address 3001:ABCD:ABCD:220::1/112
 no shutdown
!
route-map PREPEND-IPv4 permit 10
 set as-path prepend 200
!
route-map PREPEND-IPv6 permit 10
 set as-path prepend 200 200
!
router bgp 300
 bgp router-id 192.168.100.1
 bgp log-neighbor-changes
 no bgp default ipv4-unicast
 neighbor 220.50.0.2 remote-as 200
 !
 address-family ipv4
  network 192.168.100.1 mask 255.255.255.255
  network 220.50.0.0 mask 255.255.255.252
  neighbor 220.50.0.2 activate
  neighbor 220.50.0.2 route-map PREPEND-IPv4 out
 exit-address-family
 !
 address-family ipv6
  network 3001:ABCD:ABCD:100::1/128
  network 3001:ABCD:ABCD:220::/112
  neighbor 220.50.0.2 activate
  neighbor 220.50.0.2 route-map PREPEND-IPv6 out
 exit-address-family
!
end
"""


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    generate_switch_configs()

    (OUT_DIR / "r1_base.cfg").write_text(r1_base_config(), encoding="utf-8")
    print("Generated r1_base.cfg")

    r2_base = router_base_config(
        "R2", "Ethernet0/3", "Ethernet0/1", "192.168.12.0", [21, 22]
    )
    (OUT_DIR / "r2_base.cfg").write_text(r2_base, encoding="utf-8")
    print("Generated r2_base.cfg")

    r3_base = router_base_config(
        "R3", "Ethernet0/3", "Ethernet0/2", "192.168.13.0", [23, 24, 25]
    )
    (OUT_DIR / "r3_base.cfg").write_text(r3_base, encoding="utf-8")
    print("Generated r3_base.cfg")

    r2_vpn = vpn_config("R2", 2, "3.3.3.3", "10.100.100.1", "10.100.100.2")
    r3_vpn = vpn_config("R3", 3, "2.2.2.2", "10.100.100.2", "10.100.100.1")
    (OUT_DIR / "r2_vpn.cfg").write_text(r2_vpn, encoding="utf-8")
    (OUT_DIR / "r3_vpn.cfg").write_text(r3_vpn, encoding="utf-8")
    print("Generated r2_vpn.cfg and r3_vpn.cfg")

    (OUT_DIR / "r1_bgp.cfg").write_text(r1_bgp_config(), encoding="utf-8")
    (OUT_DIR / "r2_bgp.cfg").write_text(r2_bgp_config(), encoding="utf-8")
    (OUT_DIR / "r3_bgp.cfg").write_text(r3_bgp_config(), encoding="utf-8")
    (OUT_DIR / "isp.cfg").write_text(isp_config(), encoding="utf-8")
    (OUT_DIR / "br.cfg").write_text(br_config(), encoding="utf-8")
    print("Generated r1_bgp.cfg, r2_bgp.cfg, r3_bgp.cfg, isp.cfg, br.cfg")


if __name__ == "__main__":
    main()
