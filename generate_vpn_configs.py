"""Generate VPN Site-to-Site config for R2 and R3 (GRE over IPsec)."""

from pathlib import Path

OUT_DIR = Path(r"C:\Users\lukas\Downloads\CCNPlabs\configs")
OUT_DIR.mkdir(exist_ok=True)

COMMON = """!
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

R2 = f"""ipv6 unicast-routing
ipv6 cef
{COMMON}
!
interface Tunnel0
 ip address 10.100.100.1 255.255.255.252
 ipv6 address 3001:ABCD:ABCD:100::1/64
 tunnel source Loopback2
 tunnel destination 3.3.3.3
 tunnel mode gre multipoint
 tunnel protection ipsec profile VPN-PROFILE
 ip ospf 1 area 100
 ipv6 ospf 1 area 100
!
end
"""

R3 = f"""ipv6 unicast-routing
ipv6 cef
{COMMON}
!
interface Tunnel0
 ip address 10.100.100.2 255.255.255.252
 ipv6 address 3001:ABCD:ABCD:100::2/64
 tunnel source Loopback3
 tunnel destination 2.2.2.2
 tunnel mode gre multipoint
 tunnel protection ipsec profile VPN-PROFILE
 ip ospf 1 area 100
 ipv6 ospf 1 area 100
!
end
"""

(OUT_DIR / "r2_vpn.cfg").write_text(R2, encoding="utf-8")
(OUT_DIR / "r3_vpn.cfg").write_text(R3, encoding="utf-8")
print("Generated r2_vpn.cfg and r3_vpn.cfg")
