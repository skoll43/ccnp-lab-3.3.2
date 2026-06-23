import fitz, os

pdf_path = r'C:\Users\CETECOM\ccnp-lab-3.3.2\lab16\Laboratorio N°16 Aplicación de una Red Corporativa Enterprise (1).pdf'
out_dir = r'C:\Users\CETECOM\ccnp-lab-3.3.2\lab16\assets'
os.makedirs(out_dir, exist_ok=True)

doc = fitz.open(pdf_path)
for i, page in enumerate(doc):
    print(f'=== Page {i+1} ===')
    blocks = page.get_text_blocks()
    for j, block in enumerate(blocks):
        t = block[4].replace('\n', '\\n')
        print(f'  Block {j}: ({block[0]:.0f},{block[1]:.0f},{block[2]:.0f},{block[3]:.0f}) type={block[6]}')
        print(f'    text={repr(t[:200])}')
    images = page.get_images(full=True)
    print(f'  Images: {len(images)}')
    for idx, img in enumerate(images):
        xref = img[0]
        base_image = doc.extract_image(xref)
        ext = base_image["ext"]
        w, h = base_image["width"], base_image["height"]
        size = len(base_image["image"])
        fname = f'page{i+1}_img{idx+1}.{ext}'
        fpath = os.path.join(out_dir, fname)
        with open(fpath, 'wb') as f:
            f.write(base_image["image"])
        print(f'    Saved {fname}: {w}x{h} {size} bytes')
    print()

doc.close()
print('Done.')
