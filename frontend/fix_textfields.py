from pathlib import Path

root = Path("frontend/views")
modified = []
for path in root.rglob("*.py"):
    text = path.read_text(encoding="utf-8")
    if "ft.TextField(" not in text:
        continue
    lines = text.splitlines(keepends=True)
    out = []
    changed = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if "ft.TextField(" in line:
            start = i
            block = line
            open_parens = line.count("(") - line.count(")")
            i += 1
            while open_parens > 0 and i < len(lines):
                line2 = lines[i]
                block += line2
                open_parens += line2.count("(") - line2.count(")")
                i += 1
            if "color=" not in block:
                new_first = lines[start].replace("ft.TextField(", "ft.TextField(color=\"black\", ", 1)
                out.append(new_first)
                out.extend(lines[start+1:i])
                changed = True
            else:
                out.extend(lines[start:i])
        else:
            out.append(line)
            i += 1
    if changed:
        path.write_text(''.join(out), encoding='utf-8')
        modified.append(str(path))

print(f"modified {len(modified)} files")
for p in modified:
    print(p)
