import os

app_path = r'c:\Users\Administrator\capstone\MomCare-App-by-MomTech-1\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1093, 1105):
    line = lines[i]
    print(f"{i+1:4}: {''.join(f'{ord(c):02X} ' for c in line)}")
