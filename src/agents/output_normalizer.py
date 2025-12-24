from __future__ import annotations

import re
import inspect
from typing import Any
from urllib.parse import urlparse

from .ctdatenight_agents import FINAL_SETTINGS, _rewrite_ctdatenight_links_in_html


def _is_ctdatenight_host(host: str) -> bool:
    if not host:
        return False
    host = host.lower()
    return host in FINAL_SETTINGS["allowed_domains"] or host.endswith(".ctdatenight.com")


def normalize_links(obj: Any) -> Any:
    """Recursively rewrite CTDateNight links in strings, HTML anchor hrefs, and URL occurrences.

    - HTML anchor hrefs are rewritten using `_rewrite_ctdatenight_links_in_html`.
    - Plain URLs (http/https) pointing to CTDateNight are replaced with `FINAL_SETTINGS['redirect_url']`.
    - Relative links are treated as CTDateNight and rewritten when found in HTML anchors.
    """
    if isinstance(obj, bytes):
        try:
            obj = obj.decode("utf-8")
        except Exception:
            obj = obj.decode("utf-8", errors="replace")

    if isinstance(obj, str):
        # First rewrite any anchor hrefs in HTML
        s = _rewrite_ctdatenight_links_in_html(obj)

        # Replace bare absolute URLs that point to CTDateNight
        def _url_repl(m: re.Match) -> str:
            url = m.group(0)
            try:
                host = urlparse(url).hostname or ""
            except Exception:
                host = ""
            if _is_ctdatenight_host(host):
                return FINAL_SETTINGS["redirect_url"]
            return url

        s = re.sub(r"https?://[^\s<'\"]+", _url_repl, s)
        return s

    if isinstance(obj, dict):
        return {k: normalize_links(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [normalize_links(i) for i in obj]

    if isinstance(obj, tuple):
        return tuple(normalize_links(list(obj)))

    if isinstance(obj, set):
        return {normalize_links(i) for i in obj}

    return obj


def output_normalizer(func):
    """Decorator: normalize any CTDateNight links in function return value.

    Supports both synchronous and asynchronous functions.
    """

    if inspect.iscoroutinefunction(func):
        async def async_wrapper(*args, **kwargs):
            res = await func(*args, **kwargs)
            return normalize_links(res)

        return async_wrapper

    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        return normalize_links(res)

    return wrapper


__all__ = ["normalize_links", "output_normalizer"]
