#!/usr/bin/env python3
"""Build feed.xml (podcast RSS) and index.html from episodes.json + the MP3s in episodes/.

Usage (from the repo root):  python3 tools/build_feed.py
Episodes whose MP3 isn't in the repo yet are skipped with a warning, so the feed can grow
one file at a time. Needs ffprobe for durations.
"""
import email.utils, html, json, os, subprocess, sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def probe_seconds(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path], capture_output=True, text=True).stdout
    return int(float(out.strip()))


def hms(s):
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def rfc2822(day, hour=7):
    dt = datetime.fromisoformat(day).replace(hour=hour, tzinfo=timezone.utc)
    return email.utils.format_datetime(dt)


def main():
    data = json.load(open(os.path.join(ROOT, "episodes.json")))
    show, base = data["show"], data["show"]["base_url"].rstrip("/") + "/"
    items, cards, missing = [], [], []
    for ep in sorted(data["episodes"], key=lambda e: e["n"], reverse=True):
        path = os.path.join(ROOT, ep["file"])
        if not os.path.exists(path):
            missing.append(ep["file"]); continue
        size, secs = os.path.getsize(path), probe_seconds(path)
        url = base + ep["file"]
        notes = ep["summary"] + ("\n\nScript and sources: " + ep["script"] if ep.get("script") else "")
        notes_html = f"<p>{escape(ep['summary'])}</p>" + (
            f'<p><a href="{escape(ep["script"])}">Script and sources</a></p>' if ep.get("script") else "")
        items.append(f"""    <item>
      <title>{escape(f"{ep['n']}. {ep['title']}")}</title>
      <itunes:title>{escape(ep['title'])}</itunes:title>
      <itunes:episode>{ep['n']}</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <guid isPermaLink="false">history-slop-ep{ep['n']:02d}</guid>
      <pubDate>{rfc2822(ep['date'])}</pubDate>
      <enclosure url="{escape(url)}" length="{size}" type="audio/mpeg"/>
      <itunes:duration>{secs}</itunes:duration>
      <description><![CDATA[{notes_html}]]></description>
      <itunes:summary>{escape(notes)}</itunes:summary>
      <itunes:explicit>false</itunes:explicit>
      {f'<link>{escape(ep["script"])}</link>' if ep.get('script') else ''}
    </item>""")
        cards.append(f"""<article>
  <div class="num">{ep['n']:02d}</div>
  <div class="body">
    <h2>{html.escape(ep['title'])}</h2>
    <p>{html.escape(ep['summary'])}</p>
    <audio controls preload="none" src="{html.escape(ep['file'])}"></audio>
    <div class="meta">{hms(secs)} · {size / 1e6:.0f} MB · <a href="{html.escape(ep['file'])}" download>MP3</a></div>
  </div>
</article>""")

    now = email.utils.format_datetime(datetime.now(timezone.utc))
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{escape(show['title'])}</title>
    <link>{escape(base)}</link>
    <atom:link href="{escape(base)}feed.xml" rel="self" type="application/rss+xml"/>
    <description>{escape(show['summary'])}</description>
    <language>{show['language']}</language>
    <lastBuildDate>{now}</lastBuildDate>
    <itunes:author>{escape(show['author'])}</itunes:author>
    <itunes:summary>{escape(show['summary'])}</itunes:summary>
    <itunes:image href="{escape(base)}cover.jpg"/>
    <image><url>{escape(base)}cover.jpg</url><title>{escape(show['title'])}</title><link>{escape(base)}</link></image>
    <itunes:category text="{escape(show['category'])}"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:type>episodic</itunes:type>
    <itunes:block>Yes</itunes:block>
{chr(10).join(items)}
  </channel>
</rss>
"""
    open(os.path.join(ROOT, "feed.xml"), "w").write(feed)

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(show['title'])}</title>
<link rel="alternate" type="application/rss+xml" title="{html.escape(show['title'])}" href="feed.xml">
<link rel="icon" href="cover.jpg">
<style>
:root{{--bg:#16140f;--panel:#211e17;--ink:#efe6d2;--dim:#a39a86;--red:#c8432b;--line:#3a352a}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 Georgia,'Times New Roman',serif}}
main{{max-width:760px;margin:0 auto;padding:24px 16px 64px}}
header{{display:flex;gap:20px;align-items:center;margin-bottom:28px}}
header img{{width:132px;height:132px;border-radius:6px;flex:none}}
h1{{margin:0 0 6px;font-size:28px;letter-spacing:.02em}}header p{{margin:0;color:var(--dim);font-size:15px}}
.feed{{display:flex;gap:8px;margin:18px 0 32px}}
.feed input{{flex:1;min-width:0;background:var(--panel);border:1px solid var(--line);color:var(--ink);padding:10px;border-radius:6px;font:14px ui-monospace,monospace}}
.feed button{{background:var(--red);color:#fff;border:0;border-radius:6px;padding:0 16px;font:600 14px system-ui,sans-serif}}
article{{display:flex;gap:16px;padding:20px 0;border-top:1px solid var(--line)}}
.num{{font-size:28px;color:var(--red);min-width:2ch}}.body{{flex:1;min-width:0}}
h2{{margin:0 0 6px;font-size:20px}}article p{{margin:0 0 12px;color:var(--dim)}}
audio{{width:100%}}.meta{{font:13px system-ui,sans-serif;color:var(--dim);margin-top:6px}}a{{color:var(--ink)}}
@media (max-width:520px){{header{{flex-direction:column;align-items:flex-start}}}}
</style></head><body><main>
<header><img src="cover.jpg" alt="History Slop cover">
<div><h1>{html.escape(show['title'])}</h1><p>{html.escape(show['summary'])}</p></div></header>
<div class="feed"><input id="u" readonly value="{html.escape(base)}feed.xml" aria-label="Feed URL">
<button onclick="navigator.clipboard&&navigator.clipboard.writeText(document.getElementById('u').value);this.textContent='Copied'">Copy feed</button></div>
{chr(10).join(cards) or '<p>No episodes uploaded yet.</p>'}
</main></body></html>
"""
    open(os.path.join(ROOT, "index.html"), "w").write(page)
    print(f"feed.xml + index.html: {len(items)} episode(s)")
    for m in missing:
        print("  missing (skipped):", m, file=sys.stderr)


if __name__ == "__main__":
    main()
