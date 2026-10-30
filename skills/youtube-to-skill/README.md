# youtube-to-skill

Turns YouTube videos, playlists or whole channels into reusable agent skills, or answers questions about a video. Text only: it fetches transcripts, never video or audio. Scripts declare their own dependencies, so `uv run` sets them up. Needs [uv](https://docs.astral.sh/uv/).

Usage and the full pipeline are in [skills/youtube-to-skill/SKILL.md](skills/youtube-to-skill/SKILL.md). Previously its own repo, [back1ply/youtube-to-skill](https://github.com/back1ply/youtube-to-skill).

## Limits

- No captions, no transcript. There is no Whisper fallback. If captions exist only in other languages, `fetch_video.py --translate` uses YouTube's machine translation (approximate wording).
- Slides and on-screen code aren't in transcripts. Skills list these as known gaps instead of guessing.
- Auto-captions have no speaker labels, so interview advice usually isn't attributed to a speaker.
- YouTube rate-limits bulk fetching. Raise `--delay`, or set `YTDLP_COOKIES_BROWSER=chrome`.
- Generated skills are derived from the creator's work. Credit them, and keep skills private unless the video's license allows sharing.

## Credits

Formerly [fcc-skills](https://github.com/back1ply/fcc-skills) (freeCodeCamp courses only). Ideas borrowed (not code) from [EftikharAzim/youtube-to-skill](https://github.com/EftikharAzim/youtube-to-skill) (timestamp citations, quick-answer and search modes, cost check before big runs), [beast-ofcourse/SWE-pro-Agents](https://github.com/beast-ofcourse/SWE-pro-Agents) ("no repeatable process" outcome, command safety review) and [yfe404/youtube-to-skill](https://github.com/yfe404/youtube-to-skill) (checking named tools are still current).
