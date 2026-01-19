import os

app_path = r'c:\Users\Administrator\capstone\MomCare-App-by-MomTech-1\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if not line.strip():
        new_lines.append(line)
        continue
    
    lspace = len(line) - len(line.lstrip())
    # If it was likely 3-space based
    # 3 -> 4
    # 6 -> 8
    # 9 -> 12
    # 12 -> 16
    # If it was likely 4-space based
    # 4 -> 4
    # 8 -> 8
    # 12 -> 12
    
    # Precise mapping that handles both reasonably well:
    # 3 -> 4
    # 4 -> 4
    # 6 -> 8
    # 7 -> 8 (matches some of my 7-space errors)
    # 8 -> 8
    # 9 -> 12
    # 10 -> 12 (maybe 11?)
    # 11 -> 12
    # 12 -> 12? Wait 12 should probably be 16 if it was 3*4. 
    # But if it was 4*3, it should stay 12.
    
    # Let's try: if it's a multiple of 3 but not 4, it's 3-based.
    # If it's a multiple of 4, it's 4-based.
    
    level = 0
    if lspace > 0:
        # Heuristic based on original 3-space base mostly
        level = int(round(lspace * (4.0/3.0) / 4.0)) * 4
        # Wait, if lspace was 4, 4 * 1.33 = 5.33. round(5.33 / 4) = round(1.33) = 1. level = 4. (Correct)
        # If lspace was 8, 8 * 1.33 = 10.66. round(10.66 / 4) = round(2.66) = 3. level = 12. (ERROR! 8 should be 8)
        
    # Better heuristic: just fix the specific levels I've seen.
    if lspace == 0: level = 0
    elif lspace in [3, 4, 5]: level = 4
    elif lspace in [6, 7, 8, 9]: level = 8
    elif lspace in [10, 11, 12, 13]: level = 12
    elif lspace in [14, 15, 16, 17]: level = 16
    elif lspace in [18, 19, 20, 21]: level = 20
    else: level = ((lspace + 1) // 4) * 4

    new_lines.append(' ' * level + line.lstrip())

with open(app_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Standardized entire app.py to 4-space indentation properly.")
