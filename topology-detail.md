# Inventario detallado de interfaces y protocolos — Lab 3.3.2

> Extraído de `assets/image2.png` (topología principal).
> ⚠️ Los campos marcados con `?` no son visibles en el diagrama y deben deducirse durante la configuración.

## 1. Dispositivos y roles

| Dispositivo | Rol | AS / Sistema autónomo | Observaciones |
|-------------|-----|----------------------|---------------|
| BR | Router frontera (cliente/peer BGP) | 300 | Loopback 192.168.100.1/32, 3001:ABCD:ABCD:100::1/128 |
| ISP | Router proveedor / upstream | 200 | Loopback 8.8.8.8/32, 3001:ABCD:ABCD:8:8::/128 |
| R1 | Router frontera + DHCP server + iBGP + OSPF ABR | 100 | Etiquetado DHCPv4/DHCPv6 |
| R2 | Router OSPF ABR + VPN peer + iBGP | 100 | Loopback 2.2.2.2/32 |
| R3 | Router OSPF ABR + VPN peer + iBGP | 100 | Loopback 3.3.3.3/32 |
| SWA | Switch distribución (distribution) | — | IPv4: 7 (último octeto) |
| SWB | Switch distribución (distribution) | — | IPv4: 21 (último octeto) |
| SWC | Switch acceso (access) | — | IPv4: 14 (último octeto) |
| SWD | Switch acceso (access) | — | IPv4: 28 (último octeto) |
| PC-VLAN21 | Host FINANZAS | — | IPv4/IPv6 por DHCP |
| PC-VLAN22 | Host GESTIÓN | — | IPv4/IPv6 por DHCP |
| PC-VLAN23 | Host FUERZA-VENTAS | — | IPv4/IPv6 por DHCP |
| PC-VLAN24 | Host RRHH | — | IPv4/IPv6 por DHCP |

---

## 2. Matriz de interfaces de switches (verificado contra el diagrama)

| Switch | Interfaz | Conecta a | Interfaz remota | EtherChannel |
|--------|----------|-----------|-----------------|--------------|
| **SWA** | E0/3 | R2 | E0/3 | — |
| **SWA** | E1/0 | SWB | E1/0 | Po6 LACP |
| **SWA** | E1/1 | SWB | E1/1 | Po6 LACP |
| **SWA** | E1/2 | SWC | E1/2 | Po5 Static |
| **SWA** | E1/3 | SWC | E1/3 | Po5 Static |
| **SWA** | E0/0 | SWD | E0/0 | Po4 PAgP |
| **SWA** | E0/1 | SWD | E0/1 | Po4 PAgP |
| **SWB** | E0/3 | R3 | E0/3 | — |
| **SWB** | E1/0 | SWA | E1/0 | Po6 LACP |
| **SWB** | E1/1 | SWA | E1/1 | Po6 LACP |
| **SWB** | E0/0 | SWC | E0/0 | Po2 LACP |
| **SWB** | E0/1 | SWC | E0/1 | Po2 LACP |
| **SWB** | E1/2 | SWD | E1/2 | Po3 Static |
| **SWB** | E1/3 | SWD | E1/3 | Po3 Static |
| **SWC** | E1/2 | SWA | E1/2 | Po5 Static |
| **SWC** | E1/3 | SWA | E1/3 | Po5 Static |
| **SWC** | E0/0 | SWB | E0/0 | Po2 LACP |
| **SWC** | E0/1 | SWB | E0/1 | Po2 LACP |
| **SWC** | E1/0 | SWD | E1/0 | Po1 PAgP |
| **SWC** | E1/1 | SWD | E1/1 | Po1 PAgP |
| **SWC** | E0/2 | PC-VLAN21 | — | — |
| **SWC** | E0/3 | PC-VLAN22 | — | — |
| **SWD** | E0/0 | SWA | E0/0 | Po4 PAgP |
| **SWD** | E0/1 | SWA | E0/1 | Po4 PAgP |
| **SWD** | E1/2 | SWB | E1/2 | Po3 Static |
| **SWD** | E1/3 | SWB | E1/3 | Po3 Static |
| **SWD** | E1/0 | SWC | E1/0 | Po1 PAgP |
| **SWD** | E1/1 | SWC | E1/1 | Po1 PAgP |
| **SWD** | E0/2 | PC-VLAN23 | — | — |
| **SWD** | E0/3 | PC-VLAN24 | — | — |

---

## 3. Tabla completa de interfaces y conectividad física

| Dispositivo A | Interfaz A | Dispositivo B | Interfaz B | Tipo / Protocolo | Subred IPv4 | Subred IPv6 | Notas |
|---------------|------------|---------------|------------|------------------|-------------|-------------|-------|
| BR | E0/2 | ISP | E0/2 | eBGP (AS 300 ↔ 200) | 220.50.0.0/30 (BR .1, ISP .2) | 3001:ABCD:ABCD:220::/112 | — |
| ISP | E0/3 | R1 | E0/3 | eBGP (AS 200 ↔ 100) | ? | ? | Solo visibles host labels: R1 .1, ISP .2 |
| R1 | E0/1 | R2 | E0/1 | OSPF Área 0 | 192.168.12.0/24 (R1 .1, R2 .2) | 3001:ABCD:ABCD:12::/64 | — |
| R1 | E0/2 | R3 | E0/2 | OSPF Área 0 | 192.168.13.0/24 (R1 .1, R3 .3) | 3001:ABCD:ABCD:13::/64 | — |
| R2 | E0/3 | SWA | E0/3 | Trunk / routing L3? | ? | ? | Enlace hacia capa de distribución |
| R3 | E0/3 | SWB | E0/3 | Trunk / routing L3? | ? | ? | Enlace hacia capa de distribución |
| SWA | E1/0 | SWB | E1/0 | EtherChannel Po6 (LACP) | — | — | Capa 2 |
| SWA | E1/1 | SWB | E1/1 | EtherChannel Po6 (LACP) | — | — | Capa 2 |
| SWA | E1/2 | SWC | E1/2 | EtherChannel Po5 (Static) | — | — | Capa 2 |
| SWA | E1/3 | SWC | E1/3 | EtherChannel Po5 (Static) | — | — | Capa 2 |
| SWA | E0/0 | SWD | E0/0 | EtherChannel Po4 (PAgP) | — | — | Capa 2 |
| SWA | E0/1 | SWD | E0/1 | EtherChannel Po4 (PAgP) | — | — | Capa 2 |
| SWB | E0/0 | SWC | E0/0 | EtherChannel Po2 (LACP) | — | — | Capa 2 |
| SWB | E0/1 | SWC | E0/1 | EtherChannel Po2 (LACP) | — | — | Capa 2 |
| SWB | E1/2 | SWD | E1/2 | EtherChannel Po3 (Static) | — | — | Capa 2 |
| SWB | E1/3 | SWD | E1/3 | EtherChannel Po3 (Static) | — | — | Capa 2 |
| SWC | E1/0 | SWD | E1/0 | EtherChannel Po1 (PAgP) | — | — | Capa 2 |
| SWC | E1/1 | SWD | E1/1 | EtherChannel Po1 (PAgP) | — | — | Capa 2 |
| SWC | E0/2 | PC-VLAN21 | — | Acceso VLAN 21 | 10.0.21.0/24 | 3001:ABCD:ABCD:A::/64 | DHCP |
| SWC | E0/3 | PC-VLAN22 | — | Acceso VLAN 22 | 10.0.31.0/24 | 3001:ABCD:ABCD:B::/64 | DHCP |
| SWD | E0/2 | PC-VLAN23 | — | Acceso VLAN 23 | 10.0.41.0/24 | 3001:ABCD:ABCD:C::/64 | DHCP |
| SWD | E0/3 | PC-VLAN24 | — | Acceso VLAN 24 | 10.0.51.0/24 | 3001:ABCD:ABCD:D::/64 | DHCP |

---

## 4. EtherChannels

| Nombre | Modo | Miembros SWA/SWB | Miembros SWC/SWD | Par |
|--------|------|------------------|------------------|-----|
| Po1 | PAgP | — | SWC E1/0-1 ↔ SWD E1/0-1 | SWC ↔ SWD |
| Po2 | LACP | — | SWB E0/0-1 ↔ SWC E0/0-1 | SWB ↔ SWC |
| Po3 | Static | — | SWB E1/2-3 ↔ SWD E1/2-3 | SWB ↔ SWD |
| Po4 | PAgP | SWA E0/0-1 ↔ SWD E0/0-1 | — | SWA ↔ SWD |
| Po5 | Static | SWA E1/2-3 ↔ SWC E1/2-3 | — | SWA ↔ SWC |
| Po6 | LACP | SWA E1/0-1 ↔ SWB E1/0-1 | — | SWA ↔ SWB |

---

## 5. Protocolos y dónde corren

| Protocolo | Alcance / Dispositivos | Detalle |
|-----------|------------------------|---------|
| **BGP** | BR (300) ↔ ISP (200) | eBGP IPv4/IPv6 |
| **BGP** | ISP (200) ↔ R1 (100) | eBGP IPv4/IPv6 |
| **MP-BGP / iBGP** | R1, R2, R3 (AS 100) | Loopbacks como prefijos; se requiere redistribución IGP↔EGP |
| **OSPF** | R1, R2, R3 | Área 0 (R1-R2, R1-R3) |
| **OSPF** | R2, R3 | Área 100 (R2-R3); se debe sumarizar y propagar al área 0 |
| **VPN Site-to-Site** | R2 ↔ R3 | Túnel sobre el backbone de capa 2; parámetros a elección |
| **Inter-VLAN routing** | R2 y R3 | Default-gateway última IP asignable (IPv4) y ::FF (IPv6) |
| **FHRP / Alta disponibilidad capa 3** | R2 y R3 | VLAN21/22 prefieren R2; VLAN23/24 prefieren R3 |
| **DHCPv4 / DHCPv6** | R1 | Servidor DHCP para PCs |
| **PVST+ Rápido** | SWA, SWB, SWC, SWD | Spanning-Tree rapid-PVST+ |
| **Port-security** | SWC, SWD | Máximo 2 direcciones MAC, desactivar puerto en error |
| **STP stability features** | Interfaces apropiadas | Root guard / BPDU guard / loop guard (a elección) |
| **PACL** | SWA/SWB/SWC/SWD | VLAN21 no se comunica con VLAN22 (filtro de capa 2) |
| **VACL** | SWA/SWB | VLAN23 no se comunica con VLAN24 |

---

## 6. VLANs

| VLAN | Nombre | Subred IPv4 | Subred IPv6 | Gateway (IPv4) | Gateway (IPv6) | PCs conectadas |
|------|--------|-------------|-------------|----------------|----------------|----------------|
| 21 | FINANZAS | 10.0.21.0/24 | 3001:ABCD:ABCD:A::/64 | 10.0.21.254 | 3001:ABCD:ABCD:A::FF | PC bajo SWC |
| 22 | GESTIÓN | 10.0.31.0/24 | 3001:ABCD:ABCD:B::/64 | 10.0.31.254 | 3001:ABCD:ABCD:B::FF | PC bajo SWC |
| 23 | FUERZA-VENTAS | 10.0.41.0/24 | 3001:ABCD:ABCD:C::/64 | 10.0.41.254 | 3001:ABCD:ABCD:C::FF | PC bajo SWD |
| 24 | RRHH | 10.0.51.0/24 | 3001:ABCD:ABCD:D::/64 | 10.0.51.254 | 3001:ABCD:ABCD:D::FF | PC bajo SWD |
| 25 | ADM | 10.0.61.0/24 | 3001:ABCD:ABCD:E::/64 | 10.0.61.254 | 3001:ABCD:ABCD:E::FF | Sin PCs en diagrama |

> Nota: "última IP asignable" para IPv4 es la .254 de cada /24. Para IPv6 el diagrama indica `::FF` como default-gateway.

---

## 7. Loopbacks y prefijos de enrutamiento

| Dispositivo | Loopback IPv4 | Loopback IPv6 | Uso |
|-------------|---------------|---------------|-----|
| BR | 192.168.100.1/32 | 3001:ABCD:ABCD:100::1/128 | Prefijo BGP AS 300 |
| ISP | 8.8.8.8/32 | 3001:ABCD:ABCD:8:8::/128 | Prefijo BGP AS 200 |
| R1 | ? | ? | Probable loopback para BGP/OSPF (no visible) |
| R2 | 2.2.2.2/32 | ? | Prefijo iBGP / OSPF |
| R3 | 3.3.3.3/32 | ? | Prefijo iBGP / OSPF |

---

## 8. Incógnitas del diagrama (por confirmar durante la configuración)

1. **Subred ISP ↔ R1**: no está etiquetada. Solo se ven host labels `.1` (R1) y `.2` (ISP).
2. **Loopback de R1**: no aparece en el diagrama, pero se usa para iBGP/MP-BGP.
3. **IPv6 de loopbacks R2 y R3**: no visibles.
4. **Direccionamiento exacto de los enlaces R2↔SWA y R3↔SWB**: no visibles.
5. **Mecanismo FHRP exacto**: el requerimiento dice "alta disponibilidad de capa 3"; se asume HSRP/VRRP/GLBP.
6. **Tipo de túnel Site-to-Site**: el requerimiento dice "Utilizar parámetros a elección".
7. **AS y route-maps de BGP**: se requiere influenciar atributos para que el path hacia BR/ISP muestre 2×AS200 en IPv4 y 3×AS200 en IPv6.
