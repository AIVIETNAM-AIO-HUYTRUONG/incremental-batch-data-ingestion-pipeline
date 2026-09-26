import subprocess
import sys
from pathlib import Path


def run_python(script_path: Path) -> int:
    """
    Chạy một Python script dưới dạng subprocess.

    Args:
        script_path: Đường dẫn đến Python script cần chạy.

    Returns:
        int: Exit code của subprocess.
            ``0`` nghĩa là chạy thành công.
            Giá trị khác ``0`` nghĩa là script thất bại.
    """
    result = subprocess.run(
        [sys.executable, str(script_path)],
        check=False,
    )

    return result.returncode