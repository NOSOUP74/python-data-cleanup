# folder_pipeline (client package v0)

**Isolated** — ship this folder only. Not JoeysAI / Victor house.

## What it does

Watch an inbox folder → extract simple fields from text/CSV → SQLite + CSV → resume after crash (by file hash). Bad files go to quarantine.

## Run

```text
python -m packages.folder_pipeline run --inbox samples/inbox --out samples/out
python -m packages.folder_pipeline status --out samples/out
```

From this package dir:

```text
cd packages/folder_pipeline
python pipeline.py run --inbox samples/inbox --out samples/out
```

## Config

See `config.example.json`.

## Status

v0 skeleton — safe defaults, no network, no whole-house imports.
