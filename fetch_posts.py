"""Забирает последние посты публичного канала и сохраняет в posts.json.
Старые посты из posts.json не теряются: новые просто добавляются сверху."""
import html, json, re, urllib.request
from pathlib import Path

CHANNEL = "grotescvilla"
OUT = Path(__file__).resolve().parent.parent / "posts.json"
KEEP = 100  # сколько постов хранить

req = urllib.request.Request(f"https://t.me/s/{CHANNEL}", headers={"User-Agent": "Mozilla/5.0"})
page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

def clean(fragment):
    fragment = re.sub(r"<br\s*/?>", "\n", fragment)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return html.unescape(fragment).strip()

fresh = []
for chunk in page.split("tgme_widget_message_wrap")[1:]:
    pid = re.search(r'data-post="([^"]+)"', chunk)
    date = re.search(r'<time[^>]*datetime="([^"]+)"', chunk)
    if not (pid and date):
        continue
    text = re.search(r'tgme_widget_message_text[^>]*>(.*?)</div>', chunk, re.S)
    photo = re.search(r"tgme_widget_message_photo_wrap[^>]*background-image:url\('([^']+)'\)", chunk)
    fresh.append({
        "id": pid.group(1),
        "date": date.group(1),
        "text": clean(text.group(1)) if text else "",
        "photo": photo.group(1) if photo else "",
    })

old = json.loads(OUT.read_text("utf-8")) if OUT.exists() else []
merged = {p["id"]: p for p in old}
merged.update({p["id"]: p for p in fresh})
posts = sorted(merged.values(), key=lambda p: p["date"], reverse=True)[:KEEP]

OUT.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", "utf-8")
print(f"Постов в файле: {len(posts)} (новых за проход: {len(fresh)})")
