# SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0
"""Build every publication PDF from its Markdown source (M6, decision D-002 toolchain).

pandoc (Markdown to Typst) then the `typst` Python package, as in `streak.report.build_pdf`,
with three additions: the PDF title is always set (document metadata), the intermediate
`.typ` file can be kept for page rendering, and `manuscript.tex` is regenerated from
`manuscript.md` (pandoc, not compiled locally).

Usage:
    .venv/bin/python scripts/build_pdfs.py [--keep-typ DIR] [--png DIR] [--ppi 60]

Outputs: research/paper/manuscript.pdf, research/paper/manuscript.tex,
research/paper/supplementary.pdf, research/paper/supplementary_tables.pdf and
research/experiments/EXP-00N/report.pdf. PDFs are written in place; nothing else changes.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANDOC = os.environ.get("STREAK_PANDOC", str(ROOT.parent / ".tools" / "pandoc"))
SPDX_TEX = "% SPDX-License-Identifier: LicenseRef-STREAK-NC-Research-1.0\n"
TEX_NOTE = "% Generated from manuscript.md by pandoc {v}; do not edit by hand.\n"

# (source, pdf title, landscape)
DOCS = [
    ("research/paper/manuscript.md", None, False),
    ("research/paper/supplementary.md", "STREAK supplementary material", False),
    ("research/paper/supplementary_tables.md", "STREAK supplementary tables (generated)", True),
    ("research/experiments/EXP-001/report.md", "STREAK EXP-001 report", False),
    ("research/experiments/EXP-002/report.md", "STREAK EXP-002 report", False),
    ("research/experiments/EXP-003/report.md", "STREAK EXP-003 report", False),
]

# Typst set rules added to every document: captions already carry their own label
# ("Figure 1.", "FIG-01a."), so Typst's automatic numbering is switched off; tables use
# slightly smaller text and break across pages.
HEADER = """#set text(hyphenate: true)
#set figure(numbering: none)
#show table: set text(size: 0.85em)
#show table: set par(justify: false)
#show raw: set text(size: 0.85em)
#show figure.where(kind: table): set block(breakable: true)
"""


def pandoc_version() -> str:
    out = subprocess.run([PANDOC, "--version"], capture_output=True, text=True, check=True).stdout
    return out.split()[1]


def to_typst(md: Path, typ: Path, title: str | None, landscape: bool) -> None:
    header = HEADER
    before = f'#set document(title: "{title}")\n' if title else ""
    if landscape:
        header += '#set page(flipped: true)\n'
    with tempfile.NamedTemporaryFile("w", suffix=".typ", delete=False) as h:
        h.write(header)
        hpath = h.name
    with tempfile.NamedTemporaryFile("w", suffix=".typ", delete=False) as b:
        b.write(before)
        bpath = b.name
    try:
        subprocess.run([PANDOC, md.name, "-s", "-t", "typst", "--wrap=none",
                        "-V", "mainfont=Libertinus Serif", "-V", "papersize=a4",
                        "-V", "fontsize=10pt", "-V", "margin.x=2cm", "-V", "margin.y=2cm",
                        "-H", hpath, "-B", bpath, "-o", str(typ)], cwd=md.parent, check=True)
    finally:
        os.unlink(hpath)
        os.unlink(bpath)


def compile_typ(typ: Path, pdf: Path, root: Path) -> None:
    import typst  # the shared tool environment provides it (D-002)

    typst.compile(str(typ), output=str(pdf), root=str(root))


def render_png(typ: Path, out_dir: Path, stem: str, root: Path, ppi: int) -> None:
    import typst

    out_dir.mkdir(parents=True, exist_ok=True)
    typst.compile(str(typ), output=str(out_dir / f"{stem}-{{p}}.png"), format="png", ppi=ppi, root=str(root))


def build_tex() -> Path:
    md = ROOT / "research/paper/manuscript.md"
    tex = md.with_suffix(".tex")
    # The LaTeX template prints a structured author (name and affiliation) as "true", so the
    # author line is passed as variables read from the front matter (owner, 2026-11-26, B3).
    front = md.read_text().split("\n---\n", 2)[1]
    name = re.search(r'^\s*- name: "(.*)"$', front, re.M).group(1)
    aff = re.search(r'^\s*affiliation: "(.*)"$', front, re.M).group(1)
    body = subprocess.run([PANDOC, md.name, "-s", "-t", "latex",
                           "-V", f"author={name}, {aff[0].lower() + aff[1:]}", "-V", f"author-meta={name}"],
                          cwd=md.parent, capture_output=True, text=True, check=True).stdout
    tex.write_text(SPDX_TEX + TEX_NOTE.format(v=pandoc_version()) + body)
    return tex


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--keep-typ", type=Path, help="copy intermediate .typ files here")
    ap.add_argument("--png", type=Path, help="render every page to PNG here")
    ap.add_argument("--ppi", type=int, default=60)
    args = ap.parse_args(argv)

    print(f"tex: {build_tex().relative_to(ROOT)}")
    for rel, title, landscape in DOCS:
        md = ROOT / rel
        typ = md.with_suffix(".typ")
        pdf = md.with_suffix(".pdf")
        to_typst(md, typ, title, landscape)
        try:
            compile_typ(typ, pdf, ROOT)
            stem = re.sub(r"[^A-Za-z0-9]+", "-", str(Path(rel).with_suffix(""))).strip("-")
            if args.png:
                render_png(typ, args.png, stem, ROOT, args.ppi)
            if args.keep_typ:
                args.keep_typ.mkdir(parents=True, exist_ok=True)
                shutil.copy(typ, args.keep_typ / f"{stem}.typ")
        finally:
            typ.unlink()
        print(f"pdf: {pdf.relative_to(ROOT)} ({pdf.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
