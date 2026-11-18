"""
scripts/capture_qa_screenshots.py
Captures high-resolution visual QA screenshots using Chrome Headless:
1. Landing Page (Desktop 1440x900)
2. Top 10 Batters (Desktop 1440x900)
3. Top 10 Bowlers (Desktop 1440x900)
4. Player Profile Modal (Desktop 1440x900)
5. Mobile View (Mobile 390x844)
6. Tablet View (Tablet 768x1024)

Also synchronizes all screenshots to the artifact directory.
"""

import os
import subprocess
import shutil

chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
html_base = os.path.abspath('dashboard/index.html').replace('\\', '/')
artifact_dir = r'C:\Users\mohdh\.gemini\antigravity\brain\0a5c9430-2afb-4204-8921-0fc7f597ec0a'

os.makedirs('dashboard', exist_ok=True)
os.makedirs(artifact_dir, exist_ok=True)

targets = [
    {
        'name': 'screenshot_landing.png',
        'url': f'file:///{html_base}#overview',
        'width': 1440,
        'height': 900
    },
    {
        'name': 'screenshot_top_batters.png',
        'url': f'file:///{html_base}#top-batters',
        'width': 1440,
        'height': 900
    },
    {
        'name': 'screenshot_top_bowlers.png',
        'url': f'file:///{html_base}#top-bowlers',
        'width': 1440,
        'height': 900
    },
    {
        'name': 'screenshot_player_profile.png',
        'url': f'file:///{html_base}?modal=7016&disc=Batting',
        'width': 1440,
        'height': 900
    },
    {
        'name': 'screenshot_mobile.png',
        'url': f'file:///{html_base}#overview',
        'width': 390,
        'height': 844
    },
    {
        'name': 'screenshot_tablet.png',
        'url': f'file:///{html_base}#overview',
        'width': 768,
        'height': 1024
    }
]

for t in targets:
    out_path = os.path.abspath(f"dashboard/{t['name']}")
    cmd = [
        chrome,
        '--headless=new',
        '--no-sandbox',
        '--disable-gpu',
        f"--window-size={t['width']},{t['height']}",
        '--virtual-time-budget=3000',
        f'--screenshot={out_path}',
        t['url']
    ]
    print(f"Capturing {t['name']} ({t['width']}x{t['height']})...")
    subprocess.run(cmd, check=True)
    size = os.path.getsize(out_path)
    print(f"Captured {t['name']} (Size: {size:,} bytes)")
    
    # Copy to artifact directory
    art_path = os.path.join(artifact_dir, t['name'])
    shutil.copy2(out_path, art_path)
    print(f"Copied to artifact dir: {art_path}")

print("\nAll 6 QA screenshots captured and synchronized successfully!")
