import os

app_path = r'c:\Users\Administrator\capstone\MomCare-App-by-MomTech-1\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if not line.strip():
        new_lines.append(line)
        continue
    
    # Simple heuristic to convert 3-space increments to 4-space increments
    # and clean up my mess of 5/7/8 spaces.
    lspace = len(line) - len(line.lstrip())
    # Guess level
    # 0 -> 0
    # 3-5 -> 4
    # 6-9 -> 8
    # 10-13 -> 12
    # 14-17 -> 16
    # 18-21 -> 20
    level = 0
    if lspace > 0:
        if lspace <= 2: level = 0 # tiny indents probably shouldn't exist
        elif lspace <= 5: level = 4
        elif lspace <= 9: level = 8
        elif lspace <= 13: level = 12
        elif lspace <= 17: level = 16
        elif lspace <= 21: level = 20
        else: level = ((lspace + 1) // 4) * 4 # fallback
    
    new_lines.append(' ' * level + line.lstrip())

with open(app_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Standardized entire app.py to 4-space indentation.")
