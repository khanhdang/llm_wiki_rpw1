# LLM research wiki

An example template for a research wiki that AI agents write and people review.
Drop a group's papers, talks and code into `raw/`, and any AI agent (a coding
agent, a chat assistant, or a local model) turns them into linked, cited
markdown pages. The sample ids and topics (spiking neural networks, edge AI
hardware) are only illustrations; swap in your own field.

## How it works

```
 raw/ ──► extracted/ ──► AI agent ──► wiki/ ──► review
 original    plain text    any tool,     draft pages   another member
 files       per source    any model     with sources  sets status: reviewed
```

- **`raw/`**: original files, split into `open/`, `internal/` and
  `restricted/` by who may see them. Agents only read it.
- **`sources/`**: one small manifest per source (id, title, authors, file
  hashes, tags). Agents use it as the index instead of searching `raw/`.
- **`extracted/`**: the text of each source, with page or timestamp markers.
- **`wiki/`**: the pages people read. Every claim cites its source down to the
  page or timestamp, e.g. `[src:smith2024-spike-timing-attacks p.4]`.

## Files

```
llm-wiki/
├── README.md                     # this file
├── AGENTS.md                     # the rules every AI agent follows
├── CLAUDE.md, GEMINI.md          # point Claude Code and Gemini CLI at AGENTS.md
├── CONTRIBUTING.md               # setup, adding sources, review
├── chat-agent-instructions.md    # for chat assistants that only see uploads
├── setup-prompt.md               # prompt that rebuilds this scaffold
├── .claude/settings.json         # Claude Code permission rules
├── raw/  sources/  extracted/    # source material
├── wiki/
│   ├── index.md                  # start here
│   ├── log.md                    # every agent run
│   ├── concepts/  methods/  hardware/
│   ├── papers/    projects/ people/
│   └── questions/
└── tools/                        # check_raw.sh, validate_manifests.py, lint.py
```

## Works with any agent

All the rules live in one file, [AGENTS.md](AGENTS.md), written so that any
agent can follow it:

- **Coding agents** that open the folder (Codex, OpenCode, Cursor, Aider,
  Copilot, and others) read `AGENTS.md` directly. Claude Code and Gemini CLI
  find it through `CLAUDE.md` and `GEMINI.md`.
- **Chat assistants** that only see uploaded files (ChatGPT, Claude, or Gemini
  projects) get a paste-in prompt from
  [chat-agent-instructions.md](chat-agent-instructions.md) and return complete
  files for you to save.
- **Local models** work through either route. Give them fewer sources per run.

Every agent writes draft pages, logs what it did in `wiki/log.md`, and leaves
`status: reviewed` to people.

## Getting started

1. Run `pip install pyyaml` and `./tools/check_raw.sh`.
2. Add a source: the file in `raw/`, a manifest in `sources/`, and its text in
   `extracted/`. [CONTRIBUTING.md](CONTRIBUTING.md#4-add-a-source) shows how.
3. Ask your agent: `Ingest the new sources`.
4. Run `python tools/lint.py`, then have another member review the drafts.

## Reading the wiki

Open `wiki/index.md`. Pages are plain markdown with `[[links]]`, so they work in
Obsidian (open the folder as a vault), VS Code, or any markdown viewer.
`status: reviewed` means a person checked the page; `status: draft` means an
agent wrote it and nobody has checked it yet.

## Data rules

| Folder        | Cloud models                       | Local models |
|---------------|------------------------------------|--------------|
| `open/`       | allowed                            | allowed      |
| `internal/`   | only with the group lead's approval | allowed     |
| `restricted/` | never                              | allowed, outside this workflow |

`restricted/` is for interviews, participant data and unpublished work. No agent
working on the wiki reads it. Claude Code is blocked from it by
`.claude/settings.json`, but other tools only have the written rules, so keep
real sensitive data off any machine where a cloud agent runs. Refer to interview
participants only by opaque ids such as `INT-2026-007`.

## Maintenance

| Task | Who | How often |
|------|-----|-----------|
| Add sources, manifests and extracted text | any member | as needed |
| Ingest new sources | any member with an agent | weekly |
| Lint: broken links, missing citations, duplicates | rotating member | weekly |
| Review draft pages | rotating member | weekly |
| Back up the whole folder | group lead or delegate | monthly |

Questions about access go to the group lead. Replace this line with your own
group's contact details.
