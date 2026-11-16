# PUBLISHING_CHECKLIST

This checklist reflects the current repository state as it exists in the project at the time of review. Status entries are based on evidence currently present in the repository, not on assumptions.

## Repository and provenance

- [x] Ownership of original source code: preserved in the source package and repository metadata; no independent chain-of-title review is included in the repo.
- [x] Third-party license obligations: preserved notices and license archives remain in the repo.
- [ ] AGPL compatibility review: pending formal review because PyMuPDF/MuPDF is AGPL-3.0 and the project also uses a custom source-available license.
- [x] Dependency license verification: dependency notices are listed in `THIRD_PARTY.md` and the preserved archive directories.
- [x] Completeness of the version 10.3 source: source package and build scripts are present under `Velqora-PDF-10.3-Cheesy-Studios-Source-Available/`.

## Security and privacy

- [x] Detection of secrets and private information: no obvious passwords, API keys, or personal credentials were found in the repository files reviewed.
- [ ] Source-to-binary reproducibility: not fully established from repository content alone.
- [x] Release asset verification: the official GitHub release names and assets were checked against the repository distribution metadata.

## Documentation and publication quality

- [x] README and documentation accuracy: updated to match the actual source package layout and release links.
- [ ] Cross-platform testing: not all OS builds were run in this environment; platform-specific testing remains pending.
- [ ] Publication readiness: pending final legal review of the custom source-available license against AGPL and other third-party obligations.

## Release readiness summary

- [x] Official release filenames and downloads are documented.
- [x] Repository paths and source entry point are documented accurately.
- [x] Third-party rights and risk notes are preserved for review.
- [ ] Final legal sign-off: pending.
- [ ] Final public release sign-off: pending.

## Notes

This checklist intentionally marks unresolved items as pending rather than claiming compliance that the repository cannot yet substantiate.

