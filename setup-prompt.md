# Setup prompt

This folder already contains everything this prompt builds. Keep the prompt as a
record of how the scaffold was made, or use it to rebuild the scaffold in an
empty folder that holds only `README.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
`CONTRIBUTING.md`, and `chat-agent-instructions.md`.

It works with any agent:

- **An agent with file access** (Claude Code, Codex, OpenCode, Gemini CLI,
  Cursor, Aider, and similar): open the folder in it and paste the prompt.
- **A chat assistant without file access**: upload the files above, paste the
  prompt, then save the returned files and run the test commands yourself.

---

## Paste everything below this line

Set up this folder as an LLM research wiki. Read `AGENTS.md` first and follow
it; everything you build must match its layout and rules. `CONTRIBUTING.md`
shows how people will use the folder; make the scripts match the commands it
lists. Don't edit `README.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
`CONTRIBUTING.md`, or `chat-agent-instructions.md`, and don't overwrite or delete
any existing file.

If you can write files, create everything directly. If you can't, return each
file in full as its own code block headed by its path, and list the folders I
need to create.

Never read anything under `restricted/`. Don't write anything under `raw/`
beyond creating its empty folders in step 1.

Do these steps in order, and stop to ask me if anything fails:

1. **Folders.** Create `raw/open`, `raw/internal`, `raw/restricted`,
   `sources/open`, `sources/internal`, `extracted/open`, `extracted/internal`,
   `wiki/concepts`, `wiki/methods`, `wiki/hardware`, `wiki/papers`,
   `wiki/projects`, `wiki/people`, `wiki/questions`, and `tools`. Create
   `wiki/index.md` (one heading per page type, empty lists, and the line format
   from `AGENTS.md`) and `wiki/log.md` (a title and the log line format from
   `AGENTS.md`).

2. **Permissions for tools that support them.** For Claude Code, create
   `.claude/settings.json` (keep any rules already there, never loosen them):

   ```json
   {
     "permissions": {
       "deny": [
         "Read(./raw/restricted/**)",
         "Edit(./raw/**)",
         "Write(./raw/**)",
         "Read(./extracted/restricted/**)",
         "Read(./sources/restricted/**)"
       ]
     }
   }
   ```

   If you are a different tool with its own permission settings, tell me how to
   add the same rules there. Then tell me plainly that these settings are a
   backstop, not a security boundary: most tools can still reach files through
   shell commands, and the only real protection for sensitive material is
   keeping it off machines where cloud agents run.

3. **`tools/check_raw.sh`** (bash). Exit 0 only if `raw/` exists next to
   `tools/`, is a real directory and not a symlink, none of `raw/open`,
   `raw/internal`, `raw/restricted` is a symlink, and `raw/open/` can be listed
   without recursion. Otherwise print the reason and exit 1.

4. **`tools/manifest_schema.yaml` and `tools/validate_manifests.py`** (Python
   standard library plus PyYAML). Schema fields: `id`, `type` (paper | code |
   media | thesis | report | meeting), `title`, `authors`, `date`, `added_by`,
   `tags`, `access` (open | internal), `files` (list of `{path, sha256, size}`,
   paths relative to `raw/`), `source_url`, `doi`, `derived`. The validator:
   - reads manifests only under `sources/open/`, plus `sources/internal/` with
     `--include-internal`, and never lists or opens `sources/restricted/`;
   - checks each manifest against the schema, that `access` matches its folder,
     that `id` matches its folder name, and that ids are unique;
   - rejects absolute paths, `..`, symlinks, and paths outside the allowed
     access folders before opening anything;
   - with `--check-files`, runs `tools/check_raw.sh` and then checks each listed
     file exists under `raw/` with the right size, one `stat` per file, never
     listing directories;
   - accepts `--root DIR` so it can run against test data.

5. **`tools/lint.py`** (Python standard library plus PyYAML). Report broken
   `[[links]]`, orphan pages (no inbound links), missing or invalid frontmatter
   fields, pages in the wrong folder for their `type`, `[src:...]` citations to
   ids with no manifest, and counts of `[unsourced]` and `[location?]`. Print a
   markdown report. Exit 1 on broken links or unknown citation ids. Accept
   `--root DIR`.

6. **Test.** Build a small synthetic wiki in a temporary folder outside this
   one, with every sample claim labeled as synthetic. Show that the validator
   and linter pass on it, and that they catch a broken link, an unknown source
   id, and a disallowed file path. Show one sample paper page and log line.
   Delete only the temporary folder afterwards. If you can't run commands, give
   me the exact commands to run instead.

7. **Report.** Tell me briefly what you created and the commands I'll use day
   to day: check raw, validate manifests, ingest, lint.
