# SKILL-A3 / A3b dry-run — messy redacted samples

## Input

`samples/messy_redacted/` — **6 files** (5 synthetic redacted + 1 PDF)

## Command

```text
python pipeline.py run --inbox samples/messy_redacted --out samples/messy_out
```

## Result (v0.2.1 — A3b polish 2026-07-31)

- **ok:** true · **version 0.2.1**
- **files processed:** 6 (all status ok)
- **rows extracted:** **17** (was 20 before A3b — header noise rows removed)
- **out:** `samples/messy_out/rows.csv` + `pipeline.sqlite`

### A3b fixes

| Issue | Before | After |
|-------|--------|-------|
| Header as data (BOM `vendor,…`) | Mis-read as rows | Skipped via header detection |
| Quoted commas in vendor (`"Weird, Name Inc"`) | Split into broken fields | `csv.reader` → single vendor field |
| Empty vendor rows | Sometimes kept | Dropped |

### Still open (honest)

- Dup invoice lines within same file not de-duped (file-hash resume only)
- `NotARow,xx,not_number` still kept (thin extractor; amount validation optional later)
- OCR scans still out of scope

## Portfolio

Open `messy_out/rows.csv` for **A4 screenshots** (before = inbox folder, after = csv).
