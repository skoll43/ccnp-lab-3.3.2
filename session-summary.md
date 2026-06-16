# Resumen de sesión — Lab 3.3.2 / Laboratorio N°15

**Fecha:** 2026-06-14  
**Directorio de trabajo:** `C:\Users\lukas\Downloads\CCNPlabs`  
**Objetivo:** Preparar y verificar las configuraciones completas del laboratorio antes de aplicarlas a los dispositivos IOL/IOU.

---

## 1. Estado actual

Se generó un conjunto completo y consistente de configuraciones para todos los dispositivos del laboratorio. Las configuraciones antiguas con errores fueron archivadas en `configs/old/`.

### Archivos de configuración listos para aplicar

| Dispositivo | Archivos | Descripción |
|-------------|----------|-------------|
| SWA, SWB, SWC, SWD | `configs/swa_layer2.cfg`, etc. | VLANs, trunks, EtherChannels, port-security, PACL, VACL |
| R1 | `configs/r1_base.cfg` + `configs/r1_bgp.cfg` | Interfaces, loopback, DHCPv4/v6, OSPF, BGP |
| R2 | `configs/r2_base.cfg` + `configs/r2_vpn.cfg` + `configs/r2_bgp.cfg` | Subinterfaces, HSRP, OSPF, DHCP relay, VPN, BGP |
| R3 | `configs/r3_base.cfg` + `configs/r3_vpn.cfg` + `configs/r3_bgp.cfg` | Subinterfaces, HSRP, OSPF, DHCP relay, VPN, BGP |
| ISP | `configs/isp.cfg` | Interfaces, loopback, BGP AS 200 |
| BR | `configs/br.cfg` | Interfaces, loopback, BGP AS 300, AS-path prepending |

### Documentos creados/actualizados

| Archivo | Descripción |
|---------|-------------|
| `generate_all_configs.py` | Generador unificado de todas las configuraciones |
| `verify_configs.py` | Verificador de consistencia de configuraciones |
| `deployment-plan.md` | Plan paso a paso para aplicar y verificar |
| `session-summary.md` | Este resumen |

---

## 2. Correciones realizadas respecto a la sesión anterior

### Configuración de routers

- **R1**: se agregó config base completa con direcciones WAN, loopback, OSPF y DHCPv4/v6.
- **R2/R3**: se corrigieron direcciones IPv4/IPv6 de loopbacks y enlaces WAN.
- **R2/R3**: se eliminó la duplicación de bloques OSPF y el comando inválido `ip ospf 1 passive`.
- **R2/R3**: se configuró `passive-interface default` con solo `Tunnel0` y el enlace hacia R1 como activos.
- **R2/R3**: se agregó `ip helper-address` e `ipv6 dhcp relay destination` para reenviar DHCP hacia R1.
- **R2/R3**: se agregaron flags `ipv6 nd managed-config-flag` y `other-config-flag` para DHCPv6 stateful.

### VPN

- Se cambió `tunnel mode gre multipoint` a `tunnel mode gre ip` (túnel punto a punto).
- Se mantuvo GRE sobre IPsec con IKEv1/AES-256/SHA256/DH14.

### BGP

- Se crearon configs base para ISP y BR, no solo BGP.
- Se corrigió la loopback IPv6 de ISP a `3001:ABCD:ABCD:8:8::8/128`.
- Se verificó que los vecinos iBGP/eBGP usen las direcciones correctas.
- Se mantuvo AS-path prepending en BR: IPv4 prepend `200`, IPv6 prepend `200 200`.

### Seguridad

- **PACL IPv4/IPv6** en SWC para bloquear VLAN21 ↔ VLAN22 en puertos de acceso.
- **VACL IPv4** en todos los switches para VLAN23 ↔ VLAN24.
- **Router ACL IPv4/IPv6** en R2/R3 subinterfaces VLAN23/VLAN24 para reforzar el bloqueo inter-VLAN (VACL en switches L2 no bloquea tráfico enrutado).

### Switches

- Se corrigió el bug que mostraba el diccionario completo como nombre de VLAN.
- Se añadieron PACL IPv6 y VACL.

---

## 3. Verificaciones automáticas

El script `verify_configs.py` confirma que:

- Todos los archivos requeridos existen.
- No hay comandos inválidos como `tunnel mode gre multipoint` ni `ip ospf 1 passive`.
- Los vecinos BGP son correctos para cada router.
- HSRP priorities son consistentes (R2 activo para VLAN21/22, R3 activo para VLAN23/24/25).
- Los nombres de VLAN son correctos.

Resultado actual: **OK**.

---

## 4. Plan de aplicación

Ver `deployment-plan.md` para el orden completo, comandos de verificación y troubleshooting.

Resumen del orden:

1. Switches (SWA, SWB, SWC, SWD).
2. R1 base + BGP.
3. ISP y BR.
4. R2 base + VPN + BGP.
5. R3 base + VPN + BGP.

---

## 5. Pendientes de ejecución

1. Reiniciar dispositivos en IULab si es necesario.
2. Aplicar configuraciones según `deployment-plan.md`.
3. Verificar OSPF, BGP, VPN, DHCP, PACL/VACL y conectividad IPv4/IPv6.
4. Comprobar AS-path prepending desde R1.

---

## 6. Notas técnicas

- Guardado en IOL/IOU: `copy running-config unix:config-00001`.
- `push_config.py` aplica config y guarda automáticamente.
- Las consolas IOL/IOU son inestables; aplicar un dispositivo a la vez.
- Los archivos antiguos con errores están en `configs/old/`.
