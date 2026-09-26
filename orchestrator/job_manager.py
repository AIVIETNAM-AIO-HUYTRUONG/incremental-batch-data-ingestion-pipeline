from typing import List

from .config import JOB_ORDER, JOB_SCRIPTS


def parse_job_argument(jobs: List[str]) -> List[str]:
    """
    Chuẩn hóa và kiểm tra danh sách job cần chạy.

    Nếu ``jobs`` chứa ``"all"``, hàm trả về toàn bộ job theo thứ tự
    được định nghĩa trong ``JOB_ORDER``.

    Nếu người dùng chỉ định các job cụ thể, hàm giữ nguyên thứ tự
    mà người dùng nhập vào.

    Args:
        jobs: Danh sách tên job cần chạy.

    Returns:
        List[str]: Danh sách job hợp lệ đã được chuẩn hóa.

    Raises:
        ValueError: Nếu danh sách chứa job không tồn tại trong
            ``JOB_SCRIPTS``.

    Examples:
        ``parse_job_argument(["all"])``

        -> ``["arxiv", "yt", "unsplash"]``

        ``parse_job_argument(["yt"])``

        -> ``["yt"]``

        ``parse_job_argument(["yt", "arxiv"])``

        -> ``["yt", "arxiv"]``
    """
    if "all" in jobs:
        return list(JOB_ORDER)

    unknown = set(jobs) - set(JOB_SCRIPTS.keys())

    if unknown:
        raise ValueError(
            f"Job không hợp lệ: {sorted(unknown)}. "
            f"Các giá trị job hợp lệ: {list(JOB_SCRIPTS)} hoặc 'all'."
        )

    return jobs