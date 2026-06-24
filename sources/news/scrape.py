"""Config-driven Moroccan news-site comment scraper (Playwright headless).

Add a Moroccan site = add one SiteConfig entry. Comment sections of news sites are entity-dense
(politicians, places, institutions, clubs) and a register the YouTube/social well lacks.

  python sources/news/scrape.py --site hespress --sections politique societe --max-articles 40 --min-latin 0.6

NOTE on selectors: news DOMs change. Each SiteConfig's selectors are best-effort and must be verified against the live
page (open the site, inspect a comment node, fix the CSS). The framework is correct; selectors are the maintenance surface.
Respect each site's robots.txt / ToS; comments are personal data (GDPR) — never publish raw text or usernames.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # sources/ on path
from base import UA, BaseScraper, Record  # noqa: E402


@dataclass
class SiteConfig:
    key: str
    base_url: str
    sections: dict[str, str]              # name -> listing path
    article_link_selector: str            # links on a section listing page
    comment_selector: str                 # comment-text nodes on an article page
    article_url_contains: str = ""        # keep only hrefs containing this (filters nav/ads)
    wait_ms: int = 1500                    # let comments render/lazy-load
    locale: str = "ar-MA"


SITES: dict[str, SiteConfig] = {
    # Hespress — Morocco's largest news portal; comments heavily in Darija (Latin + Arabic).
    "hespress": SiteConfig(
        key="hespress",
        base_url="https://www.hespress.com",
        sections={
            "politique": "/politique",
            "societe": "/societe",
            "sport": "/sport",
            "economie": "/economie",
            "art-et-culture": "/art-et-culture",
            "regions": "/regions",
        },
        article_link_selector="h3.card-title a, a.stretched-link, h2.card-title a",
        comment_selector="div.comment_text, .comment-text, ul.comment-list .text, li.comment p",
        article_url_contains="hespress.com",
    ),
    # Goud.ma — popular Darija-leaning tabloid.
    "goud": SiteConfig(
        key="goud",
        base_url="https://www.goud.ma",
        sections={"akhbar": "/category/akhbar", "fdihat": "/category/fdihat", "riyada": "/category/riyada"},
        article_link_selector="h2.entry-title a, h3.entry-title a, a.post-thumbnail",
        comment_selector="ol.commentlist li .comment-content p, .comment-text",
        article_url_contains="goud.ma",
    ),
    # Le360 (Arabic edition) — major outlet with active comments.
    "le360": SiteConfig(
        key="le360",
        base_url="https://ar.le360.ma",
        sections={"politique": "/politique", "societe": "/societe", "sport": "/sport"},
        article_link_selector="article a, h3 a, a.card-link",
        comment_selector=".comment-content, .comment__body, div.comment p",
        article_url_contains="le360.ma",
    ),
}


class NewsScraper(BaseScraper):
    def __init__(self, site: SiteConfig, **kw):
        self.site = site
        self.name = site.key
        super().__init__(**kw)

    def collect(self, sections: list[str] | None = None, max_articles: int = 40,
                headless: bool = True, **_) -> Iterator[Record]:
        from playwright.sync_api import sync_playwright  # local import: no hard dep in base

        site = self.site
        secs = sections or list(site.sections)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=headless)
            ctx = browser.new_context(user_agent=UA, locale=site.locale)
            page = ctx.new_page()

            # 1) discover article URLs from each section listing
            urls: list[str] = []
            for s in secs:
                path = site.sections.get(s)
                if not path:
                    continue
                try:
                    page.goto(site.base_url + path, timeout=60000, wait_until="domcontentloaded")
                    self.throttle()
                    hrefs = page.eval_on_selector_all(
                        site.article_link_selector, "els => els.map(e => e.href).filter(Boolean)")
                except Exception as e:  # noqa: BLE001
                    print(f"[{self.name}] section {s} failed: {e}", file=sys.stderr)
                    continue
                if site.article_url_contains:
                    hrefs = [h for h in hrefs if site.article_url_contains in h]
                urls.extend(hrefs[:max_articles])
            urls = list(dict.fromkeys(urls))  # dedup, keep order
            print(f"[{self.name}] discovered {len(urls)} articles across {len(secs)} sections", file=sys.stderr)

            # 2) pull comments from each article
            for u in urls:
                try:
                    page.goto(u, timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_timeout(site.wait_ms)
                    texts = page.eval_on_selector_all(
                        site.comment_selector, "els => els.map(e => e.innerText)")
                except Exception as e:  # noqa: BLE001
                    print(f"[{self.name}] article failed {u}: {e}", file=sys.stderr)
                    continue
                for i, t in enumerate(texts):
                    if t and t.strip():
                        yield Record(text=t, source=self.name, source_id=f"{u}#c{i}",
                                     url=u, meta={"kind": "news_comment"})
                self.throttle()
            browser.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="Scrape Moroccan news-site comments (Playwright)")
    ap.add_argument("--site", required=True, choices=list(SITES), help="which configured site")
    ap.add_argument("--sections", nargs="*", default=None, help="subset of sections (default: all)")
    ap.add_argument("--max-articles", type=int, default=40, help="articles per section")
    ap.add_argument("--limit", type=int, default=None, help="cap total comments written")
    ap.add_argument("--min-latin", type=float, default=0.0, help="keep comments with >= this Latin-script ratio")
    ap.add_argument("--rate", type=float, default=1.0, help="requests/sec throttle")
    ap.add_argument("--no-headless", action="store_true", help="show the browser (debug selectors)")
    args = ap.parse_args()

    scraper = NewsScraper(SITES[args.site], rate=args.rate)
    scraper.run(limit=args.limit, min_latin=args.min_latin,
                sections=args.sections, max_articles=args.max_articles, headless=not args.no_headless)


if __name__ == "__main__":
    main()
