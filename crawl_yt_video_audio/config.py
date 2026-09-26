from dataclasses import dataclass
from pathlib import Path
from typing import List

from common.config_utils import load_yaml_config


MODULE_DIR = Path(__file__).resolve().parent

OUTPUT_ROOT = (
    MODULE_DIR.parent
    / "data_lake_local"
    / "youtube"
)


@dataclass
class YoutubeConfig:
    """Cấu hình cho YouTube crawler."""

    query: str
    days_back: int

    min_duration_seconds: int
    max_duration_seconds: int

    require_english: bool
    exclude_shorts: bool

    max_results: int
    relevance_language: str
    search_timeout_seconds: int

    video_format: str
    audio_format: str

    subtitle_langs: List[str]

    @classmethod
    def from_yaml(cls, path: Path) -> "YoutubeConfig":
        """
        Load YoutubeConfig từ YAML.

        Args:
            path: Đường dẫn tới config.yaml.

        Returns:
            YoutubeConfig: Cấu hình đã được load.
        """
        raw = load_yaml_config(path)

        download_config = raw.get("download", {})

        return cls(
            query=raw.get(
                "query",
                "AI Research Papers",
            ),
            days_back=raw.get(
                "days_back",
                1,
            ),
            min_duration_seconds=raw.get(
                "min_duration_seconds",
                120,
            ),
            max_duration_seconds=raw.get(
                "max_duration_seconds",
                720,
            ),
            require_english=raw.get(
                "require_english",
                True,
            ),
            exclude_shorts=raw.get(
                "exclude_shorts",
                True,
            ),
            max_results=raw.get(
                "max_results",
                10,
            ),
            relevance_language=raw.get(
                "relevance_language",
                "en",
            ),
            search_timeout_seconds=raw.get(
                "search_timeout_seconds",
                60,
            ),
            video_format=download_config.get(
                "video_format",
                (
                    "bestvideo[ext=mp4][height<=1080]"
                    "+bestaudio[ext=m4a]"
                    "/best[ext=mp4]/best"
                ),
            ),
            audio_format=download_config.get(
                "audio_format",
                "bestaudio[ext=m4a]/bestaudio",
            ),
            subtitle_langs=download_config.get(
                "subtitle_langs",
                ["en"],
            ),
        )