# LLM research wiki

A research wiki that Claude Code writes and people review. Drop a group's
papers, talks and code into `raw/`, and Claude Code turns them into linked,
cited markdown pages. The sample ids and topics (spiking neural networks, edge
AI hardware) are only illustrations; swap in your own field.

## How it works

```
 raw/ ──► extracted/ ──► Claude Code ──► wiki/ ──► review
 original    plain text    ingest         draft pages   another member checks,
 files       per source                   with sources  fixes via Claude Code
```

- **`raw/`**: original files, split into `open/`, `internal/` and
  `restricted/` by who may see them. Claude only reads it.
- **`sources/`**: one small manifest per source (id, title, authors, file
  hashes, tags). Claude uses it as the index instead of searching `raw/`.
- **`extracted/`**: the text of each source, with page or timestamp markers.
- **`wiki/`**: the pages people read. Every claim cites its source down to the
  page or timestamp, e.g. `[src:smith2024-spike-timing-attacks p.4]`.

## Files

```
llm-wiki/
├── README.md                     # this file
├── CLAUDE.md                     # the rules Claude Code follows
├── CONTRIBUTING.md               # setup, adding sources, review
├── .claude/settings.json         # Claude Code permission rules
├── raw/  sources/  extracted/    # source material
├── wiki/
│   ├── index.md                  # start here
│   ├── log.md                    # every Claude run
│   ├── concepts/  methods/  hardware/
│   ├── papers/    projects/ people/
│   └── questions/
└── tools/                        # check_raw.sh, validate_manifests.py, lint.py
```

## Getting started

1. Run `pip install pyyaml` and `./tools/check_raw.sh`.
2. Add a source: the file in `raw/`, a manifest in `sources/`, and its text in
   `extracted/`. [CONTRIBUTING.md](CONTRIBUTING.md#3-add-a-source) shows how.
3. Run `claude` in this folder and ask: `Ingest the new sources`.
4. Have another member review the drafts, using Claude Code to make fixes.

## Reading the wiki

Open `wiki/index.md`. Pages are plain markdown with `[[links]]`, so they work in
Obsidian (open the folder as a vault), VS Code, or any markdown viewer.
`status: reviewed` means a person checked the page; `status: draft` means Claude
wrote it and nobody has checked it yet.

## Data rules

Claude is a cloud model: everything it reads goes to Anthropic.

| Folder        | Claude may read                     |
|---------------|-------------------------------------|
| `open/`       | yes                                 |
| `internal/`   | only with the group lead's approval |
| `restricted/` | never                               |

`restricted/` is for interviews, participant data and unpublished work.
`.claude/settings.json` blocks Claude from it, but keep real sensitive data off
any machine where you run Claude Code anyway. Refer to interview participants
only by opaque ids such as `INT-2026-007`.

## Maintenance

| Task | Who | How often |
|------|-----|-----------|
| Add sources, manifests and extracted text | any member | as needed |
| Ingest new sources | any member | weekly |
| Lint: broken links, missing citations, duplicates | rotating member | weekly |
| Review draft pages | rotating member | weekly |
| Back up the whole folder | group lead or delegate | monthly |

Questions about access go to the group lead. Replace this line with your own
group's contact details.
