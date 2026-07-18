import ast, re

def _val(s):
    s=s.strip()
    if s in ('true','True'): return True
    if s in ('false','False'): return False
    if s in ('[]','{}'): return ast.literal_eval(s)
    if s.startswith('[') or s.startswith('{'):
        t=re.sub(r'([\{,]\s*)([A-Za-z_][\w-]*)(\s*:)', r'\1"\2"\3', s)
        t=re.sub(r':\s*([A-Za-z_][\w-]*)(?=[,}])', lambda m: ': '+repr(m.group(1)), t)
        if s.startswith('[') and ':' not in s:
            t='['+','.join(repr(x.strip()) for x in s.strip('[]').split(',') if x.strip())+']'
        return ast.literal_eval(t)
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')): return s[1:-1]
    try: return int(s)
    except ValueError: pass
    try: return float(s)
    except ValueError: return s

def safe_load(stream):
    text=stream.read() if hasattr(stream,'read') else stream
    if isinstance(text, bytes): text=text.decode()
    else: text=str(text)
    lines=[ln.rstrip() for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith('#')]
    root={}; stack=[(-1, root)]
    for i,ln in enumerate(lines):
        indent=len(ln)-len(ln.lstrip(' ')); s=ln.strip()
        while stack and indent<=stack[-1][0]: stack.pop()
        parent=stack[-1][1]
        if s.startswith('- '):
            item=_val(s[2:])
            if isinstance(parent,list): parent.append(item)
            continue
        if ':' in s:
            k,v=s.split(':',1); k=k.strip(); v=v.strip()
            if v:
                parent[k]=_val(v)
            else:
                # choose list if next meaningful line is list item
                nxt=''
                for later in lines[i+1:]:
                    if len(later)-len(later.lstrip(' '))>indent: nxt=later.strip(); break
                parent[k]=[] if nxt.startswith('- ') else {}
                stack.append((indent,parent[k]))
    return root

def safe_dump(data, sort_keys=False):
    return repr(data)
