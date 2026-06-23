# Lab 16 — Aplicación de una Red Corporativa Enterprise

> **Fuente:** `lab16/Laboratorio N°16 Aplicación de una Red Corporativa Enterprise (1).pdf`
> **Alcance de esta iteración:** Direccionamiento IP (IPv4/IPv6) y túnel GRE 6over4 (IPv6 sobre IPv4).

---

## 1. Dispositivos

| Dispositivo | Rol | Plataforma | Notas |
|-------------|-----|-----------|-------|
| BR | Borde BGP | Router | AS 65500, loopback 8.8.8.8 / 2021:ACAD:ACAD:8::8/128 |
| ISP | Proveedor | Router | AS 100 |
| RB | Borde con EIGRP | Router | AS 200, par EIGRP con RA |
| RA | Enrutamiento + DHCP | Router | OSPF Área 0, EIGRP AS 123, DHCP server |
| MLS1 | Multicapa core | L3 Switch | OSPF, HSRP, root VLAN10/20 |
| MLS2 | Multicapa core | L3 Switch | OSPF, HSRP, root VLAN30/40 |
| ALS1 | Acceso | L2 Switch | Port-channel Po1 (PAgP) y Po5 (Static) hacia MLS1/ALS2 |
| ALS2 | Acceso | L2 Switch | Port-channel Po3/4 hacia MLS2/ALS1 |
| PCs | End-hosts | — | 4 PCs: VLAN10/20/30/40 (IPv4: DHCP, IPv6: A/B/C/D) |

---

## 2. Direccionamiento IPv4

### 2.1 VLANs de datos

| VLAN | Nombre | Subred | Gateway (última IP) |
|------|--------|--------|----------------------|
| 10 | ENCOR | 172.16.10.0/24 | 172.16.10.254 |
| 20 | ENARSI | 172.16.20.0/24 | 172.16.20.254 |
| 30 | ROUTE | 172.16.30.0/24 | 172.16.30.254 |
| 40 | SWITCH | 172.16.40.0/24 | 172.16.40.254 |

> DHCP server: **RA**. Excluir las **primeras 5 direcciones** de cada pool.

### 2.2 Enlaces punto a punto (OSPF Área 0)

| Enlace | Subred IPv4 | IPv6 |
|--------|-------------|------|
| RA ↔ MLS1 | 192.168.23.0/30 | 2021:ACAD:ACAD:23::/112 |
| RA ↔ MLS2 | 192.168.13.0/30 | 2021:ACAD:ACAD:13::/112 |
| MLS1 ↔ MLS2 (Po2 L3 LACP) | 172.16.12.0/30 | 2021:ACAD:ACAD:12::/112 |
| RA ↔ RB (EIGRP) | 172.16.100.0/24 | 2021:ACAD:ACAD:100::/64 (EIGRPv6: 2021:ACAD:ACAD:200::/64) |
| RB ↔ ISP | 219.50.0.0/30 | — |
| ISP ↔ BR | 220.50.0.0/30 | — |

### 2.3 Direcciones IP de interfaces (resumen)

| Dispositivo | Interfaz | IPv4 | IPv6 |
|-------------|----------|------|------|
| BR | Lo0 | 8.8.8.8/32 | 2021:ACAD:ACAD:8::8/128 |
| BR | G0/2 (↔ ISP) | 220.50.0.1/30 | — |
| ISP | G0/2 (↔ BR) | 220.50.0.2/30 | — |
| ISP | G0/1 (↔ RB) | 219.50.0.2/30 | — |
| RB | G0/1 (↔ ISP) | 219.50.0.1/30 | — |
| RB | G0/0 (↔ RA) | 172.16.100.2/24 | 2021:ACAD:ACAD:200::/64 |
| RA | G0/0 (↔ RB) | 172.16.100.1/24 | 2021:ACAD:ACAD:100::1/64 |
| RA | G0/3 (↔ MLS1) | 192.168.23.2/30 | 2021:ACAD:ACAD:23::/112 |
| RA | G0/2 (↔ MLS2) | 192.168.13.2/30 | 2021:ACAD:ACAD:13::/112 |
| MLS1 | G0/3 (↔ RA) | 192.168.23.1/30 | 2021:ACAD:ACAD:23::1/112 |
| MLS1 | G0/0 (Po2 ↔ MLS2) | 172.16.12.1/30 | 2021:ACAD:ACAD:12::1/112 |
| MLS2 | G0/2 (↔ RA) | 192.168.13.1/30 | 2021:ACAD:ACAD:13::1/112 |
| MLS2 | G0/0 (Po2 ↔ MLS1) | 172.16.12.2/30 | 2021:ACAD:ACAD:12::2/112 |

### 2.4 Port-channels L2 (capa de acceso/distribución)

| Port-channel | Protocolo | Miembros |
|--------------|-----------|----------|
| Po1 | PAgP | MLS1 G1/0 ↔ ALS1 G1/2 |
| Po2 | LACP (L3) | MLS1 G0/0 — G0/1 ↔ MLS2 G0/0 — G0/1 |
| Po3 | Static (LACP en diagrama) | MLS2 ↔ ALS1 |
| Po4 | LACP | MLS2 G1/0 ↔ ALS2 G1/1 |
| Po5 | Static | MLS1 ↔ ALS2 |
| Po6 | PAgP | ALS1 G0/0 — G0/1 ↔ ALS2 G0/0 — G0/1 |

---

## 3. Direccionamiento IPv6

| VLAN | Subred |
|------|--------|
| 10 | 2021:ACAD:ACAD:10::/64 |
| 20 | 2021:ACAD:ACAD:20::/64 |
| 30 | 2021:ACAD:ACAD:30::/64 |
| 40 | 2021:ACAD:ACAD:40::/64 |

> IPv6 de PCs: A (VLAN10), B (VLAN20), C (VLAN30), D (VLAN40).

---

## 4. Resumen de protocolos

| Dominio | Protocolo IPv4 | Protocolo IPv6 |
|---------|----------------|---------------|
| Acceso ↔ Distribución | — | — |
| Distribución ↔ Core (MLS1/MLS2 ↔ RA) | OSPFv2 Área 0 | OSPFv3 Área 0 |
| RB ↔ ISP ↔ BR | eBGP (AS 200/100/65500) | — |
| RB ↔ RA | EIGRP AS 123 | EIGRPv6 (2021:ACAD:ACAD:200::/64) |
| MP-BGP | IPv4 only | — |

---

## 5. Túnel GRE 6over4 (IPv6 sobre IPv4) — **alcance de esta iteración**

**Objetivo:** Que el tráfico IPv6 corporativo (MLS1/MLS2/RA) pueda alcanzar el prefijo loopback de **BR (2021:ACAD:ACAD:8::8/128)** encapsulado en GRE sobre IPv4, y luego enrutado con **EIGRPv6** desde el otro extremo.

### 5.1 Topología lógica del túnel

```
[ MLS1/MLS2/RA ]  --- IPv4 (OSPF/BGP) --- [ RB ] --- eBGP IPv4 --- [ ISP ] --- eBGP IPv4 --- [ BR ]
       |                                                                                          |
       └────────── Túnel GRE IPv6 (2021:ACAD:ACAD:200::/64, 6over4) ─────────────────────────────┘
                                      ▲
                                      │  ipv6 eigrp 123 (sobre túnel)
                                      └─ Origen túnel: RB E0/1 (219.50.0.1)
                                         Destino túnel: BR E0/2 (220.50.0.1)
```

### 5.2 Plan de direccionamiento del túnel (propuesto)

| Elemento | Valor |
|----------|-------|
| Origen del túnel (tunnel source) | RB Ethernet0/1 (219.50.0.1) |
| Destino del túnel (tunnel destination) | BR Ethernet0/2 (220.50.0.1) |
| Modo | `tunnel mode gre ip` |
| Dirección IPv6 del túnel (BR) | 2021:ACAD:ACAD:200::1/64 |
| Dirección IPv6 del túnel (RB) | 2021:ACAD:ACAD:200::2/64 |
| Loopback IPv6 BR (prefijo anunciado) | 2021:ACAD:ACAD:8:8::8/128 |
| Proceso EIGRPv6 | AS 123, sobre Tunnel0 |

> **Importante:** la loopback `2021:ACAD:ACAD:8:8::8/128` de BR **no puede
> estar en el mismo /64 que el túnel** porque IOS rechaza interfaces con
> prefijos solapados. Por eso el túnel usa 200::/64.

### 5.3 Configuración objetivo

#### Router BR (AS 65500)

```cisco
! Loopback que participa como prefijo en EIGRPv6 vía túnel
interface Loopback0
 ip address 8.8.8.8 255.255.255.255
 ipv6 address 2021:ACAD:ACAD:8::8/128

! Enlace a ISP (eBGP IPv4)
interface GigabitEthernet0/2
 ip address 220.50.0.1 255.255.255.252

! BGP con ISP (anuncio de Lo0 8.8.8.8/32)
router bgp 65500
 neighbor 220.50.0.2 remote-as 100
 network 8.8.8.8 mask 255.255.255.255

! Túnel GRE IPv6-over-IPv4
interface Tunnel0
 ipv6 address 2021:ACAD:ACAD:8::1/64
 ipv6 eigrp 123
 tunnel source GigabitEthernet0/2
 tunnel destination 220.50.0.2  ! o el Lo0 de RB si RB inicia el túnel
 tunnel mode gre ip

! EIGRPv6 sobre el túnel (proceso 123)
ipv6 router eigrp 123
 eigrp router-id 8.8.8.8
 passive-interface default
 no passive-interface Tunnel0
```

> **Nota:** si BR no tiene adyacencia OSPF con la red corporativa, **no** levantará EIGRPv6 con nadie más que con RB a través del túnel. En este lab, BR es el único par EIGRPv6 vía túnel.

#### Router RB (AS 200)

```cisco
! Enlace a RA (EIGRPv6)
interface GigabitEthernet0/0
 ip address 172.16.100.2 255.255.255.0
 ipv6 address 2021:ACAD:ACAD:100::2/64
 ipv6 eigrp 123

! Enlace a ISP (eBGP IPv4)
interface GigabitEthernet0/1
 ip address 219.50.0.1 255.255.255.252

! Túnel GRE hacia BR
interface Tunnel0
 ipv6 address 2021:ACAD:ACAD:8::2/64
 ipv6 eigrp 123
 tunnel source GigabitEthernet0/1
 tunnel destination 220.50.0.1
 tunnel mode gre ip

router bgp 200
 neighbor 219.50.0.2 remote-as 100
 network 172.16.100.0 mask 255.255.255.0
 redistribute eigrp 123 route-map REDIST  ! o según requirementas completas

ipv6 router eigrp 123
 eigrp router-id 2.2.2.2
 passive-interface default
 no passive-interface GigabitEthernet0/0
 no passive-interface Tunnel0
```

### 5.4 Verificaciones

```text
! En BR
show interface Tunnel0
show ipv6 interface brief
show ipv6 eigrp neighbors
show ipv6 route eigrp

! En RB
show interface Tunnel0
show ipv6 eigrp neighbors
show ipv6 route eigrp

! Desde MLS1 / MLS2 / RA (debería llegar por OSPF+EIGRPv6)
ping 2021:ACAD:ACAD:8::8 source <ipv6-mls1>
traceroute 2021:ACAD:ACAD:8::8
```

Resultado esperado:
- `show ipv6 route eigrp` en MLS1/MLS2/RA ve `2021:ACAD:ACAD:8::/64` (o el prefijo exacto del túnel) como ruta EIGRP externa.
- `ping 2021:ACAD:ACAD:8::8` exitoso desde cualquier equipo de la red corporativa.

---

## 6. Pendientes (fuera de alcance de esta iteración)

- [ ] Switching L2/L3 completo (VTP off, trunks, port-channels).
- [ ] RPVST+ con root bridges por VLAN.
- [ ] Port-security, errdisable recovery, DHCP snooping / ARP inspection.
- [ ] HSRPv2 con VIP `IP1` y `::1` por VLAN; temporizadores y tracking.
- [ ] IP SLA + tracking para failover DNS.
- [ ] Redistribución OSPF ↔ EIGRP IPv4 con route-maps (métrica 85 para OSPF, K-values para EIGRP).
- [ ] Redistribución directa OSPF ↔ EIGRP IPv6.
- [ ] MP-BGP IPv4 completo y redistribuciones IGP↔EGP.

---

## 7. Inventario de imágenes extraídas del PDF

| Archivo | Tamaño | Uso |
|---------|--------|-----|
| `assets/page1_img1.jpeg` | 8 KB | Logo institucional |
| `assets/page1_img2.png` | 272 KB | **Topología principal** (1960×1357) |
