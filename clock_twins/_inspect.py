"""Inspect dino.fandom infobox HTML structure."""
import sys, re
sys.path.insert(0, '.')
import build_dinosaur_data as b

d = b.fetch_page('Tyrannosaurus')
html = d['parse']['text']['*']

# Save full HTML
with open('_trex_full.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('full html len:', len(html))

# Find aside
m = re.search(r'<aside[^>]*portable-infobox.*?</aside>', html, re.DOTALL)
if not m:
    print('NO ASIDE FOUND')
    # Search for any infobox keyword
    for kw in ['portable-infobox', 'infobox', 'pi-title', 'pi-image']:
        idx = html.find(kw)
        print(f'  "{kw}" at index: {idx}')
    # Inspect around index 79
    print()
    print('=== context around index 79 (first 1200 chars after) ===')
    print(html[79:1300])
    print()
    print('=== first 8 <img> tags ===')
    for i, im in enumerate(re.finditer(r'<img[^>]+>', html[:8000])):
        print(f'[{i}]', im.group(0)[:280])
        if i >= 7: break
    sys.exit(0)

box = m.group(0)
print('aside len:', len(box))
print('=== first 1200 chars ===')
print(box[:1200])
print()
print('=== first <img> in aside ===')
img_m = re.search(r'<img[^>]+>', box)
if img_m:
    print(img_m.group(0)[:400])
