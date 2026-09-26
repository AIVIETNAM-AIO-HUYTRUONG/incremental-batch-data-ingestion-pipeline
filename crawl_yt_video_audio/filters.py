import re
from typing import Any, Dict


ISO8601_DURATION_RE = re.compile(
    r"P"
    r"(?:(?P<days>\d+)D)?"
    r"T"
    r"(?:(?P<hours>\d+)H)?"
    r"(?:(?P<minutes>\d+)M)?"
    r"(?:(?P<seconds>\d+)S)?"
)


def parse_iso8601_duration(duration: str) -> int:
    """
    Chuyển YouTube ISO 8601 duration thành số giây.

    Ví dụ:
        PT12M34S -> 754
        PT1H2M10S -> 3730

    Args:
        duration: Chuỗi duration từ YouTube API.

    Returns:
        int: Duration tính bằng giây.
        Trả về 0 nếu không parse được.
    """
    if not duration:
        return 0

    match = ISO8601_DURATION_RE.fullmatch(duration)

    if not match:
        return 0

    parts = match.groupdict()

    days = int(parts["days"] or 0)
    hours = int(parts["hours"] or 0)
    minutes = int(parts["minutes"] or 0)
    seconds = int(parts["seconds"] or 0)

    return (
        days * 86400
        + hours * 3600
        + minutes * 60
        + seconds
    )


def is_likely_english(
    snippet: Dict[str, Any],
) -> bool:
    """
    Heuristic xác định video có khả năng là tiếng Anh.

    Ưu tiên:
        1. defaultAudioLanguage
        2. defaultLanguage

    Nếu API không cung cấp language:
        sử dụng tỷ lệ ký tự alphabet ASCII trong title.

    Args:
        snippet: YouTube video snippet.

    Returns:
        bool: True nếu video có khả năng là tiếng Anh.
    """
    for field_name in (
        "defaultAudioLanguage",
        "defaultLanguage",
    ):
        language = snippet.get(field_name)

        if language:
            return language.lower().startswith("en")

    title = snippet.get("title", "")

    if not title:
        return False

    letters = sum(
        1
        for char in title
        if char.isalpha()
    )

    if letters == 0:
        return False

    ascii_letters = sum(
        1
        for char in title
        if char.isascii() and char.isalpha()
    )

    return (ascii_letters / letters) > 0.85


def is_within_duration(
    duration_seconds: int,
    min_duration: int,
    max_duration: int,
) -> bool:
    """Kiểm tra video có nằm trong khoảng duration cho phép hay không."""
    return min_duration <= duration_seconds <= max_duration


def is_youtube_shorts(
    duration_seconds: int,
    webpage_url: str,
) -> bool:
    """
    Xác định video có khả năng là YouTube Shorts.

    Args:
        duration_seconds: Duration của video.
        webpage_url: URL thực tế của video.

    Returns:
        bool: True nếu có khả năng là Shorts.
    """
    return (
        duration_seconds <= 60
        or "/shorts/" in webpage_url
    )