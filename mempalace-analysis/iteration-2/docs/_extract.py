#!/usr/bin/env python3
"""Task 4 (wing_docs) — mechanical extraction for F-A and F-C.

Reads the raw docs transcripts (main-thread UUID *.jsonl only, excluding
agent-*.jsonl sidechains) from the two sources enumerated in 00-inventory.md
(signalk-wilhelmsk-docs = attended npm-publish-prep; wilhelm-docs-ralph =
delegated ralph build) and emits a structured dump the analyst classifies by
judgment. The two sources carry a mode tag so the synthesis can keep attended
vs delegated separable (inventory flag 4).

Robust to both transcript on-disk shapes (newline-delimited JSON or a single
pretty-printed JSON array) and to both event schemas (content under
message.content / message.role, or flattened top-level content / role).
"""
import os, sys, glob, json

SOURCES = [
    ('attended',  os.path.expanduser('~/.claude/projects/-Users-utilityserver-github-signalk-wilhelmsk-docs')),
    ('delegated', os.path.expanduser('~/.claude/projects/-Users-utilityserver-github-wilhelm-docs-ralph')),
]
MARK = '[Request interrupted by user]'


def load_events(path):
    data = open(path, encoding='utf-8', errors='replace').read()
    if data.lstrip().startswith('['):
        try:
            j = json.loads(data)
            if isinstance(j, list):
                return j
        except Exception:
            pass
    evs = []
    for ln in data.splitlines():
        ln = ln.strip()
        if ln:
            try:
                evs.append(json.loads(ln))
            except Exception:
                pass
    return evs


def _content(e):
    m = e.get('message')
    if isinstance(m, dict) and 'content' in m:
        return m['content']
    return e.get('content')


def role_of(e):
    if not isinstance(e, dict):
        return '?'
    m = e.get('message')
    if isinstance(m, dict) and m.get('role'):
        return m['role']
    return e.get('role') or e.get('type') or '?'


def get_text(e):
    c = _content(e)
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        out = []
        for b in c:
            if isinstance(b, dict):
                t = b.get('type')
                if t == 'text':
                    out.append(b.get('text', ''))
            elif isinstance(b, str):
                out.append(b)
        return ' '.join(p for p in out if p)
    return ''


def tool_uses(e):
    c = _content(e)
    res = []
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get('type') == 'tool_use':
                name = b.get('name')
                inp = b.get('input', {}) or {}
                hint = ''
                if isinstance(inp, dict):
                    for k in ('file_path', 'path', 'command', 'pattern', 'query',
                              'old_string', 'description'):
                        if k in inp and isinstance(inp[k], str):
                            hint = inp[k].replace('\n', ' ')[:80]
                            break
                res.append(f"{name}({hint})" if hint else f"{name}")
    return res


def is_tool_result(e):
    c = _content(e)
    if isinstance(c, list) and c:
        return all(isinstance(b, dict) and b.get('type') == 'tool_result' for b in c)
    return False


def is_interrupt(e):
    return role_of(e) == 'user' and get_text(e).strip() == MARK


def is_genuine_user(e):
    if role_of(e) != 'user':
        return False
    if is_interrupt(e) or is_tool_result(e):
        return False
    return get_text(e).strip() != ''


def trunc(s, n):
    s = ' '.join((s or '').split())
    return s if len(s) <= n else s[:n] + '…'


def short(uuid):
    return uuid.split('-')[0][:8]


def main():
    files = []
    for tag, src in SOURCES:
        for f in sorted(glob.glob(os.path.join(src, '*.jsonl'))):
            if os.path.basename(f).startswith('agent-'):
                continue
            files.append((tag, f))

    out = []
    out.append('# docs extraction dump (Task 4)')
    out.append('')
    out.append('turn_index = 0-based position within the ORDERED list of genuine '
               'user messages in the session (tool_results and the interrupt '
               'marker excluded). raw event index also shown as e#.')
    out.append('')
    out.append('## DELIVERABLE 1 — SESSION MANIFEST')
    out.append('')

    sessions = []
    for tag, f in files:
        uuid = os.path.splitext(os.path.basename(f))[0]
        evs = load_events(f)
        users = [i for i, e in enumerate(evs) if is_genuine_user(e)]
        ints = [i for i, e in enumerate(evs) if is_interrupt(e)]
        import time
        mt = time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(f)))
        first_user = get_text(evs[users[0]]) if users else ''
        sessions.append({'tag': tag, 'f': f, 'uuid': uuid, 'evs': evs,
                         'users': users, 'ints': ints, 'mt': mt})
        out.append(f"- [{short(uuid)}] {tag} | events={len(evs)} "
                   f"user_msgs={len(users)} interrupts={len(ints)} date={mt}")
        out.append(f"    first_user: {trunc(first_user, 200)}")
    out.append('')

    # ---- DELIVERABLE 2: F-A triples ----
    out.append('## DELIVERABLE 2 — F-A INTERRUPT TRIPLES')
    out.append('')
    total_int = 0
    for s in sessions:
        evs = s['evs']
        users = s['users']
        uidx_of = {ev: k for k, ev in enumerate(users)}  # event-index -> user-turn
        for i in s['ints']:
            total_int += 1
            # in-flight assistant action = nearest preceding assistant event
            a_idx = None
            for j in range(i - 1, -1, -1):
                if role_of(evs[j]) == 'assistant':
                    a_idx = j
                    break
            a_text = get_text(evs[a_idx]) if a_idx is not None else ''
            a_tools = tool_uses(evs[a_idx]) if a_idx is not None else []
            # preceding user instruction (genuine user before the assistant turn)
            instr = ''
            instr_turn = None
            base = (a_idx if a_idx is not None else i) - 1
            for j in range(base, -1, -1):
                if is_genuine_user(evs[j]):
                    instr = get_text(evs[j])
                    instr_turn = uidx_of.get(j)
                    break
            # correction = next genuine user after the marker
            corr = ''
            for j in range(i + 1, len(evs)):
                if is_genuine_user(evs[j]):
                    corr = get_text(evs[j])
                    break
            out.append(f"### [{short(s['uuid'])}] e#{i} (instr@turn {instr_turn})")
            out.append(f"- INSTRUCTION: {trunc(instr, 200)}")
            out.append(f"- IN-FLIGHT TEXT: {trunc(a_text, 200)}")
            out.append(f"- IN-FLIGHT TOOLS: {a_tools}")
            out.append(f"- CORRECTION: {trunc(corr, 300)}")
            out.append('')
    out.insert(out.index('## DELIVERABLE 2 — F-A INTERRUPT TRIPLES') + 1,
               f"\nTotal interrupts (exact-string MARK) found across docs: {total_int}")

    # ---- DELIVERABLE 3: F-C diagnostic material ----
    out.append('## DELIVERABLE 3 — F-C PER-SESSION USER-MESSAGE TIMELINES')
    out.append('')
    out.append('(All genuine user messages per session, in order, with turn '
               'index. Analyst classifies precise/vague and identifies '
               'diagnostic threads.)')
    out.append('')
    for s in sessions:
        evs = s['evs']
        out.append(f"### [{short(s['uuid'])}] {s['tag']} — {len(s['users'])} user msgs, "
                   f"{len(s['ints'])} interrupts, {s['mt']}")
        for k, ev in enumerate(s['users']):
            out.append(f"  t{k} (e#{ev}): {trunc(get_text(evs[ev]), 200)}")
        out.append('')

    dump = '\n'.join(out)
    dp = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_extract_dump.txt')
    with open(dp, 'w', encoding='utf-8') as fh:
        fh.write(dump)
    print(dump)


if __name__ == '__main__':
    main()
