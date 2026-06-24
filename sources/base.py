"""Scraper framework for MoriscoNER data collection.

Each concrete scraper subclasses BaseScraper and implements collect() -> Iterator[Record].
BaseScraper.run() normalises, dedups (by lowercased text hash), tags Latin-script ratio, optionally
Latin-filters, and writes JSONL to sources/<name>/raw/<name>.jsonl.

Binding: raw/ is gitignored. Bulk raw text is NEVER redistributed (site ToS / YouTube API ToS / GDPR).
Only the downstream stand-off corpus + IDs + a documented sample + trained models are released.
"""
from __future__ import annotations

import abc
import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterator

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

_ARABIC = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
_LATIN = re.compile(r"[A-Za-z]")
_WS = re.compile(r"\s+")


def latin_ratio(text: str) -> float:
    lat = len(_LATIN.findall(text))
    ar = len(_ARABIC.findall(text))
    tot = lat + ar
    return lat / tot if tot else 0.0


def norm(text: str) -> str:
    return _WS.sub(" ", (text or "").replace(" ", " ")).strip()


@dataclass
class Record:
    text: str
    source: str
    source_id: str
    url: str = ""
    latin_ratio: float = 0.0
    meta: dict = field(default_factory=dict)


class BaseScraper(abc.ABC):
    name: str = "base"

    def __init__(self, out_dir: Path | None = None, rate: float = 1.0):
        # rate = requests/sec target (throttle = 1/rate seconds between hits)
        self.out_dir = Path(out_dir) if out_dir else Path(__file__).resolve().parent / self.name / "raw"
        self.rate = rate
        self._seen: set[str] = set()

    def throttle(self) -> None:
        if self.rate > 0:
            time.sleep(1.0 / self.rate)

    @abc.abstractmethod
    def collect(self, **kwargs) -> Iterator[Record]:
        """Yield raw Record objects for this source."""

    def run(self, limit: int | None = None, min_latin: float = 0.0, **kwargs) -> int:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        out = self.out_dir / f"{self.name}.jsonl"
        n = 0
        with out.open("w", encoding="utf-8") as fh:
            for rec in self.collect(**kwargs):
                rec.text = norm(rec.text)
                if not rec.text:
                    continue
                h = hashlib.sha1(rec.text.lower().encode("utf-8")).hexdigest()
                if h in self._seen:
                    continue
                self._seen.add(h)
                rec.latin_ratio = round(latin_ratio(rec.text), 3)
                if rec.latin_ratio < min_latin:
                    continue
                fh.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
                n += 1
                if limit and n >= limit:
                    break
        print(f"[{self.name}] wrote {n} unique records -> {out}")
        return n
