"""Shared helpers: stable ids for article URLs and filename slugs. Imported by the other scripts."""

import hashlib
import re
from urllib.parse import urlsplit, urlunsplit

DROP_PARAMS = re.compile(r"^(utm_\w+|ref|fbclid|gclid|mc_cid|mc_eid)=", re.IGNORECASE)


def normalize_url(url: str) -> str:
    """Lower-case host, drop fragment, tracking params and trailing slash, so one page gets one id."""
    parts = urlsplit(url.strip())
    query = "&".join(p for p in parts.query.split("&") if p and not DROP_PARAMS.match(p))
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower() or "https", parts.netloc.lower(), path, query, ""))


def slugify(text: str, limit: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:limit].rstrip("-") or "x"


def article_id(url: str) -> str:
    """<host>_<path-slug>_<6-char hash>, e.g. martinfowler.com_articles-feature-toggles-html_3f2a1c."""
    norm = normalize_url(url)
    parts = urlsplit(norm)
    host = parts.netloc.removeprefix("www.")
    digest = hashlib.sha1(norm.encode("utf-8")).hexdigest()[:6]
    return f"{host}_{slugify(parts.path + ' ' + parts.query, 50)}_{digest}"
