# Acceptance checklist — folder_pipeline v0.2

Client or Joseph marks done when:

- [ ] Zip opens; `pipeline.py` present  
- [ ] `python pipeline.py run --inbox samples/inbox --out samples/out` exits 0  
- [ ] `samples/out/rows.csv` has header + at least one data row  
- [ ] Re-run does not explode; already-done files show `skip_dup`  
- [ ] Bad/empty files can land in quarantine without crashing the batch  
- [ ] README + RUNBOOK readable  
- [ ] No JoeysAI / private house paths required to run  

**Signed off (name / date):** _______________________
