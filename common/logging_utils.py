"""Tiện ích thiết lập logging thống nhất cho toàn bộ pipeline.

Mỗi lần chạy, mỗi module ghi log ra một file riêng theo ngày
(vd crawl_2026-09-25.log), đồng thời in ra console để tiện theo dõi khi
chạy thủ công. Khi chạy qua Windows Task Scheduler (không có console),
file log là nơi duy nhất để biết pipeline có chạy thành công hay không -
vì vậy log luôn được ghi ra file trước, console chỉ là tiện ích thêm.
"""

import logging
import sys
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def setup_logger(
    name: str,
    log_dir: PathLike,
    log_filename: str,
    level: int = logging.INFO,
) -> logging.Logger:
    """Tạo/lấy logger ghi đồng thời ra console và ra file trong `log_dir`.

    File log được mở ở chế độ append ("a") để nếu pipeline chạy lại nhiều
    lần trong cùng một ngày (vd chạy tay để kiểm tra lỗi), lịch sử log
    trước đó không bị mất.

    Hàm này an toàn khi gọi nhiều lần với cùng `name` (vd trong notebook,
    khi cell được chạy lại) - các handler cũ sẽ được dọn trước khi thêm
    handler mới, tránh log bị in lặp nhiều lần.
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / log_filename

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        logger.handlers.clear()

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    return logger
