import os

app_path = r'c:\Users\Administrator\capstone\MomCare-App-by-MomTech-1\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    ln = i + 1
    # Target lines 90-125 for migration block
    if 90 <= ln <= 125:
        # Use 4-space increments relative to 4-space function body
        # Line 90/123/124/125 are level 1 (4 spaces)
        if ln in [90, 123, 124, 125]:
            new_lines.append('    ' + line.lstrip())
        # Lines 91, 92, 93, 98, 103, 108, 113, 118 are level 2 (8 spaces)
        elif ln in [91, 92, 93, 98, 103, 108, 113, 118]:
            new_lines.append('        ' + line.lstrip())
        # Lines 94, 96, 99, 101, 104, 106, 109, 111, 114, 116, 119, 121 are level 3 (12 spaces)
        elif ln in [94, 96, 99, 101, 104, 106, 109, 111, 114, 116, 119, 121]:
            new_lines.append('            ' + line.lstrip())
        # Lines 95, 97, 100, 102, 105, 107, 110, 112, 115, 117, 120, 122 are level 4 (16 spaces)
        elif ln in [95, 97, 100, 102, 105, 107, 110, 112, 115, 117, 120, 122]:
            new_lines.append('                ' + line.lstrip())
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(app_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Repaired schema migration indentation.")
