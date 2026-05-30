#!/usr/bin/env python3
"""Task 3 probe — locate EVERY 'interrupted by user' occurrence across the
contexts transcripts, classify whether it's a genuine standalone user-turn
interrupt (a real correction event) or an embedded/tool-permission artifact,
and dump the in-flight action + following correction for the genuine ones.

Reuses the loader/role logic from _extract.py.
"""
import os, glob, importlib.util

spec = importlib.util.spec_from_file_location(
    "ex", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_extract.py"))
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)

SRC = os.path.expanduser('~/.claude/projects/-Users-utilityserver-github-claude-contexts')
VARIANTS = ['[Request interrupted by user]',
            '[Request interrupted by user for tool use]']


def classify_user_interrupt(e):
    """Is this event a standalone user message whose text IS an interrupt marker?"""
    if ex.role_of(e) != 'user':
        return None
    t = ex.get_text(e).strip()
    for v in VARIANTS:
        if t == v:
            return v
    # also: text that STARTS with the marker (user typed-over content appended)
    for v in VARIANTS:
        if t.startswith(v):
            return v + '+typed'
    return None


def main():
    out = []
    for f in sorted(glob.glob(os.path.join(SRC, '*.jsonl'))):
        if os.path.basename(f).startswith('agent-'):
            continue
        uuid = ex.short(os.path.splitext(os.path.basename(f))[0])
        evs = ex.load_events(f)
        users = [i for i, e in enumerate(evs) if ex.is_genuine_user(e)]
        uidx = {ev: k for k, ev in enumerate(users)}
        # every event whose serialized text mentions the marker
        hits = []
        for i, e in enumerate(evs):
            txt = ex.get_text(e) or ''
            if 'interrupted by user' in txt:
                hits.append(i)
        if not hits:
            continue
        out.append(f"=== [{uuid}] {len(evs)} events, {len(users)} user msgs ===")
        for i in hits:
            e = evs[i]
            role = ex.role_of(e)
            is_tr = ex.is_tool_result(e)
            cls = classify_user_interrupt(e)
            kind = ('GENUINE-USER-INTERRUPT(%s)' % cls if cls
                    else ('tool_result-embedded' if is_tr
                          else 'embedded-in-%s' % role))
            out.append(f"  e#{i} role={role} -> {kind}")
            out.append(f"    text: {ex.trunc(ex.get_text(e), 160)}")
            if cls:
                # in-flight: nearest preceding assistant
                a_idx = next((j for j in range(i-1, -1, -1)
                              if ex.role_of(evs[j]) == 'assistant'), None)
                if a_idx is not None:
                    out.append(f"    IN-FLIGHT a#e{a_idx} text: {ex.trunc(ex.get_text(evs[a_idx]),160)}")
                    out.append(f"    IN-FLIGHT tools: {ex.tool_uses(evs[a_idx])}")
                # instruction: genuine user before the assistant turn
                base = (a_idx if a_idx is not None else i) - 1
                instr_j = next((j for j in range(base, -1, -1)
                                if ex.is_genuine_user(evs[j])), None)
                if instr_j is not None:
                    out.append(f"    INSTRUCTION (t{uidx.get(instr_j)}): {ex.trunc(ex.get_text(evs[instr_j]),160)}")
                # correction: next genuine user after marker
                corr_j = next((j for j in range(i+1, len(evs))
                               if ex.is_genuine_user(evs[j])), None)
                if corr_j is not None:
                    out.append(f"    CORRECTION (t{uidx.get(corr_j)}): {ex.trunc(ex.get_text(evs[corr_j]),200)}")
            out.append('')
    dump = '\n'.join(out)
    dp = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_probe_dump.txt')
    open(dp, 'w', encoding='utf-8').write(dump)
    print(dump)


if __name__ == '__main__':
    main()
