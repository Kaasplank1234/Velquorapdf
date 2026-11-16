# Source-available edition

Velqora PDF is **source-available, not open source**. The repository's `LICENSE` is the authoritative license; it permits limited private/internal use and modification, but restricts redistribution and publication of modified versions. Reading or downloading the code does not grant broader rights. Please review `LICENSE` before using it.

## What is currently in this repository

The uploaded `Velqora-PDF-10.3-Broncode-Platte-Tekst.txt` is a plain-text reference export. Its header says it is not a runnable project and that binary assets are excluded. It contains file markers and exported content, rather than a checked-out project tree. Keep it as an archival/reference export; do not treat it as an installable source package or as a complete build input.

## Recommended project layout

When the original project files and assets are available, restore them as actual files under the repository root, following the paths recorded in the export. For example:

```text
.github/
  workflows/
src/
scripts/
tests/
requirements-macos-arm64.txt
requirements-windows.txt
README.md
LICENSE
SOURCE-AVAILABLE.md
```

Keep each file at its recorded path and with its real extension (for example, Python modules as `.py`, workflow definitions as `.yml`, and scripts as `.sh` or `.ps1`). Keep tests separate from application code. Commit only source, documentation, tests, and necessary project assets; put generated installers, build output, and diagnostic reports in GitHub Releases or Actions artifacts instead of the source tree.

## Important before building or publishing packages

The text export describes packaging workflows and references archives/assets that are not established as standalone files by the export alone. Do not enable those workflows or claim reproducible builds until the original project files, dependencies, and required assets have been restored and the build has been verified. In particular, verify that workflow filenames, version numbers, artifact names, and referenced input files all match the checked-in project.

This document describes the current repository state; it does not change or expand the rights granted by `LICENSE`.
