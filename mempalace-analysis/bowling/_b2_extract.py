#!/usr/bin/env python3
"""B2 — Vague-vs-precise diagnostics over raw bowling-league-tracker transcripts.
Reuses B1's David-message extraction, then dumps the full corpus of genuine
human messages (full text + citations) for hand-classification of the
diagnostic subset VAGUE vs PRECISE.
"""
import json, os, re

SRC = os.path.expanduser(
    "~/.claude/projects/-Users-utilityserver-github-bowling-league-tracker")

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$")
SKIP_SUBSTR = ("<system-reminder>", "<command-name>", "<command-message>",
               "<local-command-stdout>", "<command-args>", "<task-notification>")
INTERRUPT = "[Request interrupted by user"
RALPH_PROMPT = "Read PLAN.md. Find the first unchecked"
HARNESS_NOTIFY = re.compile(r"^(Ultraplan|Ralph|Loop)\b.*(stopped|complete|finished)", re.I)
SECRET_RE = re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")

def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict):
                if b.get("type") == "text":
                    parts.append(b.get("text", ""))
            elif isinstance(b, str):
                parts.append(b)
        return "\n".join(parts)
    return ""

def is_human(text):
    t = text.strip()
    if not t:
        return False
    if INTERRUPT in t:
        return False
    for s in SKIP_SUBSTR:
        if s in t:
            return False
    if t.startswith("Caveat:"):
        return False
    if t.startswith(RALPH_PROMPT):
        return False
    if HARNESS_NOTIFY.match(t):
        return False
    if t[:1] in ("◇", "◆", "◈"):
        return False
    if "Starting Claude Code on the web" in t or "Monitor progress in Claude Code" in t:
        return False
    if not re.search(r"[A-Za-z]", t):
        return False
    return True

msgs = []  # (text, session, line, wc)
files = sorted(f for f in os.listdir(SRC) if UUID_RE.match(f))
for fn in files:
    sess = fn[:-6]
    with open(os.path.join(SRC, fn)) as fh:
        for ln, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except Exception:
                continue
            if obj.get("type") != "user":
                continue
            msg = obj.get("message")
            if not isinstance(msg, dict) or msg.get("role") != "user":
                continue
            if obj.get("isMeta"):
                continue
            text = extract_text(msg.get("content"))
            if not is_human(text):
                continue
            t = SECRET_RE.sub("[REDACTED-API-KEY]", text.strip())
            msgs.append((t, sess, ln, len(t.split())))

print(f"TOTAL_HUMAN_MESSAGES\t{len(msgs)}")
print(f"FILES_PROCESSED\t{len(files)}")
sessions = sorted(set(s for _, s, _, _ in msgs))
print(f"SESSIONS_WITH_HUMAN\t{len(sessions)}\t{sessions}")

with open(os.path.join(os.path.dirname(__file__), "_b2_dump.txt"), "w") as out:
    for t, s, l, wc in msgs:
        t1 = t.replace("\n", " ⏎ ")
        out.write(f"[{s}:{l}] ({wc}w) {t1}\n")
print("DUMP_WRITTEN\t_b2_dump.txt")
