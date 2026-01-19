
path = 'app.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
fixed = False
while i < len(lines):
    # Check for the sequence by stripped content
    if i + 4 < len(lines):
        l1 = lines[i].strip()
        l2 = lines[i+1].strip()
        l3 = lines[i+2].strip()
        l4 = lines[i+3].strip()
        l5 = lines[i+4].strip()
        
        if l1 == ')' and l2 == '"""' and l3 == ')' and l4 == '"""' and l5 == ')':
            # Found it.
            # We want to keep l1, l2, and l5 (but logically l5 is the closing of the function call)
            # Actually, l1, l2 are the closing of the SQL string.
            # l3, l4 are the duplicates.
            # l5 is the closing of the execute call.
            
            # So append l1, l2
            new_lines.append(lines[i])
            new_lines.append(lines[i+1])
            # Skip l3 (i+2) and l4 (i+3)
            # Append l5 (i+4) is handled in next iterations? No, we need to jump.
            # Wait, if I append l1, l2, then I should skip i+2, i+3.
            # i should become i+4?
            # lines[i+4] will be processed in next loop iteration if I set i = i + 4
            i += 4
            fixed = True
            print("Fixed duplicate block at line", i)
            continue

    new_lines.append(lines[i])
    i += 1

if fixed:
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("File saved.")
else:
    print("Pattern not found.")
