#!/usr/bin/env python3
"""
generate_router_configs.py — Lab 16 (Aplicación de Red Corporativa Enterprise)

Genera configuraciones para los routers del laboratorio:
  - BR  (AS 65500, eBGP con ISP, loopback 8.8.8.8 / 2021:ACAD:ACAD:8::8/128)
  - ISP (AS 100, eBGP tránsito con BR y RB)
  - RB  (AS 200, eBGP con ISP, EIGRP AS 123 con RA, túnel GRE 6over4 hacia BR)
  - RA  (OSPF Área 0 con MLS1/MLS2, EIGRP AS 123 con RB, DHCP server)

Alcance: direcciones IP (IPv4/IPv6) + túnel GRE 6over4 (IPv6 sobre IPv4).
Los pendientes (switching, HSRP, port-security, redistribuciones, IP SLA, etc.)
se dejan fuera hasta una iteración posterior.
"""

import os
from textwrap import dedent

OUT_DIR = os.path.join(os.path.dirname(__file__), "configs")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Direccionamiento (extraído del PDF/imagen topología)
# ---------------------------------------------------------------------------
# Subred IPv6 del túnel (punto-a-punto entre RB y BR, sobre transporte IPv4)
TUNNEL_V6_BR = "2021:ACAD:ACAD:200::1/64"   # BR  - lado túnel
TUNNEL_V6_RB = "2021:ACAD:ACAD:200::2/64"   # RB  - lado túnel

# Loopback IPv6 de BR (anunciada en BGP y participante en EIGRPv6)
BR_LOOPBACK_V6 = "2021:ACAD:ACAD:8:8::8/128"

# ---------------------------------------------------------------------------
# BR — AS 65500
# ---------------------------------------------------------------------------
br = f"""\
! ============================================================
! BR - Router Borde (BGP AS 65500)
! ============================================================
! --- Desactivar DNS lookup (importante en IOL: evita "Translating end..."
!     cuando se ejecuta 'end' / 'q' y similares) ---
no ip domain-lookup
hostname BR
!
! --- Habilitar IPv6 unicast routing ANTES de cualquier config IPv6 ---
ipv6 unicast-routing
!
! --- Loopback0 (prefijo anunciado en BGP y participante en EIGRPv6) ---
interface Loopback0
 description BR-Loopback-BGP-y-EIGRPv6
 ip address 8.8.8.8 255.255.255.255
 ipv6 address {BR_LOOPBACK_V6}
!
! --- Enlace fisico a ISP (eBGP IPv4) ---
interface Ethernet0/2
 description BR-to-ISP
 ip address 220.50.0.1 255.255.255.252
 no shutdown
!
! --- Tunel GRE IPv6 sobre IPv4 hacia RB ---
!     Transport source : E0/2 (220.50.0.1)
!     Transport dest   : 219.50.0.1  (RB E0/1)
interface Tunnel0
 description GRE 6over4 to RB
 ipv6 address {TUNNEL_V6_BR}
 ipv6 eigrp 123
 tunnel source Ethernet0/2
 tunnel destination 219.50.0.1
 tunnel mode gre ip
!
! --- BGP con ISP (anuncia 8.8.8.8/32 y la loopback IPv6) ---
router bgp 65500
 bgp router-id 8.8.8.8
 neighbor 220.50.0.2 remote-as 100
 neighbor 220.50.0.2 description ISP
 network 8.8.8.8 mask 255.255.255.255
!
! --- EIGRPv6 (unico peer: RB via Tunnel0) ---
ipv6 router eigrp 123
 eigrp router-id 8.8.8.8
 passive-interface default
 no passive-interface Tunnel0
!
end
"""

# ---------------------------------------------------------------------------
# ISP — AS 100 (tránsito IPv4)
# ---------------------------------------------------------------------------
isp = """\
! ============================================================
! ISP - Proveedor (BGP AS 100)
! ============================================================
! --- Desactivar DNS lookup ---
no ip domain-lookup
hostname ISP
!
interface Loopback0
 description ISP-Loopback
 ip address 100.100.100.100 255.255.255.255
!
! --- Enlace a BR ---
interface Ethernet0/2
 description ISP-to-BR
 ip address 220.50.0.2 255.255.255.252
 no shutdown
!
! --- Enlace a RB ---
interface Ethernet0/1
 description ISP-to-RB
 ip address 219.50.0.2 255.255.255.252
 no shutdown
!
! --- BGP transito BR (AS 65500) <-> RB (AS 200) ---
router bgp 100
 bgp router-id 100.100.100.100
 neighbor 220.50.0.1 remote-as 65500
 neighbor 220.50.0.1 description BR
 neighbor 219.50.0.1 remote-as 200
 neighbor 219.50.0.1 description RB
!
end
"""

# ---------------------------------------------------------------------------
# RB — AS 200, EIGRP 123 con RA, túnel GRE 6over4 hacia BR
# ---------------------------------------------------------------------------
rb = f"""\
! ============================================================
! RB - Borde con EIGRP (BGP AS 200, EIGRP AS 123)
! ============================================================
! --- Desactivar DNS lookup ---
no ip domain-lookup
hostname RB
!
! --- Habilitar IPv6 unicast routing ANTES de cualquier config IPv6 ---
ipv6 unicast-routing
!
! --- Loopback0 (router-id EIGRPv6 y BGP) ---
interface Loopback0
 description RB-Loopback
 ip address 2.2.2.2 255.255.255.255
 ipv6 address 2021:ACAD:ACAD:200::2/64
!
! --- Enlace a RA (EIGRPv6 + IPv4) ---
interface Ethernet0/0
 description RB-to-RA
 ip address 172.16.100.2 255.255.255.0
 ipv6 address 2021:ACAD:ACAD:100::2/64
 ipv6 eigrp 123
 no shutdown
!
! --- Enlace a ISP (eBGP IPv4) ---
interface Ethernet0/1
 description RB-to-ISP
 ip address 219.50.0.1 255.255.255.252
 no shutdown
!
! --- Tunel GRE 6over4 hacia BR ---
!     Transport source : E0/1 (219.50.0.1)
!     Transport dest   : 220.50.0.1  (BR E0/2)
interface Tunnel0
 description GRE 6over4 to BR
 ipv6 address {TUNNEL_V6_RB}
 ipv6 eigrp 123
 tunnel source Ethernet0/1
 tunnel destination 220.50.0.1
 tunnel mode gre ip
!
! --- BGP con ISP (AS 100) ---
router bgp 200
 bgp router-id 2.2.2.2
 neighbor 219.50.0.2 remote-as 100
 neighbor 219.50.0.2 description ISP
 network 172.16.100.0 mask 255.255.255.0
!
! --- EIGRPv6 (peers: RA E0/0 y BR via Tunnel0) ---
ipv6 router eigrp 123
 eigrp router-id 2.2.2.2
 passive-interface default
 no passive-interface Ethernet0/0
 no passive-interface Tunnel0
!
end
"""

# ---------------------------------------------------------------------------
# RA — OSPFv2/v3 con MLS1/MLS2, EIGRPv6 con RB, DHCP server
# ---------------------------------------------------------------------------
ra = """\
! ============================================================
! RA - Enrutamiento + DHCP server
!   - OSPF Area 0 con MLS1 y MLS2
!   - EIGRP AS 123 con RB (E0/0)
!   - DHCPv4 server para VLANs 10/20/30/40 (excluye las 5 primeras)
! ============================================================
! --- Desactivar DNS lookup ---
no ip domain-lookup
hostname RA
!
! --- Habilitar IPv6 unicast routing ANTES de cualquier config IPv6 ---
ipv6 unicast-routing
!
! --- Loopback0 ---
interface Loopback0
 description RA-Loopback
 ip address 1.1.1.1 255.255.255.255
!
! --- Enlace a RB (EIGRPv6 + IPv4) ---
interface Ethernet0/0
 description RA-to-RB
 ip address 172.16.100.1 255.255.255.0
 ipv6 address 2021:ACAD:ACAD:100::1/64
 ipv6 eigrp 123
 no shutdown
!
! --- Enlace a MLS1 (OSPF) ---
interface Ethernet0/3
 description RA-to-MLS1
 ip address 192.168.23.2 255.255.255.252
 ipv6 address 2021:ACAD:ACAD:23::2/112
 ipv6 ospf 1 area 0
 ospf network point-to-point
 no shutdown
!
! --- Enlace a MLS2 (OSPF) ---
interface Ethernet0/2
 description RA-to-MLS2
 ip address 192.168.13.2 255.255.255.252
 ipv6 address 2021:ACAD:ACAD:13::2/112
 ipv6 ospf 1 area 0
 ospf network point-to-point
 no shutdown
!
! --- OSPFv2 ---
router ospf 1
 router-id 1.1.1.1
 passive-interface default
 no passive-interface Ethernet0/2
 no passive-interface Ethernet0/3
!
! --- OSPFv3 (IPv6) ---
ipv6 router ospf 1
 router-id 1.1.1.1
 passive-interface default
 no passive-interface Ethernet0/2
 no passive-interface Ethernet0/3
!
! --- EIGRPv6 con RB ---
ipv6 router eigrp 123
 eigrp router-id 1.1.1.1
 passive-interface default
 no passive-interface Ethernet0/0
!
! --- DHCPv4 server: VLAN10 ENCOR ---
ip dhcp pool VLAN10-ENCOR
 network 172.16.10.0 255.255.255.0
 default-router 172.16.10.254
 dns-server 8.8.8.8
 lease 7
ip dhcp excluded-address 172.16.10.1 172.16.10.5
!
! --- DHCPv4 server: VLAN20 ENARSI ---
ip dhcp pool VLAN20-ENARSI
 network 172.16.20.0 255.255.255.0
 default-router 172.16.20.254
 dns-server 8.8.8.8
 lease 7
ip dhcp excluded-address 172.16.20.1 172.16.20.5
!
! --- DHCPv4 server: VLAN30 ROUTE ---
ip dhcp pool VLAN30-ROUTE
 network 172.16.30.0 255.255.255.0
 default-router 172.16.30.254
 dns-server 8.8.8.8
 lease 7
ip dhcp excluded-address 172.16.30.1 172.16.30.5
!
! --- DHCPv4 server: VLAN40 SWITCH ---
ip dhcp pool VLAN40-SWITCH
 network 172.16.40.0 255.255.255.0
 default-router 172.16.40.254
 dns-server 8.8.8.8
 lease 7
ip dhcp excluded-address 172.16.40.1 172.16.40.5
!
end
"""

# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------
files = {
    "br.cfg": br,
    "isp.cfg": isp,
    "rb.cfg": rb,
    "ra.cfg": ra,
}

for name, content in files.items():
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] wrote {path} ({len(content)} bytes)")

print(f"\nGenerados {len(files)} archivos de configuración en {OUT_DIR}")
