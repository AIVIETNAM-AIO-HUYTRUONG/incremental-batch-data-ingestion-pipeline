import argparse
from typing import List, Optional

def parse_args(
    argv: Optional[List[str]] = None,
) -> argparse.Namespace:
    """
    Phân tích các tham số command line của Data Pipeline.

    Args:
        argv: Danh sách tham số command line.
            Nếu là ``None``, argparse sẽ đọc tham số từ ``sys.argv``.

    Returns:
        argparse.Namespace: Các tham số đã được argparse phân tích.

    Example:
        ``parse_args(["--job", "yt"])``

        trả về object có:

        ``args.job == ["yt"]``
    """
    parser = argparse.ArgumentParser(
        description="Điều phối pipeline nạp dữ liệu hàng ngày"
    )

    parser.add_argument(
        "--job",
        nargs="+",
        default=["all"],
        choices=["all", "arxiv", "yt", "unsplash"],
        help=(
            "Job cần chạy: 'all' (mặc định) hoặc một/nhiều "
            "trong số arxiv, yt, unsplash"
        ),
    )

    return parser.parse_args(argv)