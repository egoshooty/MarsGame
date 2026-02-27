from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class HttpClientError(RuntimeError):
    pass


def post_json(url: str, payload: dict[str, Any], timeout: int = 8) -> Any:
    req = Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise HttpClientError(f"POST {url} failed: {exc}") from exc


def get_json(url: str, timeout: int = 5) -> Any:
    req = Request(url=url, headers={"Accept": "application/json"}, method="GET")
    try:
        with urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise HttpClientError(f"GET {url} failed: {exc}") from exc
