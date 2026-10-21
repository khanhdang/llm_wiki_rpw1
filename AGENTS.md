# LLM research wiki: rules for AI agents

These are the rules for every AI agent that works on this wiki, whatever the tool
or model: coding agents (Claude Code, Codex, OpenCode, Gemini CLI, Cursor, Aider,
Copilot), chat assistants with uploaded files (ChatGPT, Claude, Gemini projects),
and local models. If a tool-specific file such as `CLAUDE.md` or `GEMINI.md`
seems to disagree with this one, this file wins.

## Your job

You maintain `wiki/`, a set of linked markdown pages built from the group's
sources. You read extracted text, write and update pages with citations, keep
the pages consistent, and answer research questions from them. People add the
sources and review your pages. Everything you write is a draft until a person
marks it `status: reviewed`.

## Know your mode

Work out which mode you are in before doing anything, and say so in one line at
the start of your first reply.

- **File mode**: you can read and write files in this folder, and possibly run
  commands. Edit files in place and follow the workflows below directly.
- **Chat mode**: you only see files the person uploaded. You cannot see the rest
  of the folder or run anything. Follow the workflows below, with the changes in
  [Chat mode](#chat-mode).

If you cannot run commands in file mode, do everything else and ask the person to
run `python tools/lint.py` and paste the result.

## Layout

```
llm-wiki/
├── AGENTS.md               # this file: rules for every agent
├── CLAUDE.md, GEMINI.md    # pointers to this file for tools that look for them
├── README.md               # overview for people
├── CONTRIBUTING.md         # how people set up, add sources, and review
├── chat-agent-instructions.md   # setup for chat assistants that only see uploads
├── setup-prompt.md         # prompt that builds this scaffold from scratch
├── .claude/settings.json   # Claude Code permission rules (do not loosen)
├── raw/                    # original files; read-only for agents
│   ├── open/
│   ├── internal/
│   └── restricted/         # never read by agents
├── sources/                # one manifest.yaml per source, mirroring raw/ paths
│   ├── open/
│   └── internal/
├── extracted/              # plain text of each source: <access>/<source-id>.md
│   ├── open/
│   └── internal/
├── wiki/
│   ├── index.md            # list of every page by type; start here
│   ├── log.md              # append-only record of every agent run
│   ├── concepts/   methods/   hardware/
│   ├── papers/     projects/  people/
│   └── questions/          # saved answers to research questions
└── tools/
    ├── check_raw.sh        # checks raw/ before you touch it
    ├── validate_manifests.py
    └── lint.py             # run after every change to wiki/
```

## Data access

Anything you read is sent to whoever runs your model, unless it runs on the
group's own hardware.

| Folder        | Cloud model                        | Local model |
|---------------|------------------------------------|-------------|
| `open/`       | yes                                | yes         |
| `internal/`   | only if the group lead approved it | yes         |
| `restricted/` | never                              | yes         |

- Default to `open/` only. Read `internal/` only when the person tells you the
  group lead approved it. Being able to see a file is not approval.
- Never read anything under `restricted/` (in `raw/`, `sources/`, or
  `extracted/`), in any form, with any tool or command. If a task seems to need
  it, stop and say so.
- `raw/` is read-only. Never create, move, rename, or delete anything in it.
- Never search `raw/` recursively (`find`, `ls -R`, `grep -r`, `**` globs); that
  would reach `raw/restricted/`. Use the manifests in `sources/` as the index and
  open files by their exact path.
- Before opening any raw file, run `tools/check_raw.sh` if you can. If it fails,
  stop and report the problem.
- Prefer `extracted/` to raw files. Open a raw file only to check a figure,
  table, or equation the extraction got wrong.
- Refuse paths that are absolute, contain `..`, or go through a symlink.

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
status: draft        # draft | reviewed (only people set reviewed)
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
- Pages about people cover published work only.
- Write in English. Keep original-language technical terms in parentheses where
  useful.

## People's edits win

Pages with `status: reviewed`, and any text a person wrote, are authoritative.
Do not rewrite or reorder them. Add new material below the existing text. If a
new source disagrees with them, add a note citing both sources:

```markdown
> [!conflict]
> [src:lee2023-stdp-fpga p.6] reports 12 pJ per synaptic event; this page says 20 pJ
> [src:smith2024-spike-timing-attacks p.4].
```

Never change `status` to `reviewed`, and never change it back to `draft` on a
reviewed page.

## Workflows

### Ingest (the default task)

1. List the sources to do: those named by the person, or else every manifest in
   `sources/open/` (and `sources/internal/` if approved) whose id has no line in
   `wiki/log.md`. Do at most 10 per run; local or small models should do 1 or 2.
2. For each source, read `extracted/<access>/<id>.md` and its manifest, then
   write or update `wiki/papers/<id>.md`.
3. Update or create every concept, method, hardware, project, and person page the
   source contributes to.
4. Add links in both directions between every page you touched, and add new
   pages to `wiki/index.md` as `- [[file-name]]: one-line description`.
5. Record disagreements with existing pages as `> [!conflict]` notes.
6. Append one line per source to `wiki/log.md` (format below).
7. Run `python tools/lint.py` and fix what it reports.
8. End with a short report for the reviewer: pages created, pages updated,
   conflicts, open questions, and anything you could not do.

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
YYYY-MM-DD | <source-id, lint, or question> | <tool>/<model> | created: <pages> | updated: <pages>
```

`<tool>/<model>` names who did the work, for example `claude-code/claude-opus-5-5`,
`codex/gpt-5`, `opencode/qwen3-32b`, or `chatgpt/unknown`. Use `unknown` for the
model if you do not know it; never guess.

## Chat mode

When you only see uploaded files:

- Work only from what was uploaded. Before an ingest, make sure you have the
  extracted text, its manifest, the current `wiki/index.md`, the current
  `wiki/log.md`, and every existing page you expect to change. Ask for anything
  missing instead of guessing what it contains.
- If `wiki/index.md` lists a page you need but it was not uploaded, ask for it.
  Do not create a duplicate.
- Return each changed or new file in full, as its own code block headed by its
  path, for example `### wiki/concepts/spike-timing-dependent-plasticity.md`.
  Never return fragments or diffs.
- Return the full `wiki/log.md` with your new lines appended, and the full
  updated `wiki/index.md`.
- Do not claim you searched the whole wiki or that lint passed. End by reminding
  the person to save the files, run `python tools/lint.py`, and have someone
  review the drafts.

## Never

- Read anything under `restricted/`.
- Write, move, or delete anything under `raw/`.
- Edit manifests in `sources/` unless the person asked you to fix a specific field.
- Delete wiki pages. Propose deletions in your report.
- Set `status: reviewed`, or rewrite text a person wrote.
- Invent sources, citations, numbers, or quotations.
- Loosen permission settings for any tool, or work around them.
