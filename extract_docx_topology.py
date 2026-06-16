"""
Reusable DOCX topology extractor.

Usage:
    python extract_docx_topology.py <input.docx> [--out-dir <dir>] [--lab-id <id>]

Outputs:
    <out-dir>/lab-<id>-runbook.md
    <out-dir>/assets/
    <out-dir>/assets/manifest.json
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import json
import argparse

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def q(tag):
    return f"{{{W_NS}}}{tag}"


def extract_images(docx_zip, assets_dir):
    assets_dir.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name in docx_zip.namelist():
        if name.startswith("word/media/"):
            data = docx_zip.read(name)
            filename = Path(name).name
            (assets_dir / filename).write_bytes(data)
            manifest[name] = {"file": filename, "bytes": len(data)}
    return manifest


def build_relationships(docx_zip):
    rels = {}
    rel_path = "word/_rels/document.xml.rels"
    if rel_path in docx_zip.namelist():
        root = ET.fromstring(docx_zip.read(rel_path))
        for rel in root:
            rid = rel.get("Id")
            if rid:
                rels[rid] = {"target": rel.get("Target"), "type": rel.get("Type")}
    return rels


def paragraph_text(p_elem):
    return "".join(t.text or "" for t in p_elem.iter(q("t")))


def list_prefix(p_elem):
    return "- " if p_elem.find(f".//{q('numPr')}") is not None else ""


def image_references_in_paragraph(p_elem, rels):
    refs = []
    for drawing in p_elem.iter(q("drawing")):
        blip = drawing.find(f".//{{{A_NS}}}blip")
        if blip is not None:
            embed = blip.get(f"{{{REL_NS}}}embed")
            if embed and embed in rels:
                refs.append(Path(rels[embed]["target"]).name)
    return refs


def parse_document(docx_zip, rels):
    root = ET.fromstring(docx_zip.read("word/document.xml"))
    lines = []
    image_refs = []

    for p in root.find(q("body")).iter(q("p")):
        text = paragraph_text(p).strip()
        prefix = list_prefix(p)

        imgs = image_references_in_paragraph(p, rels)
        for filename in imgs:
            image_refs.append(filename)
            lines.append(f"\n![{filename}](assets/{filename})\n")

        if text:
            lines.append(prefix + text)

    return "\n".join(lines), image_refs


def structure_runbook(raw_md):
    md = re.sub(r"\n{3,}", "\n\n", raw_md)
    section_titles = {
        "resultados de aprendizajes e indicadores de logro": "## Resultados de Aprendizajes e Indicadores de Logro",
        "descripción general actividad:": "## Descripción General de la Actividad",
        "descripción específica actividad:": "## Descripción Específica de la Actividad",
        "topología a configurar:": "## Topología a Configurar",
        "requerimientos:": "## Requerimientos",
        "preguntas:": "## Preguntas",
    }
    out = []
    for line in md.splitlines():
        stripped = line.strip().lstrip("- ").strip().lower()
        if stripped in section_titles:
            out.append("")
            out.append(section_titles[stripped])
        else:
            out.append(line)
    return "\n".join(out)


def build_runbook(lab_id, source_name, structured_md, image_manifest, image_refs):
    header = f"""# Lab {lab_id}

> Fuente: `{source_name}`

## Datos de conexión

| Dispositivo | Rol | IP de gestión | Puerto | Usuario | Contraseña | Método de acceso |
|-------------|-----|---------------|--------|---------|------------|------------------|
|             |     |               |        |         |            |                  |

## Topología

"""
    footer = "\n\n## Inventario de imágenes extraídas\n\n"
    for img in sorted(image_manifest.values(), key=lambda x: x["file"]):
        footer += f"- `{img['file']}` — {img['bytes']} bytes\n"
    return header + structured_md + footer


def main():
    parser = argparse.ArgumentParser(description="Extract topology and text from a CCNP lab DOCX")
    parser.add_argument("docx", help="Input DOCX file")
    parser.add_argument("--out-dir", default=".", help="Output directory")
    parser.add_argument("--lab-id", default="lab", help="Lab identifier for filenames")
    args = parser.parse_args()

    docx_path = Path(args.docx)
    out_dir = Path(args.out_dir)
    assets_dir = out_dir / "assets"
    runbook_path = out_dir / f"lab-{args.lab_id}-runbook.md"

    with zipfile.ZipFile(docx_path, "r") as z:
        image_manifest = extract_images(z, assets_dir)
        rels = build_relationships(z)
        raw_md, image_refs = parse_document(z, rels)

    structured_md = structure_runbook(raw_md)
    runbook = build_runbook(args.lab_id, docx_path.name, structured_md, image_manifest, image_refs)
    runbook_path.write_text(runbook, encoding="utf-8")

    manifest_file = assets_dir / "manifest.json"
    manifest_file.write_text(
        json.dumps(
            {
                "source": docx_path.name,
                "images": [{"file": v["file"], "bytes": v["bytes"]} for v in image_manifest.values()],
                "image_refs_in_text": image_refs,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Runbook: {runbook_path}")
    print(f"Assets: {assets_dir}")
    print(f"Images: {len(image_manifest)}")
    for v in image_manifest.values():
        print(f"  - {v['file']}: {v['bytes']} bytes")


if __name__ == "__main__":
    main()
