import shutil

def require_ffmpeg() -> None:
    """Kiểm tra ffmpeg đã được cài đặt và có trong PATH."""

    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "Không tìm thấy ffmpeg. "
            "Hãy cài ffmpeg và đảm bảo ffmpeg có trong PATH."
        )