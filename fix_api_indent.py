import os

app_path = r'c:\Users\Administrator\capstone\MomCare-App-by-MomTech-1\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # If line starts with 7 spaces and contains cur.execute or conn.close, change to 4 spaces
    if line.startswith('       ') and ('cur.execute' in line or 'conn.close()' in line):
        new_lines.append('    ' + line.lstrip())
    else:
        new_lines.append(line)

with open(app_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Standardized API indentation to 4 spaces.")
