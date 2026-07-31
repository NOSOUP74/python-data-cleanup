# Python Data Cleanup · Folder → Table

**What clients get:** a small offline Python tool — drop messy text/CSV files in an inbox, get a clean table (CSV + SQLite). No cloud required. No access to any private systems.

## Who this is for

- Bookkeeping prep from invoice/export dumps  
- CSV / spreadsheet cleanup automation  
- Small Python fixes around data scripts  

## Quick start

```text
cd folder_pipeline
python pipeline.py run --inbox samples/inbox --out samples/out
python pipeline.py status --out samples/out
```

See `folder_pipeline/RUNBOOK.md` and `folder_pipeline/ACCEPTANCE.md`.

## Sample outputs

- `folder_pipeline/samples/out/rows.csv` — example cleaned rows  
- `folder_pipeline/samples/messy_redacted/` — redacted messy inputs for demos  

## Design rules

- **Isolated package** — ship this folder only  
- **No network** required for the core pipeline  
- **Crash-safe resume** by file hash  
- **Quarantine** for unreadable / no-match files  
- dig ≠ proof on research; for clients: clear deliverables only  

## Stack

Python 3.10+ · standard library first · optional PDF text via pypdf if installed  

## Hire / contact

Looking for **fixed-price** small automation jobs: CSV clean, script fix, folder → spreadsheet.  
Upwork profile: link when live.

---

*Built as a client-safe product sample — not a dump of private infrastructure.*
