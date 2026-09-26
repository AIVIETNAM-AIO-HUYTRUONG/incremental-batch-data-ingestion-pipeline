from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set

from common.retry_utils import retry_on_exception

from .config import YoutubeConfig
from .filters import (
    is_likely_english,
    is_within_duration,
    parse_iso8601_duration,
)


@retry_on_exception(
    (Exception,),
    max_attempts=3,
    base_delay=3.0,
)
def search_page(
    youtube,
    query: str,
    published_after: str,
    relevance_language: str,
    max_results: int,
    page_token: Optional[str] = None,
):
    """Gọi YouTube search.list()."""
    return (
        youtube.search()
        .list(
            q=query,
            type="video",
            part="id",
            publishedAfter=published_after,
            order="date",
            relevanceLanguage=relevance_language,
            maxResults=min(50, max_results),
            pageToken=page_token,
        )
        .execute()
    )


@retry_on_exception(
    (Exception,),
    max_attempts=3,
    base_delay=3.0,
)
def get_video_details(
    youtube,
    video_ids: List[str],
):
    """Gọi YouTube videos.list() để lấy thông tin chi tiết."""
    return (
        youtube.videos()
        .list(
            part="snippet,contentDetails",
            id=",".join(video_ids),
        )
        .execute()
    )


def get_recent_videos(
    youtube,
    skip_ids: Set[str],
    config: YoutubeConfig,
    logger,
) -> List[str]:
    """
    Tìm và lọc video YouTube mới.

    Pipeline:

        search.list()
            ↓
        candidate video IDs
            ↓
        videos.list()
            ↓
        language filter
            ↓
        duration filter
            ↓
        video URLs
    """
    published_after = (
        datetime.now(timezone.utc)
        - timedelta(days=config.days_back)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    video_urls: List[str] = []

    page_token: Optional[str] = None

    deadline = (
        datetime.now(timezone.utc)
        + timedelta(
            seconds=config.search_timeout_seconds
        )
    )

    while (
        len(video_urls) < config.max_results
        and datetime.now(timezone.utc) < deadline
    ):
        response = search_page(
            youtube=youtube,
            query=config.query,
            published_after=published_after,
            relevance_language=config.relevance_language,
            max_results=config.max_results * 4,
            page_token=page_token,
        )

        candidate_ids = [
            item["id"]["videoId"]
            for item in response.get("items", [])
            if item.get("id", {}).get("videoId")
            not in skip_ids
        ]

        if candidate_ids:
            details = get_video_details(
                youtube,
                candidate_ids,
            )

            details_by_id = {
                item["id"]: item
                for item in details.get("items", [])
            }

            for video_id in candidate_ids:
                item = details_by_id.get(video_id)

                if not item:
                    continue

                snippet = item["snippet"]

                duration_seconds = parse_iso8601_duration(
                    item["contentDetails"]["duration"]
                )

                if (
                    config.require_english
                    and not is_likely_english(snippet)
                ):
                    continue

                if not is_within_duration(
                    duration_seconds,
                    config.min_duration_seconds,
                    config.max_duration_seconds,
                ):
                    continue

                video_urls.append(
                    f"https://www.youtube.com/watch?v={video_id}"
                )

                if len(video_urls) >= config.max_results:
                    break

        next_page_token = response.get("nextPageToken")

        if (
            not next_page_token
            or len(video_urls) >= config.max_results
        ):
            break

        page_token = next_page_token

    logger.info(
        "Tìm thấy %d video phù hợp sau khi lộc.",
        len(video_urls),
    )

    return video_urls