# History Slop

The Anna & Rune history podcast, published as a podcast feed with GitHub Pages.

- Feed: https://chakker-git.github.io/History-Slop/feed.xml
- Web player: https://chakker-git.github.io/History-Slop/

## Layout

| Path | What it is |
|---|---|
| `episodes.json` | Show metadata and one entry per episode (title, date, file, script link, show notes) |
| `episodes/NN-slug.mp3` | The 64k mono MP3s from `podcast_tts.py encode` (chapters embedded) |
| `cover.jpg` | 3000×3000 cover art, made by `tools/make_cover.py` |
| `tools/build_feed.py` | Rebuilds `feed.xml` and `index.html` from `episodes.json` and the MP3s |
| `feed.xml`, `index.html` | Generated; don't edit by hand |

## Adding an episode

1. Copy the 64k MP3 to `episodes/NN-slug.mp3`.
2. Add an entry to `episodes.json`.
3. Run `python3 tools/build_feed.py`, then commit and push. Podcast apps pick the episode up on their next refresh.

Keep each MP3 under 100 MB, which is GitHub's per-file limit. An hour at 64k is about 29 MB.

## Notes

- `<itunes:block>Yes</itunes:block>` keeps the show out of the Apple directory. You subscribe by URL. It's unlisted, not private: anyone with the URL can listen.
- Episode dates in `episodes.json` are placeholders that keep the order right. Edit them if you care.
- Script links point at claude.ai artifacts, which are private to their owner unless shared.
