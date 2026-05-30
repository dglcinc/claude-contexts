#!/usr/bin/env python3
"""B1 — Directive histogram over raw bowling-league-tracker transcripts.
Extracts David's genuine human messages from the 570 uuid-named *.jsonl
main-thread sessions, classifies them, and prints aggregates + samples.
"""
import json, glob, os, re, statistics, sys
from collections import Counter

SRC = os.path.expanduser(
    "~/.claude/projects/-Users-utilityserver-github-bowling-league-tracker")

# uuid-named only; exclude agent-*.jsonl and *.md
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$")

SKIP_SUBSTR = ("<system-reminder>", "<command-name>", "<command-message>",
               "<local-command-stdout>", "<command-args>", "<task-notification>")
INTERRUPT = "[Request interrupted by user"
# The bowling build was itself driven by a ralph loop: ~560 sessions open with
# this identical injected harness prompt. It is NOT a David directive.
RALPH_PROMPT = "Read PLAN.md. Find the first unchecked"
# Loop/Ultraplan harness auto-notifications (not human-typed).
HARNESS_NOTIFY = re.compile(r"^(Ultraplan|Ralph|Loop)\b.*(stopped|complete|finished)",
                            re.I)
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
                # skip tool_result, tool_use, image, etc.
            elif isinstance(b, str):
                parts.append(b)
        return "\n".join(parts)
    return ""

def is_directive(text):
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
    # Ultraplan/CC-web UI status lines pasted into the transcript (◇/◆ glyphs).
    if t[:1] in ("◇", "◆", "◈"):
        return False
    if "Starting Claude Code on the web" in t or "Monitor progress in Claude Code" in t:
        return False
    # Pure tool plumbing / pasted blobs heuristics: skip if no letters at all
    if not re.search(r"[A-Za-z]", t):
        return False
    return True

directives = []  # (text, session_uuid, line_no, wordcount)
files = sorted(f for f in os.listdir(SRC) if UUID_RE.match(f))
for fn in files:
    sess = fn[:-6]  # strip .jsonl
    path = os.path.join(SRC, fn)
    with open(path, "r") as fh:
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
            if not is_directive(text):
                continue
            t = SECRET_RE.sub("[REDACTED-API-KEY]", text.strip())
            wc = len(t.split())
            directives.append((t, sess, ln, wc))

n = len(directives)
print(f"TOTAL_DIRECTIVES\t{n}")
print(f"FILES_PROCESSED\t{len(files)}")

# (b) first-word histogram
fw = Counter()
for t, s, l, wc in directives:
    w = re.sub(r"[^a-z']", "", t.split()[0].lower()) if t.split() else ""
    if w:
        fw[w] += 1
print("\nTOP40_FIRSTWORD")
for w, c in fw.most_common(40):
    print(f"{w}\t{c}")

# imperative-verb-leading classification (same verb set spirit as baseline)
VERBS = set("""add remove delete merge commit push pull run open close update
fix make create build use change set move rename revert switch start stop
publish install check show give let put keep undo redo write read review test
deploy refactor rename split combine try look go get find replace edit apply
generate implement enable disable rerun restart clean drop bump""".split())
verb_lead = sum(1 for t,_,_,_ in directives
                if re.sub(r"[^a-z']","",t.split()[0].lower()) in VERBS)
print(f"\nVERB_LEADING\t{verb_lead}\t{100*verb_lead/n:.1f}%")

# (c)+(d) word-count buckets
def bucket(wc):
    if wc == 1: return "1"
    if wc <= 3: return "2-3"
    if wc <= 7: return "4-7"
    if wc <= 15: return "8-15"
    return "16+"
buckets = Counter(bucket(wc) for *_, wc in directives)
print("\nBUCKETS")
for b in ["1","2-3","4-7","8-15","16+"]:
    print(f"{b}\t{buckets[b]}\t{100*buckets[b]/n:.1f}%")

wcs = [wc for *_, wc in directives]
print(f"\nMEAN\t{statistics.mean(wcs):.2f}")
print(f"MEDIAN\t{statistics.median(wcs):.1f}")
le3 = sum(1 for w in wcs if w <= 3)
print(f"LE3\t{le3}\t{100*le3/n:.1f}%")

# Dump per-bucket samples to a file (varied, with citations) for hand-picking
with open(os.path.join(os.path.dirname(__file__), "_b1_samples.txt"), "w") as out:
    by_bucket = {b: [] for b in ["1","2-3","4-7","8-15","16+"]}
    for t, s, l, wc in directives:
        by_bucket[bucket(wc)].append((t, s, l))
    for b in ["1","2-3","4-7","8-15","16+"]:
        out.write(f"\n===== BUCKET {b} (n={len(by_bucket[b])}) =====\n")
        # spread samples across the corpus
        items = by_bucket[b]
        step = max(1, len(items)//40)
        for t, s, l in items[::step][:40]:
            t1 = t.replace("\n", " ⏎ ")
            out.write(f"[{s}:{l}] {t1[:160]}\n")
print("\nSAMPLES_WRITTEN\t_b1_samples.txt")
