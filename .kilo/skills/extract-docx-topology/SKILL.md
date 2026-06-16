---
name: extract-docx-topology
description: Extract topology images, device interfaces, protocols, and structured lab data from a Cisco/CCNP-style DOCX lab document.
---

# Skill: Extract topology and lab data from a DOCX

Use this skill when the user needs to pull images, text, interfaces, and protocols out of a Cisco/NetAcad/CCNP lab packaged as a `.docx` file.

## Goal
Produce a reproducible set of artifacts from the source DOCX:
- `lab-<id>-runbook.md` — human-readable guide with metadata, topology image, requirements, and connection placeholders.
- `topology-detail.md` — structured inventory of devices, interfaces, protocols, VLANs, and EtherChannels.
- `topology-detail.json` — machine-readable version of the inventory.
- `assets/` — extracted embedded images, with the topology image identified.

## Input
- Path to a `.docx` file that contains a network topology diagram and lab instructions.
- (Optional) A known IULab/remote title or import file name to record in the runbook.

## Steps

### 1. Inspect the DOCX package
A `.docx` is a ZIP archive. List its contents and identify:
- `word/document.xml` — main text.
- `word/media/image*.png|gif|jpeg` — embedded images.
- `word/_rels/document.xml.rels` — image ID-to-filename mapping.

### 2. Extract images
Copy all files from `word/media/` into an `assets/` directory next to the runbook.
Note each image size and identify the largest/complex one as the topology image.

### 3. Extract text
Parse `word/document.xml`:
- Preserve paragraph breaks.
- Detect list items via `w:numPr` and mark them with `- `.
- Do **not** rely on style names for headings (DOCX templates often reuse one style for headings and body text).
- Reconstruct sections by matching known section titles (e.g., "Requerimientos:", "Topología", "Preguntas:").

### 4. Read the topology image
Open the topology image and transcribe:
- **Devices**: routers, switches, PCs, ISP/BR, etc.
- **Interfaces**: every link label (e.g., `E0/1`, `G0/0`) on both ends.
- **EtherChannels**: port-channel names, member interfaces, mode (LACP/PAgP/Static).
- **Protocols**: BGP AS numbers, OSPF areas, VPN type, FHRP, STP mode, DHCP, PACL/VACL, etc.
- **Addressing**: IPv4/IPv6 subnets, loopbacks, gateway addresses.
- **VLANs**: IDs, names, subnets, access ports.

### 5. Resolve unknowns
If a subnet or interface IP is not visible in the diagram, mark it with `?` and add it to an "Unknowns" section. Later, back up the live device configs (`show running-config`) to fill in the gaps.

### 6. Build outputs
- `lab-<id>-runbook.md`: metadata, connection table with empty placeholders, topology image, extracted requirements, questions.
- `topology-detail.md`: device table, switch-interface matrix, link table, EtherChannel table, protocol matrix, VLAN table, loopback table, unknowns.
- `topology-detail.json`: same data in JSON for scripting.

### 7. Validate
- Ensure every extracted image is catalogued.
- Ensure every interface in the diagram appears in the interface matrix.
- Cross-check protocol statements against the requirements text.

## Tips
- Use `python-docx` or `zipfile + xml.etree.ElementTree` for extraction.
- In Python, the drawing wrapper for inline images is usually `{http://schemas.openxmlformats.org/wordprocessingml/2006/main}drawing`, not `wp:drawing`.
- Crop the topology image to read small labels more easily.
- A reusable helper script is available at `extract_docx_topology.py`.
- When consoles are used for backup, go one device at a time; direct console connections via terminal server can freeze if rushed.

## Example invocation
> "Extract the topology and requirements from `lab-3.3.2.docx` and build the runbook and inventory files."
