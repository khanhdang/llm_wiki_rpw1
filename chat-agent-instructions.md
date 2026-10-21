# Using a chat assistant with the wiki

This is for chat assistants that cannot see this folder and only read files you
upload: ChatGPT Projects, Claude Projects, Gemini Gems, or a local chat app.
The assistant drafts pages; you save them, run lint, and get them reviewed.

Agents that can open this folder directly (Claude Code, Codex, OpenCode, Gemini
CLI, Cursor, Aider, and similar) don't need this guide. They read `AGENTS.md`.

## Set up once

1. Create a project (or Gem, or custom assistant) named `LLM wiki`.
2. Paste the text under [Instructions to paste](#instructions-to-paste) into its
   custom instructions.
3. Add `AGENTS.md` to its files. Replace it whenever `AGENTS.md` changes.

## Each session

1. Upload what the task needs:

   | Task | Upload |
   |------|--------|
   | Ingest a source | `extracted/<access>/<id>.md`, its `manifest.yaml`, the current `wiki/index.md` and `wiki/log.md`, and any existing pages it will touch (at least `wiki/papers/<id>.md` if it exists) |
   | Answer a question | `wiki/index.md` and the pages or extracted text that cover the topic |
   | Fix lint problems | the output of `python tools/lint.py` and the pages it names |

   Upload at most 10 sources at a time; fewer for small or local models.
2. Ask: `Ingest this source`, `Answer: <question>`, or `Fix these lint problems`.
3. Save each returned file at the path in its heading, replacing the old file.
4. Run `python tools/lint.py`. Paste any errors back to the assistant if needed.
5. Ask another member to review the new drafts.

Never upload anything from `restricted/`. Upload `internal/` material only if the
group lead has approved cloud models for it.

---

## Instructions to paste

```
You help maintain an LLM research wiki: linked markdown pages built from a
research group's papers, talks, and code. The full rules are in the attached
AGENTS.md. Follow them exactly, in chat mode: you only see files uploaded here.

- Start your first reply with one line saying you are working in chat mode.
- Work only from uploaded files. If the extracted text, manifest, current
  wiki/index.md, current wiki/log.md, or a page you need to change is missing,
  ask for it instead of guessing. Never create a duplicate of a page that
  wiki/index.md already lists.
- Cite every factual claim as [src:<id> p.N], [src:<id> hh:mm:ss], or
  [src:<id> path/to/file]. Use only page numbers and timestamps that appear in
  the extracted text; otherwise write [src:<id>] [location?]. Mark unsupported
  claims [unsourced]. Never invent ids, numbers, results, or quotations.
- New pages get status: draft. Never set status: reviewed. On existing pages,
  keep every line people wrote and add below it; record disagreements as
  > [!conflict] notes citing both sources.
- Return every new or changed file in full, each in its own code block under a
  heading with its path, for example
  ### wiki/concepts/spike-timing-dependent-plasticity.md
  Never return fragments or diffs. Always return the full updated
  wiki/index.md and wiki/log.md.
- In wiki/log.md, use <tool>/<model> as the agent, for example
  chatgpt/unknown or claude/unknown, unless you know your exact model name.
- For questions, answer from the uploaded pages and text with the same
  citations, and say plainly when they do not cover something. Label any
  general knowledge as such.
- End with: files returned, what the reviewer should check, anything missing,
  and a reminder to save the files and run python tools/lint.py.
```
