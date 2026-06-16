import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import json

WORK_DIR = Path(r"C:\Users\lukas\Downloads\CCNPlabs")
DOCX = WORK_DIR / "3.3.2 Actividad Implementación de Seguridad sobre Tuneles.docx"
ASSETS = WORK_DIR / "assets"
RUNBOOK = WORK_DIR / "lab-3.3.2-runbook.md"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def q(tag):
    return f"{{{W_NS}}}{tag}"


def extract_images(docx_zip):
    ASSETS.mkdir(exist_ok=True)
    manifest = {}
    for name in docx_zip.namelist():
        if name.startswith("word/media/"):
            data = docx_zip.read(name)
            filename = Path(name).name
            (ASSETS / filename).write_bytes(data)
            manifest[name] = {"file": filename, "bytes": len(data)}
    return manifest


def build_relationships(docx_zip):
    rels = {}
    rel_path = "word/_rels/document.xml.rels"
    if rel_path in docx_zip.namelist():
        xml = docx_zip.read(rel_path)
        root = ET.fromstring(xml)
        for rel in root:
            rid = rel.get("Id")
            target = rel.get("Target")
            rel_type = rel.get("Type")
            if rid:
                rels[rid] = {"target": target, "type": rel_type}
    return rels


def paragraph_text(p_elem):
    parts = []
    for t in p_elem.iter(q("t")):
        if t.text:
            parts.append(t.text)
    return "".join(parts)


def list_prefix(p_elem):
    """Return a bullet/number prefix if the paragraph is a list item."""
    num_pr = p_elem.find(f".//{q('numPr')}")
    if num_pr is None:
        return ""
    # Try to find the actual number text in numbering.xml; fallback to '-'.
    ilvl = num_pr.find(q("ilvl"))
    level = ilvl.get(q("val")) if ilvl is not None else "0"
    numId = num_pr.find(q("numId"))
    # We don't resolve numbering definitions here; plain bullets are enough.
    return "- "


def image_references_in_paragraph(p_elem, rels):
    refs = []
    # In this DOCX the drawing wrapper is in the w: namespace.
    for drawing in p_elem.iter(q("drawing")):
        blip = drawing.find(f".//{{{A_NS}}}blip")
        if blip is not None:
            embed = blip.get(f"{{{REL_NS}}}embed")
            if embed and embed in rels:
                filename = Path(rels[embed]["target"]).name
                refs.append(filename)
    return refs


def parse_document(docx_zip, rels):
    xml = docx_zip.read("word/document.xml")
    root = ET.fromstring(xml)

    lines = []
    image_refs = []

    for p in root.find(q("body")).iter(q("p")):
        text = paragraph_text(p).strip()
        prefix = list_prefix(p)

        # Images can be in paragraphs with or without text.
        imgs = image_references_in_paragraph(p, rels)
        for filename in imgs:
            image_refs.append(filename)
            lines.append(f"\n![{filename}](assets/{filename})\n")

        if text:
            lines.append(prefix + text)

    return "\n".join(lines), image_refs


def structure_runbook(raw_md):
    """Split the raw markdown into recognizable sections."""
    # Normalize excessive blank lines
    md = re.sub(r"\n{3,}", "\n\n", raw_md)

    section_titles = {
        "resultados de aprendizajes e indicadores de logro": "## Resultados de Aprendizajes e Indicadores de Logro",
        "descripción general actividad:": "## Descripción General de la Actividad",
        "descripción específica actividad:": "## Descripción Específica de la Actividad",
        "topología a configurar:": "## Topología a Configurar",
        "requerimientos:": "## Requerimientos",
        "preguntas:": "## Preguntas",
    }

    out_lines = []
    for line in md.splitlines():
        stripped = line.strip().lstrip("- ").strip()
        key = stripped.lower()
        if key in section_titles:
            out_lines.append("")
            out_lines.append(section_titles[key])
            # If the original line also carried content after the title, keep it.
            if stripped != line.strip().lstrip("- ").strip():
                out_lines.append(line)
        else:
            out_lines.append(line)

    return "\n".join(out_lines)


def main():
    with zipfile.ZipFile(DOCX, "r") as z:
        image_manifest = extract_images(z)
        rels = build_relationships(z)
        raw_md, image_refs = parse_document(z, rels)

    structured_md = structure_runbook(raw_md)

    header = """# Lab 3.3.2 — Implementación de Seguridad sobre Túneles

> Fuente: `3.3.2 Actividad Implementación de Seguridad sobre Tuneles.docx`  
> IULab import: `3.3.3 Laboratorio Implementación de Seguridad sobre Tuneles.gz` (tu parte)

## Datos de conexión (completar cuando entregues las IPs)

| Dispositivo | Rol | IP de gestión | Usuario | Contraseña | Método de acceso |
|-------------|-----|---------------|---------|------------|------------------|
|             |     |               |         |            |                  |
|             |     |               |         |            |                  |
|             |     |               |         |            |                  |
|             |     |               |         |            |                  |
|             |     |               |         |            |                  |

"""

    footer = """

## Inventario de imágenes extraídas

"""
    for img in sorted(image_manifest.values(), key=lambda x: x["file"]):
        footer += f"- `{img['file']}` — {img['bytes']} bytes\n"

    runbook_content = header + structured_md + footer
    RUNBOOK.write_text(runbook_content, encoding="utf-8")

    # Machine-readable manifest
    manifest_file = ASSETS / "manifest.json"
    manifest_file.write_text(
        json.dumps(
            {
                "source": DOCX.name,
                "images": [
                    {"file": v["file"], "bytes": v["bytes"]} for v in image_manifest.values()
                ],
                "image_refs_in_text": image_refs,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Runbook: {RUNBOOK}")
    print(f"Images: {len(image_manifest)}")
    for v in image_manifest.values():
        print(f"  - {v['file']}: {v['bytes']} bytes")


if __name__ == "__main__":
    main()
