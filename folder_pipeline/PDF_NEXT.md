# PDF extract next (UP-001b)

**At:** 2026-07-30T22:36:11.210947+00:00

## Status

- v0 CSV/text pipeline: **done** (`pipeline.py`, sample smoke).
- PDF: **planned** — prefer optional `pypdf` if present; else quarantine PDF with clear note.
- OCR: **later** (Tesseract) — not required for first paid CSV jobs.

## Client package rule

Ship `packages/folder_pipeline` only. No JoeysAI house.

## Next code slice

1. Detect `.pdf` in inbox
2. Try text extract if pypdf installed
3. Else quarantine + status row
4. Keep hash resume + CSV export
