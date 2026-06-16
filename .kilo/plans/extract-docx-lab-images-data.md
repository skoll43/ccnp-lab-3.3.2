# Plan: Extract Images and Data from the CCNP Lab DOCX

## Source
- **File:** `3.3.2 Actividad Implementación de Seguridad sobre Tuneles.docx`
- **Scope:** Extract text, images, and structured requirements for the lab.
- **Out of scope:** `3.3.3 ... .gz` is for IULab import.

## Goal
Produce a clean Markdown runbook plus an `assets/` folder of images that we can use once the device IPs/credentials are supplied.

## What the DOCX contains
- `word/document.xml` — main instructions, requirements, and questions.
- `word/media/image1.gif`, `image2.png`, `image3.png`, `image4.jpeg` — embedded images.
- `word/_rels/document.xml.rels` — relationship mapping for images.

## Extraction steps
1. Extract all media files to `assets/`.
2. Parse `word/document.xml` to Markdown, preserving paragraphs and numbering.
3. Build `lab-3.3.2-runbook.md` with metadata, topology, requirements, questions, and connection placeholders.
4. Validate that every image is referenced and no requirement is lost.

## Outputs
- `lab-3.3.2-runbook.md`
- `assets/image1.gif`, `image2.png`, `image3.png`, `image4.jpeg`

## Next action
Extract the DOCX now.
