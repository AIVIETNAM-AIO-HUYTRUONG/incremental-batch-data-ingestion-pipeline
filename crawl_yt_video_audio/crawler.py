from crawl_yt_video_audio.downloader import download_assets
from crawl_yt_video_audio.youtube_api import get_recent_videos
from common.state_store import load_state
from datetime import datetime
from pathlib import Path
from typing import Optional


from common.config_utils import require_env, load_env
from .environment import require_ffmpeg
from common.logging_utils import setup_logger


from .config import (
    MODULE_DIR,
    OUTPUT_ROOT,
    YoutubeConfig,
)

def create_youtube_client(api_key:str):
    """
    Khởi tạo YouTube Data API client.
    """
    from googleapiclient.discovery import build

    return build(
        "youtube",
        "v3",
        developerKey=api_key,
        cache_discovery=False
    )

def run(config_path: Optional[Path] = None) -> int:
    """
    Chạy toàn bộ YouTube crawler một lần.

    Workflow:

        Load environment
            ↓
        Load configuration
            ↓
        Load state
            ↓
        Search YouTube
            ↓
        Filter videos
            ↓
        Download assets
            ↓
        Update state
    """

    require_ffmpeg()
    
    config_path = (
        config_path or MODULE_DIR/"config.yaml"
    )

    # 1. Environment
    load_env(MODULE_DIR/".env")
    api_key:str = require_env(key="YOUTUBE_API_KEY")

    # 2. Configuration
    config:YoutubeConfig = YoutubeConfig.from_yaml(config_path)
    
    # 3. Run directories
    run_date = datetime.now().strftime("%Y-%m-%d") 

    state_dir = (OUTPUT_ROOT / "state") 
    state_dir.mkdir(
        parents=True,
        exist_ok=True,
    )    

    #4. Logger
    logger = setup_logger(
        "crawl_youtube",
        state_dir,
        f"crawl_{run_date}.log",
    )
    
    logger.info(
        "\nBắt đầu crawl YouTube | "
        "query='%s' | days_back=%d | max_results=%d",
        config.query,
        config.days_back,
        config.max_results,
    )

    # 5. Load state
    state = load_state(
        state_dir / "downloaded_ids.json"
    )

    skip_ids = set(
        state.keys()
    )
    
    # 6. YouTube client
    youtube = create_youtube_client(
        api_key
    )


    # 7. Search + filter
    try:
        urls = get_recent_videos(
            youtube=youtube,
            skip_ids=skip_ids,
            config=config,
            logger=logger,
        )

    except Exception:
        logger.exception("Lỗi nghiêm trọng khi tìm kiêm video trên YouTube")
        return 1
    
    if not urls:
        logger.info("Không có video mới nào phù hợp.")
        return 0

    # 8. Download
    base_dir = OUTPUT_ROOT/run_date

    download_assets(
        urls=urls,
        base_dir=base_dir,
        config=config,
        state=state,
        logger=logger,
    )
    return 0