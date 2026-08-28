# Original-file integrity check

## Baseline

Before publication authoring, `git status --short` and `git diff --name-only` were empty. SHA-256 hashes were captured for all 15 original tracked files in `original_tracked_hashes.sha256`.

## Final verification

The integrity script reported:

```text
All original tracked files match the recorded SHA-256 baseline.
```

Final Git checks report only the new untracked `publication/` directory. No original tracked path appears in `git diff --name-only`.

## Checklist

- [x] Original notebooks unchanged
- [x] Original source code unchanged
- [x] Original tracked result unchanged
- [x] Original report source and PDF unchanged
- [x] Original README unchanged
- [x] Original requirements unchanged
- [x] No original file deleted, renamed, moved, or overwritten
- [x] Publication work isolated below `publication/`
- [x] Original and extension experiments distinguished
- [x] No test-set threshold optimization
- [x] Failure-mode columns excluded from predictors
- [x] Average Precision terminology used correctly

Re-run at any time:

```powershell
powershell -ExecutionPolicy Bypass -File publication\scripts\check_original_integrity.ps1
```
