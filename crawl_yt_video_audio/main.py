import sys

from .cli import parse_args
from .crawler import run


def main() -> int:
    """Parse CLI arguments và chạy YouTube crawler."""
    args = parse_args()
    return run(args.config)


if __name__ == "__main__":
    sys.exit(main())