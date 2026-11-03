#!/usr/bin/env python3
"""Extract the PDFs of a source to extracted/<access>/<id>.md with docling.

Finds the source by id through its manifest in sources/ (never by listing
raw/), checks every file path with wikipaths, runs tools/check_raw.sh, then
converts each PDF listed under `files:` and writes one markdown file with a
`<!-- p.N -->` marker before each page. N is the 1-based page of the PDF
file, not the number printed on the page.

Docling runs offline: HF_HUB_OFFLINE is set, so the layout models must
already be on this machine. A person downloads them once with
`docling-tools models download`; this script never does.

Refuses to overwrite an existing extracted file unless --force is given.

--force-ocr ignores the PDF's text layer and OCRs every page with RapidOCR.
Use it when the text layer is unusable (e.g. a broken font encoding that
extracts as symbols). The OCR models must also already be on this machine.

Usage:
  python tools/extract_pdf.py <source-id> [--include-internal] [--force] [--force-ocr]
"""

import argparse
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wikipaths  # noqa: E402

REPO = wikipaths.TOOLS_DIR.parent


def find_manifest(source_id, allowed):
    for path, access, err in wikipaths.iter_manifests(REPO, allowed):
        if err is None and path.parent.name == source_id:
            return path, access
    return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source_id")
    ap.add_argument("--include-internal", action="store_true",
                    help="allow sources/internal/ (only after group-lead approval)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing extracted file")
    ap.add_argument("--force-ocr", action="store_true",
                    help="OCR every page instead of using the PDF text layer")
    args = ap.parse_args()

    allowed = wikipaths.allowed_roots(args.include_internal)
    manifest_path, access = find_manifest(args.source_id, allowed)
    if manifest_path is None:
        print(f"no manifest for '{args.source_id}' under sources/{{{','.join(allowed)}}}/", file=sys.stderr)
        return 1

    with open(manifest_path, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    pdfs = []
    for entry in manifest.get("files") or []:
        rel = entry.get("path", "")
        err = wikipaths.check_rel_path(rel, (access,))
        if err:
            print(f"{manifest_path}: {rel}: {err}", file=sys.stderr)
            return 1
        if rel.lower().endswith(".pdf"):
            pdfs.append(rel)
    if not pdfs:
        print(f"{manifest_path}: no PDF listed under files:", file=sys.stderr)
        return 1

    out = REPO / "extracted" / access / f"{args.source_id}.md"
    if out.exists() and not args.force:
        print(f"{out.relative_to(REPO)} exists; use --force to overwrite", file=sys.stderr)
        return 1

    if not wikipaths.run_check_raw():
        return 1
    for rel in pdfs:
        link = wikipaths.symlink_in_path(wikipaths.RAW_DIR, rel)
        if link:
            print(f"{link} is a symlink; not followed", file=sys.stderr)
            return 1
        if not (wikipaths.RAW_DIR / rel).is_file():
            print(f"raw/{rel} not found", file=sys.stderr)
            return 1

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    try:
        from docling.document_converter import DocumentConverter
    except ImportError:
        print("docling is not installed: pip install docling", file=sys.stderr)
        return 1

    if args.force_ocr:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
        from docling.document_converter import PdfFormatOption

        opts = PdfPipelineOptions(do_ocr=True, ocr_options=RapidOcrOptions(force_full_page_ocr=True))
        converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
    else:
        converter = DocumentConverter()
    parts = [f"<!-- source: {args.source_id} | extracted with docling -->\n"]
    empty = []
    for rel in pdfs:
        doc = converter.convert(str(wikipaths.RAW_DIR / rel)).document
        if len(pdfs) > 1:
            parts.append(f"\n<!-- file: {rel} -->\n")
        for page_no in sorted(doc.pages):
            text = doc.export_to_markdown(page_no=page_no).strip()
            if not text:
                empty.append(f"{rel} p.{page_no}")
            parts.append(f"\n<!-- p.{page_no} -->\n\n")
            parts.append(text + "\n")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {out.relative_to(REPO)}")
    if empty:
        print(f"no text on {len(empty)} page(s): {', '.join(empty)}", file=sys.stderr)
    print(f"set derived.extracted: extracted/{access}/{args.source_id}.md in {manifest_path.relative_to(REPO)} if missing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
