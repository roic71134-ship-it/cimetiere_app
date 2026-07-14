from pathlib import Path
root = Path('frontend/views')
files = []
for path in root.rglob('*.py'):
    text = path.read_text(encoding='utf-8')
    if 'ft.TextField(' not in text:
        continue
    lines = text.splitlines()
    i = 0
    missing = []
    while i < len(lines):
        line = lines[i]
        if 'ft.TextField(' in line:
            block = line
            open_parens = line.count('(') - line.count(')')
            i2 = i + 1
            while open_parens > 0 and i2 < len(lines):
                block += '\n' + lines[i2]
                open_parens += lines[i2].count('(') - lines[i2].count(')')
                i2 += 1
            if 'color=' not in block:
                missing.append((i + 1, line.strip()))
            i = i2
        else:
            i += 1
    if missing:
        files.append((path, missing))
for path, missing in files:
    print(path)
    for ln, content in missing:
        print(' ', ln, content)
print('TOTAL', len(files), 'files with missing color')
