# Python Data Cleanup — Folder → Clean Table

**Client-ready sample from Olivia Steele's technical delivery team.**

Drop messy text/CSV files in an inbox → get a **clean table** (CSV + SQLite).  
Runs **offline** on your machine. **No cloud.** **No access** to any private systems.

---

## Buy this kind of work when you need

- Bookkeeping prep from invoice / export dumps  
- CSV / spreadsheet cleanup (headers, dedupe, merge)  
- A small Python tool you **own** after delivery  
- Crash-safe processing of a whole folder

---

## Quick demo (2 minutes)

```text
cd folder_pipeline
python pipeline.py run --inbox samples/inbox --out samples/out
python pipeline.py status --out samples/out
```

| Output | Meaning |
|--------|---------|
| `samples/out/rows.csv` | Cleaned rows |
| Quarantine folder | Files that did not match / unreadable |
| Runbook | How to run on your data |

More: `folder_pipeline/RUNBOOK.md` · `folder_pipeline/ACCEPTANCE.md`

---

## What you get on a real job

1. Scoped fields and price after **your** redacted samples  
2. **Zip package** + short runbook  
3. Proof run on samples  
4. Fix window for package defects  

**Stack:** Python 3.10+ · standard library first · optional PDF text (pypdf)

---

## Design rules (why it is trustworthy)

- Isolated package only — not a dump of private infrastructure  
- Crash-safe resume by file hash  
- Quarantine for bad files  
- Clear deliverables — clients get done-means  

---

## Hire the team

Public face / delivery manager: **Olivia Steele**  
This repo is a **sample product**, not the full private stack.

- GitHub profile: https://github.com/NOSOUP74  
- Marketplace: Fiverr / work channels under Olivia Steele  

Open an issue titled **Quote request** with what you need, or contact via marketplace.

---

*Built as a client-safe product sample.*