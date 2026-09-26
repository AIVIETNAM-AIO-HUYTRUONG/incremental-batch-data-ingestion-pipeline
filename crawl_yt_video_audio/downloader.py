from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from common.state_store import save_state

from .config import OUTPUT_ROOT, YoutubeConfig
from .filters import is_youtube_shorts


def extract_video_id(url: str) -> str:
    """Extract video ID từ YouTube URL."""
    return (
        url.split("v=")[-1]
        .split("&")[0]
    )


def prepare_output_directories(
    base_dir: Path,
) -> None:
    """Tạo các thư mục output cần thiết."""
    for sub_dir in (
        "video",
        "audio",
        "info",
        "subs",
    ):
        (
            base_dir / sub_dir
        ).mkdir(
            parents=True,
            exist_ok=True,
        )


def download_video_info(
    url: str,
    base_dir: Path,
    config: YoutubeConfig,
):
    """
    Lấy metadata và subtitle trước khi tải media.

    Returns:
        dict: Metadata từ yt-dlp.
    """
    import yt_dlp

    options = {
        "skip_download": True,
        "writeinfojson": True,
        "writesubtitles": True,
        "subtitleslangs": config.subtitle_langs,
        "subtitlesformat": "vtt",
        "outtmpl": str(
            base_dir / "info" / "%(id)s.%(ext)s"
        ),
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        return ydl.extract_info(
            url,
            download=True,
        )


def move_subtitles(
    video_id: str,
    base_dir: Path,
    record: Dict[str, Any],
) -> None:
    """Di chuyển subtitle từ info/ sang subs/."""
    for subtitle_file in (
        base_dir / "info"
    ).glob(
        f"{video_id}.*.vtt"
    ):
        target = (
            base_dir
            / "subs"
            / subtitle_file.name
        )

        subtitle_file.replace(target)

        record["subtitle"] = str(
            target.relative_to(OUTPUT_ROOT)
        )


def save_info_reference(
    video_id: str,
    base_dir: Path,
    record: Dict[str, Any],
) -> None:
    """Lưu relative path của info.json vào state."""
    info_json = (
        base_dir
        / "info"
        / f"{video_id}.info.json"
    )

    if info_json.exists():
        record["info"] = str(
            info_json.relative_to(OUTPUT_ROOT)
        )


def download_video(
    url: str,
    video_id: str,
    base_dir: Path,
    config: YoutubeConfig,
    record: Dict[str, Any],
) -> None:
    """Download video MP4."""
    import yt_dlp

    options = {
        "format": config.video_format,
        "outtmpl": str(
            base_dir / "video" / "%(id)s.%(ext)s"
        ),
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

    video_path = (
        base_dir
        / "video"
        / f"{video_id}.mp4"
    )

    if video_path.exists():
        record["video"] = str(
            video_path.relative_to(OUTPUT_ROOT)
        )


def download_audio(
    url: str,
    video_id: str,
    base_dir: Path,
    config: YoutubeConfig,
    record: Dict[str, Any],
) -> None:
    """Download audio M4A."""
    import yt_dlp

    options = {
        "format": config.audio_format,
        "outtmpl": str(
            base_dir / "audio" / "%(id)s.%(ext)s"
        ),
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

    audio_path = (
        base_dir
        / "audio"
        / f"{video_id}.m4a"
    )

    if audio_path.exists():
        record["audio"] = str(
            audio_path.relative_to(OUTPUT_ROOT)
        )


def download_assets(
    urls: List[str],
    base_dir: Path,
    config: YoutubeConfig,
    state: Dict[str, Any],
    logger,
) -> None:
    """
    Download toàn bộ assets của danh sách video.

    State được lưu ngay sau mỗi video thành công.
    """
    prepare_output_directories(base_dir)

    state_dir = base_dir.parent / "state"

    for url in urls:
        video_id = extract_video_id(url)

        record: Dict[str, Any] = {
            "url": url,
            "downloaded_at": (
                datetime.utcnow().isoformat()
                + "Z"
            ),
        }

        try:
            # -------------------------------------------------
            # STEP 1: Metadata + subtitle
            # -------------------------------------------------
            info = download_video_info(
                url,
                base_dir,
                config,
            )

            is_shorts = is_youtube_shorts(
                info.get("duration") or 0,
                info.get("webpage_url") or "",
            )

            if config.exclude_shorts and is_shorts:
                logger.info(
                    f"Bỏ qua %s vì là YouTube Shorts: https://www.youtube.com/watch?v={video_id}"
                )
                continue

            move_subtitles(
                video_id,
                base_dir,
                record,
            )

            save_info_reference(
                video_id,
                base_dir,
                record,
            )

            # STEP 2: Video
            download_video(
                url,
                video_id,
                base_dir,
                config,
                record,
            )

            # STEP 3: Audio
            download_audio(
                url,
                video_id,
                base_dir,
                config,
                record,
            )

            # STEP 4: State
            if record.get("video") or record.get("audio"):
                state[video_id] = record

                save_state(
                    state_dir / "downloaded_ids.json",
                    state,
                )

                logger.info(
                    "Đã tải xong video %s",
                    video_id,
                )
            else:
                logger.warning(
                    "Video %s không tải được video/audio.",
                    video_id,
                )

        except Exception:
            logger.exception(
                "Lỗi tải video %s, "
                "bỏ qua và tiếp tục video tiếp theo.",
                video_id,
            )