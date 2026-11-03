#!/usr/bin/env python3
"""Ask research questions of the wiki through a local oMLX (or other OpenAI-compatible) server.

Follows the Question workflow in AGENTS.md: answers from wiki/ first, then
from extracted/, with [src:...] citations. Picks the most relevant pages and
extracted passages by keyword overlap and sends only those to the model.

Reads wiki/ and extracted/open/ (plus extracted/internal/ with
--include-internal; see the data-access table in AGENTS.md). Never opens raw/ or anything
under restricted/.

Usage:
  python tools/chat.py                         # interactive
  python tools/chat.py "What is STDP?"         # one question
  python tools/chat.py "What is STDP?" --save stdp-basics

Settings (flag, else environment, else default):
  --base-url  OMLX_BASE_URL  http://127.0.0.1:8000/v1
  --model     OMLX_MODEL     first model the server lists
  --api-key   OMLX_API_KEY   auth.api_key from ~/.omlx/settings.json
"""

import argparse
import datetime
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wikipaths  # noqa: E402

SPECIAL = {"index.md", "log.md"}
MARKER_RE = re.compile(r"<!--\s*(p\.\d+|\d{1,2}:\d{2}:\d{2})\s*-->")
CITE_RE = re.compile(r"\[src:([^\]\s]+)(?:\s[^\]]*)?\]")
WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-]{2,}")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
STOP = set("""the and for with that this from are was were what which how does into about
have has had not but can its their there they them than then also use used using who why
when where your you our all any each other some such these those between more most""".split())
CHUNK_CHARS = 3000

SYSTEM = """You answer research questions for a group's research wiki. Rules:
- Use only the CONTEXT below. Prefer wiki pages; use extracted source text to add detail.
- Cite every factual claim inline. Wiki pages already carry citations such as
  [src:smith2024-spike-timing-attacks p.4]; carry those over. For extracted text, cite
  [src:<source-id> <location>] using the location shown in the passage header
  (p.N or hh:mm:ss). If you cannot tell the location, write [src:<id>] [location?].
- You may also point to wiki pages as [[page-name]].
- Never invent a source id, page number, timestamp, number, or quotation.
- If the context does not cover the question, say so plainly. Label anything you add from
  general knowledge as "(general knowledge, not from the sources)".
- Answer in English, concisely, in markdown."""


def tokens(text):
    return [w for w in WORD_RE.findall(text.lower()) if w not in STOP]


def safe_files(top):
    """Yield .md files under `top`, skipping symlinks; `top` must not be under restricted/."""
    if top.is_symlink() or not top.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(top, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if not (Path(dirpath) / d).is_symlink())
        for f in sorted(filenames):
            p = Path(dirpath) / f
            if f.endswith(".md") and not p.is_symlink():
                yield p


def wiki_chunks(root):
    for p in safe_files(root / "wiki"):
        if p.parent == root / "wiki" and p.name in SPECIAL:
            continue
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        parts = [text] if len(text) <= 2 * CHUNK_CHARS else re.split(r"\n(?=## )", text)
        for part in parts:
            yield {"label": f"wiki page {rel} (link as [[{p.stem}]])", "text": part.strip(), "wiki": True, "page": p.stem}


def extracted_chunks(root, allowed):
    for access in allowed:
        top = root / "extracted" / access
        for p in safe_files(top):
            rel = p.relative_to(root / "extracted").as_posix()
            if wikipaths.check_rel_path(rel, allowed) or wikipaths.symlink_in_path(root / "extracted", rel):
                continue
            sid = p.stem
            text = p.read_text(encoding="utf-8", errors="replace")
            # Split at location markers, then pack into chunks of about CHUNK_CHARS.
            pieces, loc, last = [], None, 0
            for m in MARKER_RE.finditer(text):
                pieces.append((loc, text[last:m.start()]))
                loc, last = m.group(1), m.end()
            pieces.append((loc, text[last:]))
            buf, start = "", None
            for loc, piece in pieces:
                if buf and len(buf) + len(piece) > CHUNK_CHARS:
                    yield chunk_from(sid, start, buf)
                    buf, start = "", None
                if start is None:
                    start = loc
                buf += (f"\n<!-- {loc} -->\n" if loc else "") + piece
                while len(buf) > 2 * CHUNK_CHARS:
                    yield chunk_from(sid, start, buf[:CHUNK_CHARS])
                    buf = buf[CHUNK_CHARS:]
            if buf.strip():
                yield chunk_from(sid, start, buf)


def chunk_from(sid, loc, text):
    where = f"starting at {loc}" if loc else "location unknown before first marker"
    return {"label": f"extracted text of source {sid} ({where})", "text": text.strip(), "wiki": False}


def retrieve(chunks, question, budget):
    q = set(tokens(question))
    if not chunks or not q:
        return []
    docs = [Counter(tokens(c["text"] + " " + c["label"])) for c in chunks]
    n = len(docs)
    df = Counter(w for d in docs for w in q if w in d)
    scored = []
    for c, d in zip(chunks, docs):
        length = sum(d.values()) or 1
        s = sum(math.log(1 + n / df[w]) * (1 + math.log(d[w])) for w in q if d[w])
        s /= math.sqrt(length / 200 + 1)
        if c["wiki"]:
            s *= 2  # wiki first
        if s > 0:
            scored.append((s, c))
    scored.sort(key=lambda x: -x[0])
    picked, used = [], 0
    for _, c in scored:
        if used + len(c["text"]) > budget:
            continue
        picked.append(c)
        used += len(c["text"])
    return picked


def default_api_key(base_url):
    if os.environ.get("OMLX_API_KEY"):
        return os.environ["OMLX_API_KEY"]
    if not re.match(r"https?://(127\.0\.0\.1|localhost)[:/]", base_url):
        return None
    try:
        settings = json.loads((Path.home() / ".omlx" / "settings.json").read_text())
        return settings.get("auth", {}).get("api_key") or None
    except (OSError, ValueError):
        return None


def request(base_url, api_key, path, payload=None):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(base_url.rstrip("/") + path, data=data, headers=headers)
    return urllib.request.urlopen(req, timeout=600)


def first_model(base_url, api_key):
    with request(base_url, api_key, "/models") as r:
        models = json.load(r).get("data", [])
    if not models:
        sys.exit("The server lists no models. Download one in oMLX first.")
    return models[0]["id"]


def ask(args, chunks, question):
    picked = retrieve(chunks, question, args.budget)
    if picked:
        context = "\n\n".join(f"### {c['label']}\n{c['text']}" for c in picked)
    else:
        context = "(No wiki page or extracted text matched this question.)"
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"CONTEXT:\n\n{context}\n\nQUESTION: {question}"},
    ]
    if args.show_context:
        for c in picked:
            print(f"  - {c['label']}", file=sys.stderr)
    payload = {"model": args.model, "messages": messages, "stream": True,
               "temperature": args.temperature, "max_tokens": args.max_tokens}
    out = []
    with request(args.base_url, args.api_key, "/chat/completions", payload) as r:
        for raw in r:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                delta = json.loads(data)["choices"][0].get("delta", {})
            except (ValueError, KeyError, IndexError):
                continue
            piece = delta.get("content") or ""
            out.append(piece)
            print(piece, end="", flush=True)
    print()
    return "".join(out).strip(), sorted({c["page"] for c in picked if c["wiki"]})


def save(root, name, question, answer, pages, model):
    today = datetime.date.today().isoformat()
    path = root / "wiki" / "questions" / f"{name}.md"
    if path.exists():
        sys.exit(f"{path.relative_to(root)} already exists; pick another name.")
    known = wikipaths.manifest_ids(root, ("open", "internal"))
    sources = sorted({s for s in CITE_RE.findall(answer) if s in known})
    title = question.strip().rstrip("?") + "?"
    page = (f"---\ntitle: {json.dumps(title)}\ntype: question\nsources: [{', '.join(sources)}]\n"
            f"tags: [question]\nupdated: {today}\nstatus: draft\n---\n\n"
            f"**Question:** {question.strip()}\n\n{answer}\n\n## Related\n\n"
            + "".join(f"- [[{pg}]]\n" for pg in pages))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")

    index = root / "wiki" / "index.md"
    text = index.read_text(encoding="utf-8")
    entry = f"- [[{name}]]: {question.strip()}\n"
    if "## Questions" in text:
        head, tail = text.split("## Questions", 1)
        rest = tail.lstrip("\n")
        nxt = rest.find("\n## ")
        section, after = (rest, "") if nxt == -1 else (rest[:nxt + 1], rest[nxt + 1:])
        section = section.rstrip("\n") + "\n" if section.strip() else ""
        text = f"{head}## Questions\n\n{section}{entry}" + (f"\n{after}" if after else "")
    else:
        text = text.rstrip("\n") + f"\n\n## Questions\n\n{entry}"
    index.write_text(text, encoding="utf-8")

    with open(root / "wiki" / "log.md", "a", encoding="utf-8") as f:
        f.write(f"{today} | question | omlx-chat/{model} | created: questions/{name} | updated: index\n")
    print(f"\nSaved wiki/questions/{name}.md (draft). Run: python tools/lint.py", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("question", nargs="?", help="question to ask; omit for interactive mode")
    ap.add_argument("--root", default=str(wikipaths.TOOLS_DIR.parent), help="wiki root folder (default: this folder)")
    ap.add_argument("--base-url", default=os.environ.get("OMLX_BASE_URL", "http://127.0.0.1:8000/v1"))
    ap.add_argument("--model", default=os.environ.get("OMLX_MODEL"))
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--include-internal", action="store_true",
                    help="also read extracted/internal/ (local models, or cloud with group-lead approval)")
    ap.add_argument("--budget", type=int, default=60000, help="max characters of context sent (default: 60000)")
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--show-context", action="store_true", help="list the passages sent to the model")
    ap.add_argument("--save", metavar="NAME", help="save the answer as wiki/questions/NAME.md (one question only)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if args.save and (not args.question or not NAME_RE.match(args.save)):
        sys.exit("--save needs a question and a lowercase-hyphen NAME, e.g. --save stdp-basics")
    args.api_key = args.api_key or default_api_key(args.base_url)
    allowed = wikipaths.allowed_roots(args.include_internal)
    if args.include_internal:
        print("Reading extracted/internal/: fine if the model runs on the group's own hardware;\n"
              "for a cloud model only with group-lead approval.", file=sys.stderr)

    try:
        args.model = args.model or first_model(args.base_url, args.api_key)
    except urllib.error.HTTPError as e:
        sys.exit(f"Server refused the request ({e.code}). Set OMLX_API_KEY or --api-key.")
    except urllib.error.URLError as e:
        sys.exit(f"Cannot reach {args.base_url} ({e.reason}). Is oMLX running? Try: omlx start")

    chunks = list(wiki_chunks(root)) + list(extracted_chunks(root, allowed))
    print(f"[{args.model} @ {args.base_url} | {len(chunks)} passages from wiki/ and "
          f"extracted/{{{','.join(allowed)}}}]", file=sys.stderr)

    if args.question:
        answer, pages = ask(args, chunks, args.question)
        if args.save:
            save(root, args.save, args.question, answer, pages, args.model)
        return
    while True:
        try:
            q = input("\n? ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if q in ("exit", "quit"):
            return
        if q:
            ask(args, chunks, q)


if __name__ == "__main__":
    main()
