"""
folder_pipeline v0 — watch-style batch: inbox → sqlite/csv → resume by hash.

Client-safe: stdlib only. No JoeysAI imports when run as standalone copy.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "0.2.1"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            hash TEXT PRIMARY KEY,
            path TEXT,
            status TEXT,
            processed_at TEXT,
            note TEXT
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS rows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT,
            vendor TEXT,
            invoice_no TEXT,
            amount TEXT,
            raw_line TEXT,
            created_at TEXT
        )
        """
    )
    con.commit()
    return con


def already_done(con: sqlite3.Connection, h: str) -> bool:
    row = con.execute(
        "SELECT status FROM files WHERE hash=? AND status='ok'", (h,)
    ).fetchone()
    return bool(row)


_HEADER_VENDOR = frozenset(
    {"vendor", "vendor name", "name", "company", "client", "payee"}
)
_HEADER_INVOICE = frozenset(
    {"invoice", "invoice_no", "invoice no", "inv", "invoice#", "inv_no", "number"}
)
_HEADER_AMOUNT = frozenset(
    {"amount", "total", "amt", "price", "sum", "value", "usd"}
)


def _is_header_row(parts: List[str]) -> bool:
    if len(parts) < 2:
        return False
    cells = [p.strip().lower().lstrip("\ufeff") for p in parts[:4]]
    if not cells:
        return False
    # classic vendor,invoice,amount
    if cells[0] in _HEADER_VENDOR:
        return True
    # any two of header-ish tokens in first three cells
    hits = 0
    for c in cells[:3]:
        if c in _HEADER_VENDOR or c in _HEADER_INVOICE or c in _HEADER_AMOUNT:
            hits += 1
    return hits >= 2


def _looks_like_amount(s: str) -> bool:
    s = (s or "").strip().replace("$", "").replace(",", "")
    if not s:
        return False
    return bool(re.match(r"^-?\d+(\.\d+)?$", s))


def _row_from_parts(parts: List[str], raw_line: str) -> Optional[Dict[str, str]]:
    """Map CSV cells → vendor/invoice/amount; skip headers and empty vendors."""
    if len(parts) < 3:
        return None
    cleaned = [p.strip().strip('"').strip("'") for p in parts]
    if _is_header_row(cleaned):
        return None
    vendor = cleaned[0][:120]
    invoice_no = cleaned[1][:80]
    amount = cleaned[2][:40]
    if not vendor:
        return None
    # skip pure noise: empty amount and empty invoice
    if not invoice_no and not amount:
        return None
    return {
        "vendor": vendor,
        "invoice_no": invoice_no,
        "amount": amount,
        "raw_line": raw_line[:400],
    }


def extract_csv_rows(text: str) -> List[Dict[str, str]]:
    """
    Proper CSV parse (quoted commas, headers, BOM).
    SKILL-A3b: do not use naive split(',') on invoice CSVs.
    """
    out: List[Dict[str, str]] = []
    # strip BOM for DictReader/reader
    raw = (text or "").lstrip("\ufeff")
    if not raw.strip():
        return out
    try:
        reader = csv.reader(raw.splitlines())
        for row in reader:
            if not row or all(not (c or "").strip() for c in row):
                continue
            raw_line = ",".join(row)[:400]
            parsed = _row_from_parts(row, raw_line)
            if parsed:
                out.append(parsed)
    except csv.Error:
        pass
    return out


def extract_from_text(text: str) -> List[Dict[str, str]]:
    """Extractor for CSV/text/PDF invoice-ish content."""
    out: List[Dict[str, str]] = []
    text = text or ""
    # Prefer full CSV parse when file looks tabular
    if "," in text and text.count("\n") >= 1:
        csv_rows = extract_csv_rows(text)
        if csv_rows:
            return csv_rows

    for line in text.splitlines():
        line = line.strip().lstrip("\ufeff")
        if not line or line.startswith("#"):
            continue
        # CSV-ish single line with possible quotes
        if "," in line:
            try:
                parts = next(csv.reader([line]))
            except csv.Error:
                parts = [p.strip() for p in line.split(",")]
            parsed = _row_from_parts(parts, line)
            if parsed:
                out.append(parsed)
                continue
        m = re.search(
            r"vendor\s*[:=]\s*(.+?)\s+invoice\s*[:=]\s*(\S+)\s+amount\s*[:=]\s*(\S+)",
            line,
            re.I,
        )
        if m:
            out.append(
                {
                    "vendor": m.group(1)[:120],
                    "invoice_no": m.group(2)[:80],
                    "amount": m.group(3)[:40],
                    "raw_line": line[:400],
                }
            )
    # whole-blob patterns (PDF text often one stream)
    if not out:
        for m in re.finditer(
            r"vendor\s*[:=]\s*([A-Za-z0-9 ._-]{2,80})\s+"
            r"invoice\s*[:=]\s*([A-Za-z0-9._-]{2,40})\s+"
            r"amount\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)",
            text,
            re.I,
        ):
            out.append(
                {
                    "vendor": m.group(1).strip()[:120],
                    "invoice_no": m.group(2).strip()[:80],
                    "amount": m.group(3).strip()[:40],
                    "raw_line": m.group(0)[:400],
                }
            )
    return out


def extract_pdf_text(path: Path) -> Tuple[str, str]:
    """
    PDF text: optional pypdf, else raw bytes decode (works for simple text PDFs).
    Returns (text, method).
    """
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        parts: List[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        text = "\n".join(parts).strip()
        if text:
            return text, "pypdf"
    except Exception:
        pass
    try:
        raw = path.read_bytes()
        # pull readable ASCII runs (enough for simple invoice PDFs)
        text = raw.decode("latin-1", errors="ignore")
        return text, "raw_bytes"
    except Exception as exc:  # noqa: BLE001
        return "", f"fail:{exc}"[:80]


def read_document_text(path: Path) -> Tuple[str, str]:
    suf = path.suffix.lower()
    if suf == ".pdf":
        return extract_pdf_text(path)
    if suf in (".txt", ".csv", ".md", ".log"):
        return path.read_text(encoding="utf-8", errors="replace"), "text"
    # try text first
    try:
        return path.read_text(encoding="utf-8", errors="replace"), "text_guess"
    except Exception:
        return "", "unreadable"


def process_file(
    path: Path,
    con: sqlite3.Connection,
    quarantine: Path,
) -> Dict[str, Any]:
    h = file_hash(path)
    if already_done(con, h):
        return {"path": str(path), "hash": h, "status": "skip_dup"}
    try:
        text, method = read_document_text(path)
        rows = extract_from_text(text) if text else []
        suf = path.suffix.lower()
        if not rows:
            quarantine.mkdir(parents=True, exist_ok=True)
            dest = quarantine / path.name
            if not dest.exists():
                dest.write_bytes(path.read_bytes())
            note = f"no_rows method={method} suf={suf}"
            if suf == ".pdf":
                note += " (OCR not in v0.2 — install pypdf for text PDFs; images need later OCR)"
            con.execute(
                "INSERT OR REPLACE INTO files(hash,path,status,processed_at,note) VALUES (?,?,?,?,?)",
                (h, str(path), "quarantine", utc(), note[:200]),
            )
            con.commit()
            return {
                "path": str(path),
                "hash": h,
                "status": "quarantine",
                "rows": 0,
                "method": method,
            }
        for r in rows:
            con.execute(
                "INSERT INTO rows(file_hash,vendor,invoice_no,amount,raw_line,created_at) VALUES (?,?,?,?,?,?)",
                (h, r["vendor"], r["invoice_no"], r["amount"], r["raw_line"], utc()),
            )
        con.execute(
            "INSERT OR REPLACE INTO files(hash,path,status,processed_at,note) VALUES (?,?,?,?,?)",
            (h, str(path), "ok", utc(), f"rows={len(rows)} method={method}"),
        )
        con.commit()
        return {
            "path": str(path),
            "hash": h,
            "status": "ok",
            "rows": len(rows),
            "method": method,
        }
    except Exception as exc:  # noqa: BLE001
        quarantine.mkdir(parents=True, exist_ok=True)
        dest = quarantine / (path.name + ".err.txt")
        dest.write_text(f"{path}\n{exc}\n", encoding="utf-8")
        con.execute(
            "INSERT OR REPLACE INTO files(hash,path,status,processed_at,note) VALUES (?,?,?,?,?)",
            (h, str(path), "error", utc(), str(exc)[:200]),
        )
        con.commit()
        return {"path": str(path), "hash": h, "status": "error", "error": str(exc)[:160]}


def export_csv(con: sqlite3.Connection, csv_path: Path) -> int:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    cur = con.execute(
        "SELECT vendor, invoice_no, amount, file_hash, created_at FROM rows ORDER BY id"
    )
    rows = cur.fetchall()
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["vendor", "invoice_no", "amount", "file_hash", "created_at"])
        w.writerows(rows)
    return len(rows)


def run_pipeline(
    inbox: Path,
    out: Path,
    quarantine: Optional[Path] = None,
) -> Dict[str, Any]:
    quarantine = quarantine or (out / "quarantine")
    db_path = out / "pipeline.sqlite"
    csv_path = out / "rows.csv"
    inbox.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    con = ensure_db(db_path)
    results = []
    for path in sorted(inbox.iterdir()):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        results.append(process_file(path, con, quarantine))
    n_csv = export_csv(con, csv_path)
    con.close()
    return {
        "ok": True,
        "version": VERSION,
        "inbox": str(inbox),
        "out": str(out),
        "files": results,
        "csv_rows": n_csv,
        "db": str(db_path),
        "csv": str(csv_path),
    }


def status(out: Path) -> Dict[str, Any]:
    db_path = out / "pipeline.sqlite"
    if not db_path.is_file():
        return {"ok": False, "error": "no db yet", "out": str(out)}
    con = sqlite3.connect(str(db_path))
    files = con.execute(
        "SELECT status, COUNT(*) FROM files GROUP BY status"
    ).fetchall()
    nrows = con.execute("SELECT COUNT(*) FROM rows").fetchone()[0]
    con.close()
    return {
        "ok": True,
        "files_by_status": {s: n for s, n in files},
        "row_count": nrows,
        "db": str(db_path),
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="folder_pipeline v0")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--inbox", default="samples/inbox")
    r.add_argument("--out", default="samples/out")
    r.add_argument("--quarantine", default="")
    s = sub.add_parser("status")
    s.add_argument("--out", default="samples/out")
    args = ap.parse_args(argv)
    # when run as script from package dir, paths relative to cwd
    base = Path.cwd()
    if args.cmd == "run":
        q = Path(args.quarantine) if args.quarantine else None
        rep = run_pipeline(base / args.inbox, base / args.out, q)
        print(json.dumps(rep, indent=2))
        return 0 if rep.get("ok") else 1
    if args.cmd == "status":
        print(json.dumps(status(base / args.out), indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
