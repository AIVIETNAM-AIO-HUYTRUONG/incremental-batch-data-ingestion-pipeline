from pathlib import Path

try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    REPO_ROOT = Path.cwd().parent

print(REPO_ROOT)

JOB_SCRIPTS = {
  "yt":REPO_ROOT/"crawl_yt_video_audio"/"main.py",
  # "arxiv": REPO_ROOT / "crawl_arxiv" / "main.py",
  # "unsplash": REPO_ROOT / "crawl_unsplash" / "main.py",
}

JOB_ORDER = [
  # "arxiv",
  "yt",
  # "unsplash"
]

LOG_DIR = REPO_ROOT / "data_lake_local" / "_orchestrator_logs"