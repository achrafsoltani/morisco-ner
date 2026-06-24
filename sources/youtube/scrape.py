"""YouTube comment scraper via the YouTube Data API v3 (conforms to the BaseScraper framework).

  export YOUTUBE_API_KEY=...            # gitignored .env
  python sources/youtube/scrape.py --query "darija maroc" --max-videos 30 --min-latin 0.6
  python sources/youtube/scrape.py --channels UCxxxx UCyyyy --max-videos 20
  python sources/youtube/scrape.py --videos VIDID1 VIDID2

Quota: 10,000 units/day; commentThreads.list = 1 unit / up to 100 comments. ToS: do not store API data > 30 days and do
not redistribute it — release stand-off + IDs + sample + models only. (Legacy v1 collector: ./yt_collect.py.)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Iterator


def _scrub(msg: str) -> str:
    """Strip the API key out of any message before logging (it appears in request URLs)."""
    return re.sub(r"key=[\w-]+", "key=REDACTED", str(msg))

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # sources/ on path
from base import BaseScraper, Record  # noqa: E402


class YouTubeScraper(BaseScraper):
    name = "youtube"

    def _client(self):
        from googleapiclient.discovery import build  # local import
        key = os.environ.get("YOUTUBE_API_KEY") or os.environ.get("YT_API_KEY")
        if not key:
            raise SystemExit("set YOUTUBE_API_KEY (keep it in a gitignored .env)")
        return build("youtube", "v3", developerKey=key, cache_discovery=False)

    def _uploads_playlist(self, yt, ident: str) -> str | None:
        """Resolve a channel id (UC...) OR an @handle to its uploads playlist id."""
        if ident.startswith("UC"):
            resp = yt.channels().list(part="contentDetails", id=ident).execute()
        else:
            # handle (with or without leading @)
            resp = yt.channels().list(part="contentDetails", forHandle=ident).execute()
        items = resp.get("items", [])
        if not items:
            print(f"[youtube] could not resolve channel '{ident}'", file=sys.stderr)
            return None
        return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def _playlist_videos(self, yt, playlist_id: str, limit: int) -> list[str]:
        vids, token = [], None
        while len(vids) < limit:
            resp = yt.playlistItems().list(
                part="contentDetails", playlistId=playlist_id, maxResults=50, pageToken=token).execute()
            vids += [it["contentDetails"]["videoId"] for it in resp.get("items", [])]
            token = resp.get("nextPageToken")
            if not token:
                break
            self.throttle()
        return vids[:limit]

    def _search_videos(self, yt, query: str, limit: int) -> list[str]:
        vids, token = [], None
        while len(vids) < limit:
            resp = yt.search().list(
                part="id", q=query, type="video", maxResults=50,
                relevanceLanguage="ar", regionCode="MA", pageToken=token).execute()
            vids += [it["id"]["videoId"] for it in resp.get("items", []) if it["id"].get("videoId")]
            token = resp.get("nextPageToken")
            if not token:
                break
            self.throttle()
        return vids[:limit]

    def _video_comments(self, yt, video_id: str, max_per: int) -> Iterator[Record]:
        token = None
        got = 0
        while got < max_per:
            try:
                resp = yt.commentThreads().list(
                    part="snippet", videoId=video_id, maxResults=100,
                    textFormat="plainText", pageToken=token, order="relevance").execute()
            except Exception as e:  # noqa: BLE001  (comments disabled / quota / not found)
                print(f"[youtube] {video_id} comments unavailable: {_scrub(e)[:160]}", file=sys.stderr)
                return
            for it in resp.get("items", []):
                sn = it["snippet"]["topLevelComment"]["snippet"]
                cid = it["snippet"]["topLevelComment"]["id"]
                yield Record(
                    text=sn.get("textDisplay", ""),
                    source="youtube",
                    source_id=f"{video_id}:{cid}",
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    meta={"like_count": sn.get("likeCount", 0)},
                )
                got += 1
                if got >= max_per:
                    break
            token = resp.get("nextPageToken")
            if not token:
                break
            self.throttle()

    def collect(self, query: str | None = None, channels: list[str] | None = None,
                channel_set: str | None = None, videos: list[str] | None = None, max_videos: int = 20,
                max_comments_per_video: int = 200, **_) -> Iterator[Record]:
        yt = self._client()
        vids: list[str] = list(videos or [])
        if query:
            vids += self._search_videos(yt, query, max_videos)

        idents: list[str] = list(channels or [])
        if channel_set:
            import channels as ch_registry  # sources/youtube/channels.py (script dir on sys.path)
            idents += ch_registry.identifiers(ch_registry.get_set(channel_set))
        for ch in dict.fromkeys(idents):  # dedup, keep order
            pl = self._uploads_playlist(yt, ch)
            if pl:
                vids += self._playlist_videos(yt, pl, max_videos)
        vids = list(dict.fromkeys(vids))
        if not vids:
            raise SystemExit("no videos: pass --query, --channels, --channel-set, or --videos")
        # Memoise scraped video IDs so repeat runs only spend quota on NEW videos.
        self.out_dir.mkdir(parents=True, exist_ok=True)
        done_path = self.out_dir / ".done_videos.txt"
        done = set(done_path.read_text().split()) if done_path.exists() else set()
        new_vids = [v for v in vids if v not in done]
        print(f"[youtube] {len(vids)} videos found, {len(new_vids)} new "
              f"(skipping {len(vids) - len(new_vids)} already scraped)", file=sys.stderr)
        with done_path.open("a", encoding="utf-8") as dfh:
            for vid in new_vids:
                yield from self._video_comments(yt, vid, max_comments_per_video)
                dfh.write(vid + "\n")
                dfh.flush()
                self.throttle()


def main() -> None:
    ap = argparse.ArgumentParser(description="Scrape YouTube comments (Data API v3)")
    g = ap.add_argument_group("video selection (combine freely)")
    g.add_argument("--query", default=None, help="search query (region MA, lang ar)")
    g.add_argument("--channels", nargs="*", default=None, help="channel IDs (UC...) or @handles -> their uploads")
    g.add_argument("--channel-set", default=None,
                   help="curated set from channels.py: news | media | creators | music | all")
    g.add_argument("--videos", nargs="*", default=None, help="explicit video IDs")
    ap.add_argument("--max-videos", type=int, default=20, help="videos per channel/query")
    ap.add_argument("--max-comments", type=int, default=200, help="per video")
    ap.add_argument("--limit", type=int, default=None, help="cap total comments written")
    ap.add_argument("--min-latin", type=float, default=0.0)
    ap.add_argument("--rate", type=float, default=2.0)
    ap.add_argument("--list-channels", metavar="SET",
                    help="print the channels in a set (news|media|creators|music|all) and exit")
    args = ap.parse_args()

    if args.list_channels:
        import channels as ch_registry
        for e in ch_registry.get_set(args.list_channels):
            ident = e.get("channel_id") or e.get("handle") or "(unresolved)"
            print(f"{ident:28}  {e['name']:28}  {e['note']}")
        return

    YouTubeScraper(rate=args.rate).run(
        limit=args.limit, min_latin=args.min_latin,
        query=args.query, channels=args.channels, channel_set=args.channel_set, videos=args.videos,
        max_videos=args.max_videos, max_comments_per_video=args.max_comments)


if __name__ == "__main__":
    main()
