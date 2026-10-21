# Contributing

You can work on the wiki with any AI agent, or by hand. Every agent follows the
same rules in [AGENTS.md](AGENTS.md), and a person reviews every page an agent
writes.

## 1. Set up once

```bash
cd llm-wiki
pip install pyyaml
./tools/check_raw.sh
```

Put `internal/` material in `raw/internal/` only if the group lead gave it to
you, and don't share it further. Never put `restricted/` material on a machine
where you run a cloud agent.

## 2. Pick an agent

Any agent works. What matters is whether it can open this folder.

| Kind of agent | Examples | How it gets the rules |
|---------------|----------|-----------------------|
| Coding agent with file access | Claude Code, Codex CLI, OpenCode, Gemini CLI, Cursor, Aider, GitHub Copilot | Reads `AGENTS.md` itself. Claude Code reads it through `CLAUDE.md`, Gemini CLI through `GEMINI.md`. If your tool reads neither, tell it: "Read AGENTS.md and follow it." |
| Chat assistant without file access | ChatGPT, Claude, or Gemini projects; local chat apps | You upload files and save its answers. Follow [chat-agent-instructions.md](chat-agent-instructions.md). |
| Local model | Any model served through an OpenAI-compatible API (vLLM, llama.cpp, Ollama, LM Studio) | Use it through a coding agent that supports custom endpoints (OpenCode, Aider, and others), or through a local chat app. |

Data rules apply whichever you pick: cloud models may read `open/`, and
`internal/` only with the group lead's approval. Only local models may process
`restricted/`, and even they only outside this workflow. Permission settings
(such as `.claude/settings.json`) exist only for some tools. With any other tool,
the safe option is to keep material it must not read off the machine.

### Example: a local model in OpenCode

Add an OpenAI-compatible provider to `opencode.local.json` or your global
OpenCode config, then run `opencode` in the wiki folder. Field names can change
between versions, so check the OpenCode docs.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "local": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Local model server",
      "options": { "baseURL": "http://<model-server-host>:8000/v1" },
      "models": { "<served-model-name>": { "name": "Local model" } }
    }
  }
}
```

Smaller models follow long instructions less reliably. Give them one or two
sources per run and review their pages more carefully.

## 3. Day to day

Ask your agent one of:

- `Ingest the new sources` (or `Ingest <source-id>, <source-id>`)
- `Run lint and fix what you can`
- `Answer: <question>` (add "and save it" to keep the answer as a page)

Then check the result yourself:

```bash
python tools/lint.py
```

## 4. Add a source

Agents never write to `raw/`, so adding sources is a person's job.

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
   relative to `raw/`.
4. Put the plain text at `extracted/open/smith2024-spike-timing-attacks.md`.
   Use any extraction tool or model you like, but mark where each page starts
   with `<!-- p.4 -->` (or `<!-- 00:12:30 -->` for audio and video) so agents
   can cite exact locations.
5. Check it, then ask an agent to ingest it:

   ```bash
   python tools/validate_manifests.py --check-files
   ```

## 5. Review

- Agents write every new or changed page as `status: draft`, log every run in
  `wiki/log.md`, and end with a report of what they changed.
- Don't review pages your own agent wrote; ask another member.
- Check that:
  - citations point to real pages or timestamps in the source,
  - there are no duplicate pages,
  - text people wrote is unchanged,
  - nothing comes from `restricted/`.
- When a page checks out, set `status: reviewed`. Only people do this.
- `wiki/log.md` shows which tool and model wrote what. If one keeps failing
  review, tell the group lead.
- Keep a backup of the whole folder with any backup or sync tool. There is no
  other change history.
