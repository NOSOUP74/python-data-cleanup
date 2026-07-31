# Runbook — folder_pipeline

## 1. Install

1. Install Python 3.10+ from python.org (check “Add to PATH” on Windows).
2. Unzip `folder_pipeline_*.zip` to a folder you control.
3. Optional: `pip install pypdf` for better PDF text extraction.

## 2. First run (demo)

```text
cd folder_pipeline
python pipeline.py run --inbox samples/inbox --out samples/out
python pipeline.py status --out samples/out
```

Open `samples/out/rows.csv` in Excel.

## 3. Client folders

1. Create e.g. `C:\ClientData\inbox` and `C:\ClientData\out`
2. Copy invoices into inbox
3. Run:

```text
python pipeline.py run --inbox C:\ClientData\inbox --out C:\ClientData\out
```

## 4. Windows Task Scheduler (optional)

1. Open Task Scheduler → Create Basic Task  
2. Trigger: daily or on logon  
3. Action: Start a program  
   - Program: `python`  
   - Arguments: `pipeline.py run --inbox C:\ClientData\inbox --out C:\ClientData\out`  
   - Start in: path to unzipped `folder_pipeline`  

## 5. If something fails

- Check `out/quarantine` for rejected files  
- Re-run is safe (hash resume)  
- Confirm Python version: `python --version`  
- For image-only PDFs, text extract will quarantine — OCR is a separate upgrade  

## 6. Support window

Package defects for **14 days** after delivery (as agreed on the job).  
New field layouts = new small change order, not free unlimited scope.
