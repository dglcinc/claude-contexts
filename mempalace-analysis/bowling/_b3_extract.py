#!/usr/bin/env python3
"""B3 — Interrupt + correction corpus over raw bowling-league-tracker transcripts.

Full 570-session scan. For every `[Request interrupted` marker:
  (1) capture the IN-FLIGHT assistant action (the last assistant message before
      the marker — its tool_use names + brief input summary, and/or text snippet),
  (2) capture the NEXT genuine David message after the marker (same is_human
      filter as B1/B2), chronological by line.
Emits a tab-delimited dump for hand theme-classification + the headline counts.
Citations are <8-char-session>:<line>.
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


def summarize_assistant(msg):
    """Return (kind, detail) for an assistant message dict.
    kind = comma-joined tool names, or 'text' if only prose.
    detail = brief input summary / text snippet."""
    content = msg.get("content")
    tools = []
    texts = []
    if isinstance(content, list):
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                name = b.get("name", "?")
                inp = b.get("input", {}) or {}
                bits = []
                if name == "Bash":
                    bits.append(str(inp.get("command", ""))[:120])
                elif name in ("Read", "Edit", "Write", "Glob", "Grep"):
                    bits.append(str(inp.get("file_path") or inp.get("pattern") or inp.get("path") or "")[:80])
                elif name == "AskUserQuestion":
                    qs = inp.get("questions") or []
                    if qs and isinstance(qs, list) and isinstance(qs[0], dict):
                        bits.append(str(qs[0].get("question", ""))[:120])
                elif name == "ExitPlanMode":
                    bits.append(str(inp.get("plan", ""))[:120])
                elif name in ("Task", "Agent"):
                    bits.append(str(inp.get("description") or inp.get("prompt") or "")[:100])
                else:
                    bits.append(json.dumps(inp)[:100])
                tools.append((name, " ".join(b for b in bits if b)))
            elif b.get("type") == "text":
                txt = b.get("text", "").strip()
                if txt:
                    texts.append(txt)
    elif isinstance(content, str):
        if content.strip():
            texts.append(content.strip())
    if tools:
        kind = ",".join(t[0] for t in tools)
        detail = " | ".join(f"{t[0]}: {t[1]}" for t in tools if t[1])
        if texts:
            # assistant said something then called a tool
            snippet = texts[-1][:160]
            detail = (detail + f"  [said: {snippet}]") if detail else f"[said: {snippet}]"
        return kind, detail
    if texts:
        return "text", texts[-1][:240]
    return "?", ""


def oneline(s):
    return s.replace("\n", " ⏎ ").strip()


events = []  # dicts
files = sorted(f for f in os.listdir(SRC) if UUID_RE.match(f))
total_human = 0

for fn in files:
    sess = fn[:-6]
    short = sess[:8]
    rows = []
    with open(os.path.join(SRC, fn)) as fh:
        for ln, raw in enumerate(fh, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except Exception:
                continue
            rows.append((ln, obj))

    # index human messages for forward lookup + count
    for ln, obj in rows:
        if obj.get("type") == "user":
            msg = obj.get("message")
            if isinstance(msg, dict) and msg.get("role") == "user" and not obj.get("isMeta"):
                txt = extract_text(msg.get("content"))
                if is_human(txt):
                    total_human += 1

    # find interrupt markers
    for i, (ln, obj) in enumerate(rows):
        if obj.get("type") != "user":
            continue
        msg = obj.get("message")
        if not isinstance(msg, dict):
            continue
        txt = extract_text(msg.get("content"))
        if INTERRUPT not in txt:
            continue
        # in-flight: last assistant message before this line
        kind, detail = "(none)", ""
        for j in range(i - 1, -1, -1):
            pobj = rows[j][1]
            if pobj.get("type") == "assistant":
                pmsg = pobj.get("message")
                if isinstance(pmsg, dict):
                    kind, detail = summarize_assistant(pmsg)
                break
        # next genuine David message after the interrupt
        corr_text, corr_line = "", None
        for j in range(i + 1, len(rows)):
            nobj = rows[j][1]
            if nobj.get("type") != "user":
                continue
            nmsg = nobj.get("message")
            if not isinstance(nmsg, dict) or nmsg.get("role") != "user" or nobj.get("isMeta"):
                continue
            ntxt = extract_text(nmsg.get("content"))
            if is_human(ntxt):
                corr_text = SECRET_RE.sub("[REDACTED-API-KEY]", ntxt.strip())
                corr_line = rows[j][0]
                break
        events.append({
            "sess": short, "iline": ln, "kind": kind,
            "detail": SECRET_RE.sub("[REDACTED-API-KEY]", detail),
            "corr": corr_text, "cline": corr_line,
        })

print(f"FILES_PROCESSED\t{len(files)}")
print(f"TOTAL_HUMAN_MESSAGES\t{total_human}")
print(f"TOTAL_INTERRUPTS\t{len(events)}")
terminal = sum(1 for e in events if not e["corr"])
print(f"TERMINAL_NO_FOLLOWUP\t{terminal}")
print(f"CORRECTED\t{len(events) - terminal}")
if total_human:
    print(f"INTERRUPTS_PER_100_HUMAN\t{100.0*len(events)/total_human:.1f}")

# kind histogram
from collections import Counter
kc = Counter(e["kind"] for e in events)
print("\n== IN-FLIGHT KIND HISTOGRAM ==")
for k, c in kc.most_common():
    print(f"{c}\t{k}")

# sessions
sc = Counter(e["sess"] for e in events)
print("\n== INTERRUPTS PER SESSION ==")
for s, c in sc.most_common():
    print(f"{c}\t{s}")

out_path = os.path.join(os.path.dirname(__file__), "_b3_dump.txt")
with open(out_path, "w") as out:
    for e in events:
        out.write(f"[{e['sess']}:{e['iline']}] INFLIGHT={e['kind']} :: {oneline(e['detail'])}\n")
        if e["corr"]:
            out.write(f"    -> CORR [{e['sess']}:{e['cline']}] {oneline(e['corr'])}\n")
        else:
            out.write(f"    -> (terminal, no follow-up)\n")
        out.write("\n")
print(f"\nDUMP_WRITTEN\t{out_path}")
