# LLM research wiki: rules for Claude Code

You maintain `wiki/`, a set of linked markdown pages built from the group's
sources. You read extracted text, write and update pages with citations, keep
the pages consistent, and answer research questions from them. People add the
sources and review your pages, and reviewers use you to make their own changes.
Everything you write is a draft until a reviewer marks it `status: reviewed`.

## Layout

```
llm-wiki/
├── CLAUDE.md               # this file: the rules
├── README.md               # overview for people
├── CONTRIBUTING.md         # how people set up, add sources, and review
├── .claude/settings.json   # permission rules (do not loosen)
├── raw/                    # original files; read-only for you
│   │                       #   <access>/<category>/<source-id>/<file>, no year folder
│   ├── open/
│   ├── internal/
│   └── restricted/         # never read
├── sources/                # one manifest.yaml per source, mirroring raw/ paths
│   ├── open/
│   └── internal/
├── extracted/              # plain text of each source: <access>/<source-id>.md
│   ├── open/
│   └── internal/
├── wiki/
│   ├── index.md            # list of every page by type; start here
│   ├── log.md              # append-only record of every run
│   ├── concepts/   methods/   hardware/
│   ├── papers/     projects/  people/
│   └── questions/          # saved answers to research questions
└── tools/
    ├── check_raw.sh        # checks raw/ before you touch it
    ├── scan_raw.py         # finds PDFs in raw/open/ with no manifest; drafts one
    ├── validate_manifests.py
    ├── extract_pdf.py      # pypdf: PDF -> extracted/<access>/<id>.md
    └── lint.py             # run after every change to wiki/
```

## Data access

Everything you read is sent to Anthropic.

| Folder        | Allowed                            |
|---------------|------------------------------------|
| `open/`       | yes                                |
| `internal/`   | only if the group lead approved it |
| `restricted/` | never                              |

- Default to `open/` only. Read `internal/` only when the person tells you the
  group lead approved it. Being able to see a file is not approval.
- Never read anything under `restricted/` (in `raw/`, `sources/`, or
  `extracted/`), in any form, with any tool or command. If a task seems to need
  it, stop and say so.
- `raw/` is read-only. Never create, move, rename, or delete anything in it.
- Never search `raw/` recursively (`find`, `ls -R`, `grep -r`, `**` globs); that
  would reach `raw/restricted/`. Use the manifests in `sources/` as the index and
  open files by their exact path. The one exception is `tools/scan_raw.py`,
  which walks only `raw/open/` (and `raw/internal/` with `--include-internal`)
  to find PDFs that have no manifest yet.
- Before opening any raw file, run `tools/check_raw.sh`. If it fails, stop and
  report the problem.
- Prefer `extracted/` to raw files. Open a raw file only to check a figure,
  table, or equation the extraction got wrong.
- Refuse paths that are absolute, contain `..`, or go through a symlink.
- Work only inside this project folder. Never read, write, or list files
  outside it (no home directory, no sibling projects, no system paths).
- No internet access. Do not search the web, fetch URLs, or call outside
  services or connectors (Slack, Google Drive, Docs, artifacts), and do not
  use Bash network tools (`curl`, `wget`, `ssh`, and the like). Work only from
  `wiki/`, `extracted/`, and `sources/`. If a task needs something from
  outside, stop and say so.
- `.claude/settings.json` backs these rules up. Never loosen it, and never use
  Bash to reach a path it denies.

## Sources and citations

- Each source has an id equal to its folder name, for example
  `smith2024-spike-timing-attacks`, `2026-03-12_isscc-talk`, `snn-toolbox-v2`.
- Cite every factual claim inline:
  - paper: `[src:smith2024-spike-timing-attacks p.4]`
  - audio or video: `[src:2026-03-12_isscc-talk 00:12:30]`
  - code: `[src:snn-toolbox-v2 path/to/file.py]`
- Extracted text marks pages as `<!-- p.4 -->` and media positions as
  `<!-- 00:12:30 -->`. Use only locations that appear in it. If you cannot find
  the location, write `[src:<id>] [location?]`.
- Mark a claim with no source as `[unsourced]`.
- Never invent a source id, page number, timestamp, result, or quotation.
- If you add general knowledge that is not in the sources, label it as such.

## Page format

Every page in `wiki/` starts with this frontmatter:

```yaml
---
title: Spike-timing-dependent plasticity
type: concept        # concept | method | hardware | paper | project | person | question
sources: [smith2024-spike-timing-attacks, lee2023-stdp-fpga]
tags: [snn, learning]
updated: 2026-10-21
status: draft        # draft | reviewed
---
```

Then a 2 to 4 sentence summary, the body, and a `## Related` section of
`[[links]]`.

- Put each page in the folder that matches its `type`.
- File names are lowercase ASCII with hyphens, ending in `.md`. Links use the file
  name without `.md`: `[[spike-timing-dependent-plasticity]]`.
- Keep one page per topic. Before creating a page, check `wiki/index.md` and
  search `wiki/` for the same topic under another name, and update that page
  instead.
- Paper pages live at `wiki/papers/<source-id>.md` and contain: a bibliographic
  line, the contribution, the method, results with numbers, limitations, and
  links to the related concept and method pages. Talks and other media use the
  same layout.
- Directly under the bibliographic line, every paper page has a `Files:` line
  of relative markdown links to the source's manifest, its extracted text, and
  each raw file listed under `files:` in the manifest:

  ```markdown
  Files: [manifest](../../sources/open/papers/smith2024-spike-timing-attacks/manifest.yaml)
  · [extracted text](../../extracted/open/smith2024-spike-timing-attacks.md)
  · [paper.pdf](../../raw/open/papers/smith2024-spike-timing-attacks/paper.pdf)
  ```

  Take every path from the manifest (`files[].path` is relative to `raw/`,
  `derived.extracted` to the wiki root). Never list or search `raw/` to find
  file names, and never link to anything under `restricted/`. If a manifest
  path changes, update the links.
- Pages about people cover published work only.
- Write in English. Keep original-language technical terms in parentheses where
  useful.

## Reviewed pages

On your own initiative (ingest, lint, questions), treat pages with
`status: reviewed` as authoritative: do not rewrite or reorder them. Add new
material below the existing text. If a new source disagrees with them, add a
note citing both sources:

```markdown
> [!conflict]
> [src:lee2023-stdp-fpga p.6] reports 12 pJ per synaptic event; this page says 20 pJ
> [src:smith2024-spike-timing-attacks p.4].
```

When a reviewer asks you to change a page, that is their edit: make it, on any
page, as asked (see [Review](#review)).

## Workflows

### Extract

Extract PDFs with pypdf, only through `tools/extract_pdf.py`:

```bash
python tools/extract_pdf.py <source-id>            # add --include-internal only if approved
```

- The source needs a manifest first; the script finds the PDFs from its
  `files:` list, never by listing `raw/`. It runs `tools/check_raw.sh` itself.
- It writes `extracted/<access>/<id>.md` with a `<!-- p.N -->` marker per page,
  where N is the page of the PDF file. Do not call pypdf yourself or
  hand-write page markers.
- If pypdf is not installed, stop and say so; never install it yourself.
- pypdf reads only the text layer. If the script reports pages with no text
  (likely a scanned PDF), list them in your report.
- Never overwrite an existing extracted file (`--force`) unless the person
  asks; someone may have corrected it by hand.
- After extracting, spot-check a few pages against the PDF for garbled tables
  and equations, and list any you find in your report. If the manifest has no
  `derived.extracted`, tell the person to add it.

### Ingest (the default task)

0. Run `python tools/scan_raw.py` (add `--include-internal` only if approved).
   If it lists PDFs with no manifest, run it again with `--write-manifests`,
   then fill each draft's `title`, `authors`, `date` and `tags` from the
   extracted text, and run `python tools/validate_manifests.py --check-files`.
   Report any `problems:` lines (for example a PDF not in its own id folder)
   to the person; do not move files in `raw/`.
1. List the sources to do: those named by the person, or else every manifest in
   `sources/open/` (and `sources/internal/` if approved) whose id has no line in
   `wiki/log.md`. Do at most 10 per run.
2. For each source, if `extracted/<access>/<id>.md` is missing and the source
   is a PDF, extract it (see [Extract](#extract)). Then read the extracted
   text and its manifest, and write or update `wiki/papers/<id>.md`.
3. Update or create every concept, method, hardware, project, and person page the
   source contributes to.
4. Add links in both directions between every page you touched, and add new
   pages to `wiki/index.md` as `- [[file-name]]: one-line description`.
5. Record disagreements with existing pages as `> [!conflict]` notes.
6. Append one line per source to `wiki/log.md` (format below).
7. Run `python tools/lint.py` and fix what it reports.
8. End with a short report for the reviewer: pages created, pages updated,
   conflicts, open questions, and anything you could not do.

### Review

A reviewer checks draft pages and asks you to fix them, for example "on
`stdp`, the energy figure is from p.6, not p.4" or "merge `stdp-learning` into
`spike-timing-dependent-plasticity`".

1. Make the change the reviewer asked for. Check citations against the
   extracted text while you do; if what they ask for contradicts the source,
   say so and ask before writing it.
2. Keep every other rule: citations, page format, data access, no deletions
   without the reviewer saying which page to delete.
3. Set `status: reviewed` only when the reviewer explicitly asks you to mark a
   named page reviewed. Never do it on your own, and never for a page the
   reviewer has not looked at in this session.
4. Update `updated:` on every page you change, run `python tools/lint.py`, and
   append a `review` line to `wiki/log.md` naming the pages changed and marked
   reviewed.

### Lint

Run `python tools/lint.py` and fix what you can: broken `[[links]]`, orphan pages,
`[unsourced]` and `[location?]` markers you can resolve from the sources,
citations to unknown ids, duplicate pages, and frontmatter errors. Do not guess:
list anything that needs a person's decision in your report. Append a `lint` line
to `wiki/log.md`.

### Question

Answer from `wiki/` first, then from `extracted/`, citing as above. Say clearly
when the sources do not cover something. If the person wants the answer kept,
save it as `wiki/questions/<short-name>.md` with `type: question` and
`status: draft`, link it from `wiki/index.md`, and log it.

### Log format

One line per source or run, appended at the end of `wiki/log.md`:

```
YYYY-MM-DD | <source-id, lint, review, or question> | claude-code/<model id> | created: <pages> | updated: <pages>
```

Use your exact model id, for example `claude-code/claude-opus-5-5`.

## Never

- Read anything under `restricted/`.
- Access the internet or anything outside this project folder.
- Write, move, or delete anything under `raw/`.
- Edit manifests in `sources/` unless the person asked you to fix a specific field.
- Delete wiki pages unless a reviewer names the page; otherwise propose
  deletions in your report.
- Set `status: reviewed` without a reviewer's explicit request.
- Invent sources, citations, numbers, or quotations.
- Loosen permission settings, or work around them.
