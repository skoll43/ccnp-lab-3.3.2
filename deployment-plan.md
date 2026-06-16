# Plan de aplicación paso a paso — Lab 3.3.2

> **Nota importante:** Los dispositivos IOL/IOU no guardan con `write memory`. El script `push_config.py` aplica la configuración y luego ejecuta `copy running-config unix:config-00001`.

## Archivos a utilizar

| Dispositivo | Archivos a aplicar (en orden) |
|-------------|------------------------------|
| SWA | `configs/swa_layer2.cfg` |
| SWB | `configs/swb_layer2.cfg` |
| SWC | `configs/swc_layer2.cfg` |
| SWD | `configs/swd_layer2.cfg` |
| R1 | `configs/r1_base.cfg` → `configs/r1_bgp.cfg` |
| R2 | `configs/r2_base.cfg` → `configs/r2_vpn.cfg` → `configs/r2_bgp.cfg` |
| R3 | `configs/r3_base.cfg` → `configs/r3_vpn.cfg` → `configs/r3_bgp.cfg` |
| ISP | `configs/isp.cfg` |
| BR | `configs/br.cfg` |

## Recomendación previa

Reiniciar todos los routers/switches en IULab para partir desde una configuración limpia. Esto evita conflictos con configuraciones antiguas.

## Orden de aplicación

1. **Switches capa 2** (SWA, SWB, SWC, SWD) — establecer dominios de broadcast, trunks y EtherChannels.
2. **R1, ISP, BR** — routers independientes de la capa 2 interna.
3. **R2 y R3** — dependen de los switches y de R1 para OSPF/BGP.

## Comandos de aplicación

```powershell
# 1. Switches
python push_config.py SWA 2005 configs\swa_layer2.cfg
python push_config.py SWB 2006 configs\swb_layer2.cfg
python push_config.py SWC 2007 configs\swc_layer2.cfg
python push_config.py SWD 2008 configs\swd_layer2.cfg

# 2. R1
python push_config.py R1 2001 configs\r1_base.cfg
python push_config.py R1 2001 configs\r1_bgp.cfg

# 3. ISP y BR
python push_config.py ISP 2004 configs\isp.cfg
python push_config.py BR 2013 configs\br.cfg

# 4. R2
python push_config.py R2 2002 configs\r2_base.cfg
python push_config.py R2 2002 configs\r2_vpn.cfg
python push_config.py R2 2002 configs\r2_bgp.cfg

# 5. R3
python push_config.py R3 2003 configs\r3_base.cfg
python push_config.py R3 2003 configs\r3_vpn.cfg
python push_config.py R3 2003 configs\r3_bgp.cfg
```

> Aplicar un dispositivo a la vez y esperar a que termine antes del siguiente, especialmente con routers que ejecutan OSPF/BGP.

## Verificaciones recomendadas después de aplicar

### Switches

```text
show vlan brief
show spanning-tree
show etherchannel summary
show interfaces trunk
show port-security
show vlan access-map
show vlan filter
```

### R2 / R3

```text
show ip interface brief
show ipv6 interface brief
show standby brief
show ip ospf neighbor
show ipv6 ospf neighbor
show ip route ospf
show ipv6 route ospf
show crypto isakmp sa
show crypto ipsec sa
show interface tunnel0
show ip ospf interface tunnel0
```

### R1

```text
show ip ospf neighbor
show ipv6 ospf neighbor
show ip route bgp
show ipv6 route bgp
show ip bgp summary
show ipv6 bgp summary
show ip dhcp pool
show ipv6 dhcp pool
```

### ISP / BR

```text
show ip bgp summary
show ipv6 bgp summary
show ip route bgp
show ipv6 route bgp
show ip bgp
show ipv6 bgp
```

## Verificaciones de conectividad

### IPv4

Desde cada PC o router:

```text
ping 10.0.21.254
ping 10.0.31.254
ping 10.0.41.254
ping 10.0.51.254
ping 10.0.61.254
ping 1.1.1.1
ping 2.2.2.2
ping 3.3.3.3
ping 8.8.8.8
ping 192.168.100.1
```

### IPv6

```text
ping 3001:ABCD:ABCD:A::FF
ping 3001:ABCD:ABCD:B::FF
ping 3001:ABCD:ABCD:C::FF
ping 3001:ABCD:ABCD:D::FF
ping 3001:ABCD:ABCD:E::FF
ping 3001:ABCD:ABCD:1::1
ping 3001:ABCD:ABCD:2::2
ping 3001:ABCD:ABCD:3::3
ping 3001:ABCD:ABCD:8:8::8
ping 3001:ABCD:ABCD:100::1
```

## Verificación de políticas de seguridad

### PACL: VLAN21 no se comunica con VLAN22

Desde PC-VLAN21 (10.0.21.x):

```text
ping 10.0.31.x    # debe fallar
```

Desde PC-VLAN22 (10.0.31.x):

```text
ping 10.0.21.x    # debe fallar
```

### VACL (reforzado con router ACL): VLAN23 no se comunica con VLAN24

Desde PC-VLAN23 (10.0.41.x):

```text
ping 10.0.51.x    # debe fallar
```

Desde PC-VLAN24 (10.0.51.x):

```text
ping 10.0.41.x    # debe fallar
```

### Verificación de AS-path prepending

Desde R1:

```text
show ip bgp 192.168.100.1
show ipv6 bgp 3001:ABCD:ABCD:100::1/128
```

Resultado esperado:

- IPv4: path `200 300 200` (dos AS 200).
- IPv6: path `200 300 200 200` (tres AS 200).

## Solución de problemas comunes

| Síntoma | Causa probable | Solución |
|---------|---------------|----------|
| Consola congelada / `Login failed` | Dispositivo colgado | Reiniciar en IULab |
| `startup-config file open failed` | NVRAM IOL dañada | Guardar con `copy running-config unix:config-00001` |
| OSPF no forma adyacencia R2-R3 en Área 100 | Subinterfaces no pasivas o túnel caído | Verificar `passive-interface default` y `Tunnel0` up/up |
| iBGP Idle | Loopbacks no alcanzables | Verificar OSPF Área 0 FULL entre R1-R2 y R1-R3 |
| DHCP no asigna IPv6 | RA no indica DHCPv6 | Verificar `ipv6 nd managed-config-flag` en subinterfaces |
| PCs no obtienen IP | DHCP relay caído | Verificar `ip helper-address 1.1.1.1` en subinterfaces R2/R3 |

## Notas finales

- Los archivos antiguos (`r1_router.cfg`, `r2_router.cfg`, `r3_router.cfg`, `isp_bgp.cfg`, `br_bgp.cfg`) fueron movidos a `configs/old/` para evitar confusiones.
- El generador unificado es `generate_all_configs.py`.
- El verificador es `verify_configs.py`.
- Si se modifica algún dato (por ejemplo, la subred ISP-R1), actualizar `generate_all_configs.py` y regenerar.
