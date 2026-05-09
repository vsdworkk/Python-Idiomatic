"""A small CLI for the ReportLab API reference and docs.reportlab.com."""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import os
import pkgutil
import re
import shutil
import subprocess
import sys
import textwrap
import webbrowser
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import reportlab

from . import __version__


DOCS_BASE_URL = "https://docs.reportlab.com"

DOC_TOPICS = {
    "home": (DOCS_BASE_URL + "/", "ReportLab documentation home"),
    "installation": (DOCS_BASE_URL + "/install/Installation/", "Install ReportLab"),
    "demos": (DOCS_BASE_URL + "/demos/", "Official demos"),
    "developer-faqs": (DOCS_BASE_URL + "/developerfaqs/", "Developer FAQs"),
    "rml-quickstart": (
        DOCS_BASE_URL + "/rmlfornewbies/",
        "ReportLab Markup Language quick start",
    ),
    "rml-tags": (
        DOCS_BASE_URL + "/tagref/",
        "RML tag reference index",
    ),
    "rml-samples": (DOCS_BASE_URL + "/rmlsamples/", "RML samples"),
    "user-guide": (
        DOCS_BASE_URL + "/reportlab/userguide/ch1_intro/",
        "ReportLab user guide introduction",
    ),
    "pdf-accessibility": (
        DOCS_BASE_URL + "/pdf-accessibility/",
        "PDF accessibility guidance",
    ),
}

SYMBOL_ALIASES = {
    "Canvas": "reportlab.pdfgen.canvas.Canvas",
    "canvas": "reportlab.pdfgen.canvas",
    "PDFPathObject": "reportlab.pdfgen.pathobject.PDFPathObject",
    "PDFTextObject": "reportlab.pdfgen.textobject.PDFTextObject",
    "BaseDocTemplate": "reportlab.platypus.doctemplate.BaseDocTemplate",
    "SimpleDocTemplate": "reportlab.platypus.doctemplate.SimpleDocTemplate",
    "Paragraph": "reportlab.platypus.paragraph.Paragraph",
    "Flowable": "reportlab.platypus.flowables.Flowable",
    "Image": "reportlab.platypus.flowables.Image",
    "Spacer": "reportlab.platypus.flowables.Spacer",
    "KeepTogether": "reportlab.platypus.flowables.KeepTogether",
    "Table": "reportlab.platypus.tables.Table",
    "TableStyle": "reportlab.platypus.tables.TableStyle",
    "TableOfContents": "reportlab.platypus.tableofcontents.TableOfContents",
    "Color": "reportlab.lib.colors.Color",
    "CMYKColor": "reportlab.lib.colors.CMYKColor",
    "ParagraphStyle": "reportlab.lib.styles.ParagraphStyle",
    "getSampleStyleSheet": "reportlab.lib.styles.getSampleStyleSheet",
    "pagesizes": "reportlab.lib.pagesizes",
    "colors": "reportlab.lib.colors",
    "units": "reportlab.lib.units",
}

SEED_SYMBOLS = tuple(sorted(set(SYMBOL_ALIASES.values()))) + (
    "reportlab.pdfgen.canvas.Canvas.drawString",
    "reportlab.pdfgen.canvas.Canvas.drawImage",
    "reportlab.pdfgen.canvas.Canvas.bookmarkPage",
    "reportlab.pdfgen.canvas.Canvas.addOutlineEntry",
    "reportlab.pdfgen.canvas.Canvas.save",
    "reportlab.platypus.SimpleDocTemplate",
    "reportlab.platypus.Paragraph",
    "reportlab.platypus.Table",
    "reportlab.platypus.TableStyle",
)


@dataclass(frozen=True)
class SearchHit:
    kind: str
    name: str
    summary: str
    source: str


@dataclass(frozen=True)
class TextLine:
    page: int
    text: str
    x0: float
    x1: float
    top: float
    bottom: float
    font: str
    size: float
    bold: bool


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except BrokenPipeError:
        return 1
    except ReportLabDocsCliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reportlab-docs",
        description="Explore ReportLab APIs, docs.reportlab.com links, and examples from the terminal.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    info_parser = subparsers.add_parser("info", help="Show installed ReportLab details.")
    add_json_flag(info_parser)
    info_parser.set_defaults(func=cmd_info)

    docs_parser = subparsers.add_parser("docs", help="Print official docs topic links.")
    docs_parser.add_argument("topic", nargs="?", help="Topic key, such as user-guide or rml-tags.")
    docs_parser.add_argument("--open", action="store_true", help="Open the selected topic in a browser.")
    add_json_flag(docs_parser)
    docs_parser.set_defaults(func=cmd_docs)

    modules_parser = subparsers.add_parser("modules", help="List installed ReportLab modules.")
    modules_parser.add_argument("--prefix", default="reportlab", help="Module prefix to list.")
    modules_parser.add_argument("--limit", type=int, default=80, help="Maximum modules to print.")
    add_json_flag(modules_parser)
    modules_parser.set_defaults(func=cmd_modules)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect a ReportLab symbol.")
    inspect_parser.add_argument("symbol", help="Dotted path or alias, such as Canvas or reportlab.pdfgen.canvas.Canvas.")
    inspect_parser.add_argument("--doc-lines", type=int, default=12, help="Number of docstring lines to show.")
    add_json_flag(inspect_parser)
    inspect_parser.set_defaults(func=cmd_inspect)

    search_parser = subparsers.add_parser("search", help="Search symbols, docs topics, and optionally a reference PDF.")
    search_parser.add_argument("query", help="Search text.")
    search_parser.add_argument("--pdf", type=Path, help="Optional ReportLab API reference PDF to search.")
    search_parser.add_argument("--limit", type=int, default=12, help="Maximum hits to print.")
    add_json_flag(search_parser)
    search_parser.set_defaults(func=cmd_search)

    examples_parser = subparsers.add_parser("example", help="Generate a runnable ReportLab example PDF.")
    examples_parser.add_argument("name", choices=("hello", "platypus", "table"), help="Example to generate.")
    examples_parser.add_argument("-o", "--output", type=Path, help="Output PDF path.")
    add_json_flag(examples_parser)
    examples_parser.set_defaults(func=cmd_example)

    critique_parser = subparsers.add_parser("critique", help="Critique PDF design consistency in detail.")
    critique_parser.add_argument("pdf", type=Path, help="PDF to inspect.")
    critique_parser.add_argument("--max-examples", type=int, default=8, help="Maximum examples per finding.")
    critique_parser.add_argument(
        "--standard",
        choices=("generic", "bain-editorial"),
        default="generic",
        help="Optional design standard to check in addition to the generic extraction critique.",
    )
    add_json_flag(critique_parser)
    critique_parser.set_defaults(func=cmd_critique)

    render_parser = subparsers.add_parser("render", help="Render selected PDF pages to PNG images for visual QA.")
    render_parser.add_argument("pdf", type=Path, help="PDF to render.")
    render_parser.add_argument(
        "--pages",
        default="1",
        help="Pages to render, such as 1, 2,5,8, or 2-4. Use 'all' for every page.",
    )
    render_parser.add_argument("-o", "--output-dir", type=Path, default=Path("pdf-renders"), help="Directory for PNG outputs.")
    render_parser.add_argument("--dpi", type=int, default=144, help="Render resolution in dots per inch.")
    render_parser.add_argument("--prefix", help="Output filename prefix. Defaults to the PDF stem.")
    add_json_flag(render_parser)
    render_parser.set_defaults(func=cmd_render)

    return parser


def add_json_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")


def cmd_info(args: argparse.Namespace) -> int:
    payload = {
        "cli_version": __version__,
        "reportlab_version": getattr(reportlab, "Version", "unknown"),
        "reportlab_file": getattr(reportlab, "__file__", None),
        "docs_base_url": DOCS_BASE_URL,
    }
    emit(payload, args.json)
    return 0


def cmd_docs(args: argparse.Namespace) -> int:
    if args.topic:
        if args.topic not in DOC_TOPICS:
            raise ReportLabDocsCliError(f"unknown docs topic {args.topic!r}; run `reportlab-docs docs` to list topics")
        url, description = DOC_TOPICS[args.topic]
        payload: Any = {"topic": args.topic, "url": url, "description": description}
        if args.open:
            webbrowser.open(url)
    else:
        payload = [
            {"topic": key, "url": url, "description": description}
            for key, (url, description) in DOC_TOPICS.items()
        ]
    emit(payload, args.json)
    return 0


def cmd_modules(args: argparse.Namespace) -> int:
    prefix = args.prefix.rstrip(".")
    try:
        package = importlib.import_module(prefix)
    except ImportError as exc:
        raise ReportLabDocsCliError(str(exc)) from exc
    if not hasattr(package, "__path__"):
        raise ReportLabDocsCliError(f"{prefix!r} is not a package")
    modules = [
        module.name
        for module in pkgutil.walk_packages(package.__path__, prefix + ".")
        if not is_private_module(module.name)
    ][: max(args.limit, 0)]
    emit(modules, args.json)
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    symbol = resolve_alias(args.symbol)
    obj = load_symbol(symbol)
    payload = describe_object(symbol, obj, args.doc_lines)
    emit(payload, args.json)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    hits = search_everything(args.query, pdf_path=args.pdf, limit=args.limit)
    if args.json:
        emit([asdict(hit) for hit in hits], True)
    else:
        if not hits:
            print("No hits.")
            return 1
        for hit in hits:
            print(f"{hit.kind}: {hit.name}")
            print(f"  {hit.summary}")
            print(f"  {hit.source}")
    return 0


def cmd_example(args: argparse.Namespace) -> int:
    output = args.output or Path.cwd() / f"reportlab-{args.name}-example.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    generators = {
        "hello": generate_hello_pdf,
        "platypus": generate_platypus_pdf,
        "table": generate_table_pdf,
    }
    generators[args.name](output)
    payload = {"example": args.name, "output": str(output), "bytes": output.stat().st_size}
    emit(payload, args.json)
    return 0


def cmd_critique(args: argparse.Namespace) -> int:
    payload = critique_pdf(args.pdf, max_examples=args.max_examples, standard=args.standard)
    emit(payload, args.json)
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    payload = render_pdf_pages(
        args.pdf,
        pages_spec=args.pages,
        output_dir=args.output_dir,
        dpi=args.dpi,
        prefix=args.prefix,
    )
    emit(payload, args.json)
    return 0


def resolve_alias(symbol: str) -> str:
    return SYMBOL_ALIASES.get(symbol, symbol)


def load_symbol(symbol: str) -> Any:
    parts = symbol.split(".")
    errors: list[str] = []
    for index in range(len(parts), 0, -1):
        module_name = ".".join(parts[:index])
        try:
            obj: Any = importlib.import_module(module_name)
        except ImportError as exc:
            errors.append(str(exc))
            continue
        for attr in parts[index:]:
            try:
                obj = getattr(obj, attr)
            except AttributeError as exc:
                raise ReportLabDocsCliError(f"{symbol!r} has no attribute {attr!r}") from exc
        return obj
    raise ReportLabDocsCliError(f"could not import {symbol!r}: {errors[-1] if errors else 'invalid symbol'}")


def describe_object(symbol: str, obj: Any, doc_lines: int = 12) -> dict[str, Any]:
    doc = inspect.getdoc(obj) or ""
    try:
        signature = str(inspect.signature(obj))
    except (TypeError, ValueError):
        signature = None
    public_members: list[str] = []
    if inspect.isclass(obj):
        public_members = [
            name
            for name, value in inspect.getmembers(obj)
            if not name.startswith("_") and (inspect.isfunction(value) or inspect.ismethoddescriptor(value))
        ][:80]
    return {
        "symbol": symbol,
        "kind": object_kind(obj),
        "signature": signature,
        "doc": trim_lines(doc, doc_lines),
        "members": public_members,
        "module": getattr(obj, "__module__", None),
    }


def search_everything(query: str, pdf_path: Path | None = None, limit: int = 12) -> list[SearchHit]:
    query_norm = query.lower()
    hits: list[SearchHit] = []
    for key, (url, description) in DOC_TOPICS.items():
        haystack = f"{key} {url} {description}".lower()
        if query_norm in haystack:
            hits.append(SearchHit("docs", key, description, url))
    for symbol in SEED_SYMBOLS:
        try:
            obj = load_symbol(symbol)
        except ReportLabDocsCliError:
            continue
        described = describe_object(symbol, obj, doc_lines=4)
        haystack = f"{symbol} {described['doc']} {' '.join(described['members'])}".lower()
        if query_norm in haystack:
            summary = described["doc"] or ", ".join(described["members"][:8]) or described["kind"]
            hits.append(SearchHit("symbol", symbol, compact(summary), "installed reportlab package"))
    if pdf_path is not None:
        hits.extend(search_reference_pdf(pdf_path, query, remaining=max(limit - len(hits), 0)))
    return hits[: max(limit, 0)]


def search_reference_pdf(pdf_path: Path, query: str, remaining: int) -> list[SearchHit]:
    if remaining <= 0:
        return []
    if not pdf_path.exists():
        raise ReportLabDocsCliError(f"PDF not found: {pdf_path}")
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ReportLabDocsCliError("PDF search requires pypdf; install with `python3 -m pip install pypdf`") from exc
    reader = PdfReader(str(pdf_path))
    query_norm = query.lower()
    hits: list[SearchHit] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        position = text.lower().find(query_norm)
        if position == -1:
            continue
        start = max(0, position - 160)
        end = min(len(text), position + len(query) + 240)
        snippet = compact(text[start:end])
        hits.append(SearchHit("pdf", f"page {index}", snippet, str(pdf_path)))
        if len(hits) >= remaining:
            break
    return hits


def render_pdf_pages(
    pdf_path: Path,
    pages_spec: str = "1",
    output_dir: Path = Path("pdf-renders"),
    dpi: int = 144,
    prefix: str | None = None,
) -> dict[str, Any]:
    if not pdf_path.exists():
        raise ReportLabDocsCliError(f"PDF not found: {pdf_path}")
    if dpi <= 0:
        raise ReportLabDocsCliError("--dpi must be greater than zero")

    page_count = get_pdf_page_count(pdf_path)
    pages = parse_page_selection(pages_spec, page_count)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_prefix = prefix or pdf_path.stem

    try:
        outputs = render_with_pymupdf(pdf_path, pages, output_dir, dpi, output_prefix)
        backend = "pymupdf"
    except ImportError:
        if shutil.which("pdftoppm"):
            outputs = render_with_pdftoppm(pdf_path, pages, output_dir, dpi, output_prefix)
            backend = "pdftoppm"
        else:
            raise ReportLabDocsCliError(
                "PDF rendering requires PyMuPDF (`python3 -m pip install pymupdf`) "
                "or Poppler's `pdftoppm` on PATH."
            )

    return {
        "pdf": str(pdf_path),
        "pages": pages,
        "page_count": page_count,
        "dpi": dpi,
        "backend": backend,
        "outputs": [str(path) for path in outputs],
    }


def get_pdf_page_count(pdf_path: Path) -> int:
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            import fitz  # type: ignore
        except ImportError as exc:
            raise ReportLabDocsCliError(
                "Counting pages requires pypdf or PyMuPDF; install with `python3 -m pip install pypdf pymupdf`."
            ) from exc
        with fitz.open(str(pdf_path)) as document:
            return int(document.page_count)
    reader = PdfReader(str(pdf_path))
    return len(reader.pages)


def parse_page_selection(pages_spec: str, page_count: int) -> list[int]:
    spec = pages_spec.strip().lower()
    if not spec:
        raise ReportLabDocsCliError("--pages cannot be empty")
    if spec == "all":
        return list(range(1, page_count + 1))

    pages: set[int] = set()
    for part in spec.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            if not start_text.isdigit() or not end_text.isdigit():
                raise ReportLabDocsCliError(f"invalid page range: {token!r}")
            start, end = int(start_text), int(end_text)
            if start > end:
                raise ReportLabDocsCliError(f"invalid descending page range: {token!r}")
            pages.update(range(start, end + 1))
        elif token.isdigit():
            pages.add(int(token))
        else:
            raise ReportLabDocsCliError(f"invalid page selection token: {token!r}")

    selected = sorted(pages)
    if not selected:
        raise ReportLabDocsCliError("no pages selected")
    out_of_bounds = [page for page in selected if page < 1 or page > page_count]
    if out_of_bounds:
        raise ReportLabDocsCliError(f"page(s) outside 1-{page_count}: {out_of_bounds}")
    return selected


def render_with_pymupdf(
    pdf_path: Path,
    pages: list[int],
    output_dir: Path,
    dpi: int,
    prefix: str,
) -> list[Path]:
    import fitz  # type: ignore

    outputs: list[Path] = []
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    with fitz.open(str(pdf_path)) as document:
        for page_number in pages:
            page = document.load_page(page_number - 1)
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            output = output_dir / f"{prefix}-page-{page_number:03d}.png"
            pixmap.save(str(output))
            outputs.append(output)
    return outputs


def render_with_pdftoppm(
    pdf_path: Path,
    pages: list[int],
    output_dir: Path,
    dpi: int,
    prefix: str,
) -> list[Path]:
    outputs: list[Path] = []
    for page_number in pages:
        output_prefix = output_dir / f"{prefix}-page-{page_number:03d}"
        command = [
            "pdftoppm",
            "-png",
            "-r",
            str(dpi),
            "-f",
            str(page_number),
            "-l",
            str(page_number),
            str(pdf_path),
            str(output_prefix),
        ]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        if completed.returncode:
            raise ReportLabDocsCliError(compact(completed.stderr) or "pdftoppm failed")
        candidates = sorted(output_dir.glob(f"{output_prefix.name}-*.png"))
        if not candidates:
            raise ReportLabDocsCliError(f"pdftoppm did not create a PNG for page {page_number}")
        rendered = candidates[-1]
        final_output = output_dir / f"{prefix}-page-{page_number:03d}.png"
        if rendered != final_output:
            rendered.replace(final_output)
        outputs.append(final_output)
    return outputs


def critique_pdf(pdf_path: Path, max_examples: int = 8, standard: str = "generic") -> dict[str, Any]:
    if not pdf_path.exists():
        raise ReportLabDocsCliError(f"PDF not found: {pdf_path}")
    try:
        import pdfplumber
    except ImportError as exc:
        raise ReportLabDocsCliError(
            "PDF critique requires pdfplumber; install with `python3 -m pip install -e \".[pdf]\"`"
        ) from exc

    pages: list[dict[str, Any]] = []
    all_lines: list[TextLine] = []
    table_findings: list[dict[str, Any]] = []
    legend_candidates: list[dict[str, Any]] = []
    font_counts: dict[str, int] = {}
    size_counts: dict[str, int] = {}

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(extra_attrs=["fontname", "size"])
            lines = group_words_into_lines(words, page_number)
            all_lines.extend(lines)
            for line in lines:
                font_counts[line.font] = font_counts.get(line.font, 0) + 1
                size_key = format_size(line.size)
                size_counts[size_key] = size_counts.get(size_key, 0) + 1
                if looks_like_legend_or_caption(line.text):
                    legend_candidates.append(line_to_payload(line))
            page_tables = inspect_page_tables(page, page_number, lines, max_examples)
            table_findings.extend(page_tables)
            pages.append(
                {
                    "page": page_number,
                    "text_lines": len(lines),
                    "tables_detected": len(page_tables),
                    "graphic_objects": len(page.lines) + len(page.rects) + len(page.curves) + len(page.images),
                    "dominant_text_styles": most_common_line_styles(lines, limit=5),
                }
            )

    hierarchy = summarize_hierarchy(all_lines)
    findings = build_design_findings(
        hierarchy=hierarchy,
        tables=table_findings,
        legends=legend_candidates,
        font_counts=font_counts,
        max_examples=max_examples,
    )
    standards: dict[str, Any] = {}
    if standard == "bain-editorial":
        standards["bain_editorial"] = analyze_bain_editorial_standard(
            lines=all_lines,
            page_summaries=pages,
            max_examples=max_examples,
        )
        findings.extend(standards["bain_editorial"]["findings"])
    return {
        "pdf": str(pdf_path),
        "pages": len(pages),
        "standard": standard,
        "summary": {
            "fonts": sorted(font_counts.items(), key=lambda item: (-item[1], item[0])),
            "font_sizes": sorted(size_counts.items(), key=lambda item: (-item[1], item[0])),
            "detected_tables": len(table_findings),
            "legend_or_caption_candidates": len(legend_candidates),
        },
        "hierarchy": hierarchy,
        "tables": table_findings[:max_examples],
        "legends_and_captions": legend_candidates[:max_examples],
        "page_summaries": pages,
        "standards": standards,
        "findings": findings,
    }


def group_words_into_lines(words: list[dict[str, Any]], page_number: int, tolerance: float = 3.0) -> list[TextLine]:
    rows: list[list[dict[str, Any]]] = []
    for word in sorted(words, key=lambda item: (float(item["top"]), float(item["x0"]))):
        for row in rows:
            if abs(float(row[0]["top"]) - float(word["top"])) <= tolerance:
                row.append(word)
                break
        else:
            rows.append([word])
    lines: list[TextLine] = []
    for row in rows:
        row.sort(key=lambda item: float(item["x0"]))
        text = " ".join(str(word["text"]) for word in row).strip()
        if not text:
            continue
        fonts = [str(word.get("fontname") or "unknown") for word in row]
        sizes = [float(word.get("size") or 0) for word in row]
        font = most_common(fonts)
        size = round(sum(sizes) / len(sizes), 2) if sizes else 0.0
        lines.append(
            TextLine(
                page=page_number,
                text=text,
                x0=min(float(word["x0"]) for word in row),
                x1=max(float(word["x1"]) for word in row),
                top=min(float(word["top"]) for word in row),
                bottom=max(float(word["bottom"]) for word in row),
                font=font,
                size=size,
                bold=is_bold_font(font),
            )
        )
    return lines


def inspect_page_tables(page: Any, page_number: int, lines: list[TextLine], max_examples: int) -> list[dict[str, Any]]:
    tables: list[dict[str, Any]] = []
    try:
        found_tables = page.find_tables()
    except Exception:
        found_tables = []
    for index, table in enumerate(found_tables, start=1):
        x0, top, x1, bottom = [float(value) for value in table.bbox]
        rows_extracted = safe_table_row_count(table)
        page_area = float(page.width) * float(page.height)
        table_area = max(0.0, x1 - x0) * max(0.0, bottom - top)
        table_lines = [
            line
            for line in lines
            if line.x1 >= x0 - 2 and line.x0 <= x1 + 2 and line.top >= top - 2 and line.bottom <= bottom + 2
        ]
        if not table_lines:
            continue
        if (rows_extracted or 0) < 3 and any(line.size >= 16 for line in table_lines):
            continue
        detected_header_lines = [
            line for line in table_lines if line.bold and looks_like_table_header(line.text)
        ]
        header = min(detected_header_lines or table_lines, key=lambda line: line.top)
        if table_area > page_area * 0.65:
            continue
        if (rows_extracted or 0) < 3 and not looks_like_table_header(header.text):
            continue
        body_lines = [line for line in table_lines if line.top > header.top + 2]
        title = nearest_title_above(lines, top, x0, x1)
        body_styles = sorted({style_key(line) for line in body_lines})
        tables.append(
            {
                "page": page_number,
                "index": index,
                "bbox": [round(x0, 2), round(top, 2), round(x1, 2), round(bottom, 2)],
                "rows_extracted": rows_extracted,
                "title_above": line_to_payload(title) if title else None,
                "header": line_to_payload(header),
                "header_is_bold": header.bold,
                "body_style_variants": body_styles[:max_examples],
                "body_uses_bold": any(line.bold for line in body_lines),
                "sample_body_lines": [line_to_payload(line) for line in body_lines[: min(3, max_examples)]],
            }
        )
    return tables


def nearest_title_above(lines: list[TextLine], table_top: float, x0: float, x1: float) -> TextLine | None:
    candidates = [
        line
        for line in lines
        if line.bottom <= table_top and table_top - line.bottom <= 80 and line.x1 >= x0 - 20 and line.x0 <= x1 + 20
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda line: (table_top - line.bottom, -line.size))[0]


def summarize_hierarchy(lines: list[TextLine]) -> dict[str, Any]:
    size_groups: dict[str, list[TextLine]] = {}
    for line in lines:
        size_groups.setdefault(format_size(line.size), []).append(line)
    levels = []
    for size, grouped_lines in sorted(size_groups.items(), key=lambda item: -float(item[0])):
        fonts = sorted({line.font for line in grouped_lines})
        levels.append(
            {
                "size": size,
                "count": len(grouped_lines),
                "fonts": fonts,
                "bold_count": sum(1 for line in grouped_lines if line.bold),
                "examples": [line_to_payload(line) for line in grouped_lines[:3]],
            }
        )
    return {"levels": levels[:10]}


def build_design_findings(
    hierarchy: dict[str, Any],
    tables: list[dict[str, Any]],
    legends: list[dict[str, Any]],
    font_counts: dict[str, int],
    max_examples: int,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if len(font_counts) > 3:
        findings.append(
            {
                "severity": "medium",
                "area": "font-system",
                "message": "The document uses more than three font faces; check whether this is intentional or inherited from mixed styles.",
                "evidence": sorted(font_counts.items(), key=lambda item: (-item[1], item[0]))[:max_examples],
            }
        )
    if len(hierarchy["levels"]) > 6:
        findings.append(
            {
                "severity": "medium",
                "area": "hierarchy",
                "message": "There are many distinct text sizes; verify heading, body, caption, and table styles are intentionally separated.",
                "evidence": hierarchy["levels"][:max_examples],
            }
        )
    if tables:
        header_styles = sorted({style_key_from_payload(table["header"]) for table in tables})
        body_style_sets = sorted({tuple(table["body_style_variants"]) for table in tables})
        non_bold_headers = [table for table in tables if not table["header_is_bold"]]
        missing_titles = [table for table in tables if not table["title_above"]]
        if len(header_styles) > 1:
            findings.append(
                {
                    "severity": "high",
                    "area": "tables",
                    "message": "Detected table headers do not share one consistent font/size/bold treatment.",
                    "evidence": header_styles[:max_examples],
                }
            )
        if len(body_style_sets) > 2 and not expected_table_body_variation(tables):
            findings.append(
                {
                    "severity": "medium",
                    "area": "tables",
                    "message": "Detected table body styles vary across tables.",
                    "evidence": [list(styles) for styles in body_style_sets[:max_examples]],
                }
            )
        if non_bold_headers:
            findings.append(
                {
                    "severity": "high",
                    "area": "tables",
                    "message": "Some detected table headers are not bold.",
                    "evidence": compact_table_refs(non_bold_headers, max_examples),
                }
            )
        if missing_titles:
            findings.append(
                {
                    "severity": "medium",
                    "area": "tables",
                    "message": "Some detected tables do not have a nearby title directly above them.",
                    "evidence": compact_table_refs(missing_titles, max_examples),
                }
            )
    if legends:
        legend_styles = sorted({style_key_from_payload(legend) for legend in legends})
        if len(legend_styles) > 1:
            findings.append(
                {
                    "severity": "medium",
                    "area": "legends-captions",
                    "message": "Legend/caption-like text uses multiple font treatments.",
                    "evidence": legend_styles[:max_examples],
                }
            )
    return findings


def analyze_bain_editorial_standard(
    lines: list[TextLine],
    page_summaries: list[dict[str, Any]],
    max_examples: int,
) -> dict[str, Any]:
    """Check report layout against a Bain-style editorial figure standard."""
    lines_by_page: dict[int, list[TextLine]] = {}
    for line in lines:
        lines_by_page.setdefault(line.page, []).append(line)
    for page_lines in lines_by_page.values():
        page_lines.sort(key=lambda line: (line.top, line.x0))

    figure_labels = [line for line in lines if looks_like_figure_label(line.text)]
    note_lines = [line for line in lines if looks_like_note_or_source(line.text)]
    visual_pages = [
        page
        for page in page_summaries
        if page.get("graphic_objects", 0) >= 8 or page.get("tables_detected", 0) > 0
    ]

    figure_label_gaps = [
        gap_before_line(line, lines_by_page.get(line.page, []))
        for line in figure_labels
    ]
    figure_label_gaps = [gap for gap in figure_label_gaps if gap is not None]
    body_gaps = estimate_body_paragraph_gaps(lines_by_page)

    findings: list[dict[str, Any]] = []
    if visual_pages and not figure_labels:
        findings.append(
            {
                "severity": "high",
                "area": "bain-editorial.figure-labels",
                "message": "Visual pages are present, but no Bain-style `Figure N:` labels were found above exhibits.",
                "evidence": visual_pages[:max_examples],
            }
        )
    if figure_labels:
        x_positions = [round(line.x0, 1) for line in figure_labels]
        if max(x_positions) - min(x_positions) > 8:
            findings.append(
                {
                    "severity": "medium",
                    "area": "bain-editorial.figure-labels",
                    "message": "Figure labels are not aligned to a consistent indent.",
                    "evidence": [line_to_payload(line) for line in figure_labels[:max_examples]],
                }
            )
        tight_figure_gaps = [
            {"figure": line_to_payload(line), "gap_before": round(gap, 1)}
            for line, gap in zip(figure_labels, figure_label_gaps)
            if gap < 24
        ]
        if tight_figure_gaps:
            findings.append(
                {
                    "severity": "medium",
                    "area": "bain-editorial.spacing",
                    "message": "Some figures do not have enough arrival space above the figure label; Bain-style figures usually use roughly 33-50 pt after preceding prose.",
                    "evidence": tight_figure_gaps[:max_examples],
                }
            )
    if note_lines:
        note_style_variants = sorted({style_key(line) for line in note_lines})
        italic_notes = [line for line in note_lines if "italic" in line.font.lower() or "oblique" in line.font.lower()]
        large_notes = [line for line in note_lines if line.size > 8.1]
        if italic_notes or large_notes:
            findings.append(
                {
                    "severity": "medium",
                    "area": "bain-editorial.notes",
                    "message": "Notes/source text differs from the Bain-style convention of small regular gray sans text, usually around 7 pt and not italic.",
                    "evidence": [line_to_payload(line) for line in (italic_notes or large_notes)[:max_examples]],
                }
            )
    elif visual_pages:
        findings.append(
            {
                "severity": "medium",
                "area": "bain-editorial.notes",
                "message": "Visual pages were detected, but no note/source lines were found below exhibits.",
                "evidence": visual_pages[:max_examples],
            }
        )

    return {
        "profile": {
            "name": "bain-editorial",
            "source": "Bain-style editorial report conventions",
            "body_paragraph_gap_target_pt": "about 14",
            "pre_figure_gap_target_pt": "about 33-50",
            "figure_label_pattern": "Figure N: title above visual",
            "figure_label_indent_target_pt": "about 118 on US Letter when body starts around 72",
            "note_style_target": "small regular gray sans, about 7 pt, below visual",
        },
        "metrics": {
            "figure_label_count": len(figure_labels),
            "visual_page_count": len(visual_pages),
            "note_or_source_count": len(note_lines),
            "body_paragraph_gap_median_pt": median_or_none(body_gaps),
            "figure_label_gap_median_pt": median_or_none(figure_label_gaps),
            "figure_label_x_positions": sorted({round(line.x0, 1) for line in figure_labels}),
            "note_style_variants": sorted({style_key(line) for line in note_lines}),
        },
        "findings": findings,
    }


def generate_hello_pdf(output: Path) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas

    pdf = canvas.Canvas(str(output), pagesize=letter)
    pdf.setTitle("ReportLab hello example")
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(inch, 10 * inch, "Hello from ReportLab")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(inch, 9.55 * inch, "Generated by reportlab-docs example hello.")
    pdf.setStrokeColorRGB(0.15, 0.35, 0.55)
    pdf.setFillColorRGB(0.88, 0.94, 0.98)
    pdf.roundRect(inch, 8.35 * inch, 4.2 * inch, 0.55 * inch, 8, stroke=1, fill=1)
    pdf.setFillColorRGB(0.05, 0.08, 0.12)
    pdf.drawString(1.2 * inch, 8.55 * inch, "Canvas draws text, paths, images, and links.")
    pdf.showPage()
    pdf.save()


def generate_platypus_pdf(output: Path) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    styles = getSampleStyleSheet()
    story = [
        Paragraph("ReportLab Platypus Example", styles["Title"]),
        Spacer(1, 12),
        Paragraph(
            "Platypus builds multi-page documents from flowables such as paragraphs, tables, images, and page breaks.",
            styles["BodyText"],
        ),
    ]
    SimpleDocTemplate(str(output), pagesize=letter).build(story)


def generate_table_pdf(output: Path) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    styles = getSampleStyleSheet()
    data = [
        ["Area", "API", "Use"],
        ["Low-level drawing", "pdfgen.canvas.Canvas", "Precise page operations"],
        ["Document layout", "platypus", "Stories, flowables, templates"],
        ["Shared helpers", "reportlab.lib", "Colors, units, pagesizes, styles"],
    ]
    table = Table(data, hAlign="LEFT", colWidths=[110, 165, 210])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#153243")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#A7B4BD")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF4F7")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story = [
        Paragraph("ReportLab Table Example", styles["Title"]),
        Spacer(1, 12),
        table,
    ]
    SimpleDocTemplate(str(output), pagesize=letter).build(story)


def emit(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                print(format_dict_line(item))
            else:
                print(item)
    elif isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, list):
                print(f"{key}:")
                for item in value:
                    print(f"  - {item}")
            elif value:
                print(f"{key}: {value}")
    else:
        print(payload)


def format_dict_line(item: dict[str, Any]) -> str:
    if {"topic", "url", "description"}.issubset(item):
        return f"{item['topic']}: {item['description']} ({item['url']})"
    return " ".join(f"{key}={value}" for key, value in item.items())


def is_private_module(module_name: str) -> bool:
    return any(part.startswith("_") for part in module_name.split("."))


def object_kind(obj: Any) -> str:
    if inspect.ismodule(obj):
        return "module"
    if inspect.isclass(obj):
        return "class"
    if inspect.isfunction(obj) or inspect.ismethod(obj):
        return "function"
    return type(obj).__name__


def trim_lines(text: str, max_lines: int) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines[: max(max_lines, 0)]).strip()


def compact(text: str, width: int = 180) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    return textwrap.shorten(normalized, width=width, placeholder="...")


def line_to_payload(line: TextLine | None) -> dict[str, Any] | None:
    if line is None:
        return None
    return {
        "page": line.page,
        "text": compact(line.text, width=140),
        "x0": round(line.x0, 2),
        "x1": round(line.x1, 2),
        "top": round(line.top, 2),
        "bottom": round(line.bottom, 2),
        "font": line.font,
        "size": format_size(line.size),
        "bold": line.bold,
    }


def style_key(line: TextLine) -> str:
    return f"{line.font}|{format_size(line.size)}|{'bold' if line.bold else 'regular'}"


def style_key_from_payload(payload: dict[str, Any]) -> str:
    return f"{payload.get('font')}|{payload.get('size')}|{'bold' if payload.get('bold') else 'regular'}"


def format_size(size: float) -> str:
    return f"{float(size):.1f}"


def is_bold_font(font: str) -> bool:
    return any(token in font.lower() for token in ("bold", "black", "heavy", "semibold", "demi"))


def most_common(values: Iterable[str]) -> str:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    if not counts:
        return "unknown"
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def most_common_line_styles(lines: list[TextLine], limit: int) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    examples: dict[str, TextLine] = {}
    for line in lines:
        key = style_key(line)
        counts[key] = counts.get(key, 0) + 1
        examples.setdefault(key, line)
    return [
        {"style": key, "count": count, "example": line_to_payload(examples[key])}
        for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def looks_like_legend_or_caption(text: str) -> bool:
    normalized = text.strip().lower()
    if re.match(r"^(figure|fig\.|chart|table|source|note|legend)\b", normalized):
        return True
    return " legend" in normalized or " source:" in normalized or " note:" in normalized


def looks_like_figure_label(text: str) -> bool:
    return bool(re.match(r"^figure\s+\d+[a-z]?\s*:", text.strip(), flags=re.IGNORECASE))


def looks_like_note_or_source(text: str) -> bool:
    return bool(re.match(r"^(notes?|source)\s*:", text.strip(), flags=re.IGNORECASE))


def looks_like_table_header(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    header_starts = (
        "area",
        "category",
        "group",
        "measure",
        "metric",
        "segment",
        "tool",
    )
    return normalized.startswith(header_starts)


def safe_table_row_count(table: Any) -> int | None:
    try:
        extracted = table.extract()
    except Exception:
        return None
    return len(extracted or [])


def gap_before_line(line: TextLine, page_lines: list[TextLine]) -> float | None:
    previous = [
        candidate
        for candidate in page_lines
        if candidate.bottom <= line.top and candidate.text != line.text
    ]
    if not previous:
        return None
    nearest = max(previous, key=lambda candidate: candidate.bottom)
    return line.top - nearest.bottom


def estimate_body_paragraph_gaps(lines_by_page: dict[int, list[TextLine]]) -> list[float]:
    gaps: list[float] = []
    for page_lines in lines_by_page.values():
        body_lines = [
            line
            for line in page_lines
            if 8.5 <= line.size <= 11.5
            and not line.bold
            and not looks_like_figure_label(line.text)
            and not looks_like_note_or_source(line.text)
            and not looks_like_legend_or_caption(line.text)
        ]
        body_lines.sort(key=lambda line: (line.top, line.x0))
        for previous, current in zip(body_lines, body_lines[1:]):
            if abs(previous.x0 - current.x0) > 8:
                continue
            gap = current.top - previous.bottom
            if 5 <= gap <= 28:
                gaps.append(gap)
    return gaps


def median_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return round(ordered[mid], 1)
    return round((ordered[mid - 1] + ordered[mid]) / 2, 1)


def expected_table_body_variation(tables: list[dict[str, Any]]) -> bool:
    """Allow small extraction-level variance from mixed label/value table rows."""
    allowed_fonts = {"Helvetica", "Helvetica-Bold"}
    for table in tables:
        for style in table["body_style_variants"]:
            font, size_text, weight = style.split("|", 2)
            size = float(size_text)
            if font not in allowed_fonts:
                return False
            if weight == "regular" and 7.8 <= size <= 8.3:
                continue
            if weight == "bold" and abs(size - 6.5) <= 0.05:
                continue
            return False
    return True


def compact_table_refs(tables: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return [
        {
            "page": table["page"],
            "index": table["index"],
            "header": table["header"],
            "title_above": table["title_above"],
        }
        for table in tables[:limit]
    ]


class ReportLabDocsCliError(Exception):
    """Expected CLI failure with a user-facing message."""
