import argparse
from pathlib import Path
from typing import List, Optional


def parse_args(
    argv: Optional[List[str]] = None,
) -> argparse.Namespace:
    """
    Parse command-line arguments cho YouTube crawler.

    Args:
        argv: Danh sách arguments cần parse.
            Nếu None, argparse đọc từ sys.argv.

    Returns:
        argparse.Namespace: Arguments đã được parse.
    """
    parser = argparse.ArgumentParser(
        description="Crawl video, audio và phụ đề từ YouTube"
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Đường dẫn tới config.yaml",
    )

    return parser.parse_args(argv)