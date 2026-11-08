from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import re
import time
import urllib.parse
import urllib.request

from .models import Source, stable_id


class RetrievalError(RuntimeError):
    pass


def _get_json(url: str, timeout: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "EdgeX-Agents/0.1 research client"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # network, protocol, and JSON errors all need a retryable boundary
        raise RetrievalError(f"Could not retrieve {url}: {exc}") from exc


@dataclass
class SemanticScholarClient:
    limit: int = 8

    def search(self, query: str) -> list[Source]:
        params = urllib.parse.urlencode({
            "query": query,
            "limit": self.limit,
            "fields": "title,authors,venue,year,abstract,url,externalIds,citationCount",
        })
        payload = _get_json(f"https://api.semanticscholar.org/graph/v1/paper/search?{params}")
        output: list[Source] = []
        for item in payload.get("data", []):
            external = item.get("externalIds") or {}
            doi = external.get("DOI")
            arxiv_id = external.get("ArXiv")
            url = item.get("url") or (f"https://doi.org/{doi}" if doi else "")
            title = (item.get("title") or "").strip()
            if not title or not url:
                continue
            output.append(Source(
                source_id=stable_id("src", doi or arxiv_id or title.lower()),
                title=title,
                url=url,
                authors=[a.get("name", "") for a in item.get("authors", []) if a.get("name")],
                year=item.get("year"),
                venue=item.get("venue"),
                abstract=item.get("abstract"),
                doi=doi,
                arxiv_id=arxiv_id,
                citation_count=item.get("citationCount"),
                query=query,
            ))
        return output


@dataclass
class ArxivClient:
    limit: int = 8

    def search(self, query: str) -> list[Source]:
        params = urllib.parse.urlencode({"search_query": f"all:{query}", "start": 0, "max_results": self.limit})
        request = urllib.request.Request(
            f"https://export.arxiv.org/api/query?{params}",
            headers={"User-Agent": "EdgeX-Agents/0.1 research client"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                xml = response.read().decode("utf-8")
        except Exception as exc:
            raise RetrievalError(f"Could not retrieve arXiv results: {exc}") from exc
        entries = re.findall(r"<entry>(.*?)</entry>", xml, flags=re.DOTALL)
        output: list[Source] = []
        for entry in entries:
            def tag(name: str) -> str:
                match = re.search(rf"<{name}>(.*?)</{name}>", entry, flags=re.DOTALL)
                return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""

            title, abstract, entry_id = tag("title"), tag("summary"), tag("id")
            if not title or not entry_id:
                continue
            arxiv_id = entry_id.rsplit("/", 1)[-1]
            authors = re.findall(r"<author>\s*<name>(.*?)</name>", entry, flags=re.DOTALL)
            published = tag("published")
            output.append(Source(
                source_id=stable_id("src", arxiv_id), title=title, url=entry_id,
                authors=[re.sub(r"\s+", " ", x).strip() for x in authors],
                year=int(published[:4]) if published[:4].isdigit() else None,
                abstract=abstract, arxiv_id=arxiv_id, query=query,
            ))
        return output


def merge_sources(existing: list[Source], new_sources: list[Source]) -> list[Source]:
    by_key: dict[str, Source] = {}
    for source in [*existing, *new_sources]:
        key = (source.doi or source.arxiv_id or source.title).lower().strip()
        by_key[key] = source
    return sorted(by_key.values(), key=lambda source: (source.year or 0, source.title), reverse=True)


def search_both(query: str, limit: int = 8) -> list[Source]:
    """Best-effort retrieval. A failed provider is recorded by the caller, not hidden."""
    found: list[Source] = []
    errors: list[str] = []
    for client in (SemanticScholarClient(limit), ArxivClient(limit)):
        try:
            found.extend(client.search(query))
        except RetrievalError as exc:
            errors.append(str(exc))
        time.sleep(0.2)
    if not found and errors:
        raise RetrievalError("; ".join(errors))
    return merge_sources([], found)
