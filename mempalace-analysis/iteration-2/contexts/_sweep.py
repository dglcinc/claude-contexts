import json, glob, os, re
os.chdir(os.path.expanduser('~/.claude/projects/-Users-utilityserver-github-claude-contexts'))
pat = re.compile(r"(still|not work|doesn.?t|isn.?t|broken|wrong|fail|error|what gives|something.s (funny|off|wrong)|not right|stuck|no it|that.?s not|revert|undo)", re.I)
for f in sorted(glob.glob('*.jsonl')):
    if os.path.basename(f).startswith('agent-'):
        continue
    evs = [json.loads(l) for l in open(f) if l.strip()]
    for i, e in enumerate(evs):
        m = e.get('message')
        role = (m.get('role') if isinstance(m, dict) and m.get('role') else e.get('type', '?'))
        if role != 'user':
            continue
        c = m.get('content') if isinstance(m, dict) else e.get('content')
        if isinstance(c, str):
            txt = c
        elif isinstance(c, list):
            txt = ' '.join(b.get('text', '') for b in c if isinstance(b, dict) and b.get('type') == 'text')
        else:
            txt = ''
        txt = txt.strip()
        if not txt or txt.startswith('<') or 'Base directory for this skill' in txt:
            continue
        if pat.search(txt):
            print(f"{f[:8]} e#{i}: {' '.join(txt.split())[:170]}")
