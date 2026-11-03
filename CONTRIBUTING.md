# Contributing

All wiki work goes through [Claude Code](https://claude.com/claude-code). It
follows the rules in [CLAUDE.md](CLAUDE.md), and a person reviews every page it
writes.

## 1. Set up once

```bash
cd llm-wiki
pip install pyyaml docling
docling-tools models download   # once; docling then runs offline
./tools/check_raw.sh
```

Install Claude Code and run `claude` from this folder; it loads `CLAUDE.md` and
the permission rules in `.claude/settings.json` automatically. Don't loosen
those rules.

Put `internal/` material in `raw/internal/` only if the group lead gave it to
you, and don't share it further. Tell Claude when the group lead has approved
reading it. Never put `restricted/` material on a machine where you run Claude
Code.

## 2. Day to day

Ask Claude one of:

- `Ingest the new sources` (or `Ingest <source-id>, <source-id>`)
- `Run lint and fix what you can`
- `Answer: <question>` (add "and save it" to keep the answer as a page)

Claude runs `python tools/lint.py` itself and logs every run in `wiki/log.md`.

## 3. Add a source

Claude never writes to `raw/`, so adding sources is a person's job.

1. Pick an id: lowercase, no spaces, unique, for example
   `smith2024-spike-timing-attacks`.
2. Put the file in a folder named after the id, under the right access level:
   `raw/open/papers/2024/smith2024-spike-timing-attacks/paper.pdf`.
3. Write the manifest at the same path under `sources/`:
   `sources/open/papers/2024/smith2024-spike-timing-attacks/manifest.yaml`.

   ```yaml
   id: smith2024-spike-timing-attacks
   type: paper            # paper | code | media | thesis | report | meeting
   title: Spike-timing attacks on neuromorphic accelerators
   authors: [A. Smith, B. Tanaka]
   date: 2024-05
   added_by: your-name
   tags: [snn, security]
   access: open           # must match the top folder
   files:
     - path: open/papers/2024/smith2024-spike-timing-attacks/paper.pdf
       sha256: <output of: shasum -a 256 paper.pdf>
       size: 482113        # bytes
   source_url: https://example.org/paper
   doi:
   derived:
   ```

   All fields are described in `tools/manifest_schema.yaml`. File paths are
   relative to `raw/`. Or skip this step: `python tools/scan_raw.py
   --write-manifests` finds PDFs in `raw/open/` with no manifest and drafts
   one per source folder (path, sha256, size filled in), and Claude runs it at
   the start of every ingest. Fill in or check `title`, `authors`, `date` and
   `tags`.
4. Put the plain text at `extracted/open/smith2024-spike-timing-attacks.md`.
   For PDFs, Claude does this with docling during ingest, or you can run
   `python tools/extract_pdf.py smith2024-spike-timing-attacks` yourself.
   Docling runs offline, so once per machine run `pip install docling` and
   `docling-tools models download`. For other formats, use any tool you like,
   but mark where each page starts with `<!-- p.4 -->` (or `<!-- 00:12:30 -->`
   for audio and video) so Claude can cite exact locations.
5. Check it, then ask Claude to ingest it:

   ```bash
   python tools/validate_manifests.py --check-files
   ```

## 4. Review

Claude writes every new or changed page as `status: draft` and ends each run
with a report of what it changed. Reviewing means reading those drafts and
having Claude fix them.

- Don't review pages from your own ingest; ask another member.
- Open the draft, and check that:
  - citations point to real pages or timestamps in the source,
  - there are no duplicate pages,
  - nothing comes from `restricted/`.
- Tell Claude what to change, in plain words, for example:
  - `In wiki/concepts/stdp.md, the 12 pJ figure is on p.6, fix the citation`
  - `Merge stdp-learning into spike-timing-dependent-plasticity`
  - `Rewrite the summary of wiki/papers/<id>.md to lead with the main result`

  Claude makes the edit, checks it against the source, runs lint and logs a
  `review` line. You can also edit pages by hand; Claude keeps your text.
- When a page checks out, tell Claude `Mark <page> reviewed`, or set
  `status: reviewed` yourself. Claude never does it unasked.
- `wiki/log.md` shows which model wrote what. If drafts keep failing review,
  tell the group lead.
- Keep a backup of the whole folder with any backup or sync tool, or commit to
  git.
