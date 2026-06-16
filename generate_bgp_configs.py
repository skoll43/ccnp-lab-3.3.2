"""Generate BGP configs for R1, R2, R3, ISP, BR."""

from pathlib import Path

OUT_DIR = Path(r"C:\Users\lukas\Downloads\CCNPlabs\configs")
OUT_DIR.mkdir(exist_ok=True)

R1_BGP = """ipv6 unicast-routing
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

R2_BGP = """ipv6 unicast-routing
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

R3_BGP = """ipv6 unicast-routing
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

ISP_BGP = """ipv6 unicast-routing
ipv6 cef
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
  network 3001:ABCD:ABCD:8::8/128
  network 3001:ABCD:ABCD:209::/112
  network 3001:ABCD:ABCD:220::/112
  neighbor 209.50.0.1 activate
  neighbor 220.50.0.1 activate
 exit-address-family
!
end
"""

BR_BGP = """ipv6 unicast-routing
ipv6 cef
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

(OUT_DIR / "r1_bgp.cfg").write_text(R1_BGP, encoding="utf-8")
(OUT_DIR / "r2_bgp.cfg").write_text(R2_BGP, encoding="utf-8")
(OUT_DIR / "r3_bgp.cfg").write_text(R3_BGP, encoding="utf-8")
(OUT_DIR / "isp_bgp.cfg").write_text(ISP_BGP, encoding="utf-8")
(OUT_DIR / "br_bgp.cfg").write_text(BR_BGP, encoding="utf-8")
print("Generated BGP configs: r1_bgp.cfg, r2_bgp.cfg, r3_bgp.cfg, isp_bgp.cfg, br_bgp.cfg")
