import subprocess
import os
import re

chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
html_path = os.path.abspath('dashboard/test_automation.html')
cmd = [
    chrome,
    '--headless=new',
    '--no-sandbox',
    '--disable-gpu',
    '--virtual-time-budget=5000',
    '--dump-dom',
    f'file:///{html_path}'
]
res = subprocess.run(cmd, capture_output=True, text=True)
dom = res.stdout

m = re.search(r'<div id="test-output"[^>]*>([\s\S]*?)</div>', dom)
if m:
    content = m.group(1).strip()
    print("Test output div content:\n")
    print(content)
else:
    print("Could not find test-output div.")
