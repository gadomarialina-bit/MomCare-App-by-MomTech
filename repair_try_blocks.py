import re

app_path = r'c:\Users\Administrator\capstone\MomCare-App-by-MomTech-1\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
current_try_indent = -1
for i, line in enumerate(lines):
    # Detect try block
    try_match = re.match(r'^(\s*)try:', line)
    if try_match:
        current_try_indent = len(try_match.group(1))
        new_lines.append(line)
        continue
    
    # Detect except block (resets indent tracing)
    except_match = re.match(r'^(\s*)except', line)
    if except_match:
        # We don't Reset immediately because we want to catch calls inside except too
        # But we align subsequent calls to try_indent + 4 usually
        new_lines.append(line)
        continue
    
    # Detect end of function or next route (resets tracing)
    if re.match(r'^@app\.route', line) or re.match(r'^def ', line):
        current_try_indent = -1
        new_lines.append(line)
        continue

    # If we are inside an active try context and see a mis-indented db call
    if current_try_indent != -1:
        # Check if line contains database call and is indented too little (usually 4 or 5 spaces)
        if ('cur.execute' in line or 'conn.close()' in line or 'conn.commit()' in line):
            # If it's flattened to 4/5 spaces but the try was at 4+, it's wrong.
            # Most of my damage was moving things to 4 spaces.
            trimmed = line.lstrip()
            # If the trimmed line starts with cur.execute etc.
            if trimmed.startswith('cur.execute') or trimmed.startswith('conn.close') or trimmed.startswith('conn.commit'):
                # Heuristic: if it's currently at 4 or 5 spaces, move it to current_try_indent + 4
                current_indent = len(line) - len(trimmed)
                if current_indent in [4, 5]:
                    new_lines.append(' ' * (current_try_indent + 4) + trimmed)
                    continue

    new_lines.append(line)

with open(app_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Auto-repaired many try/except indentation mismatches.")
