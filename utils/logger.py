import logging

_FMT = "%(asctime)s | %(levelname)-8s | %(name)-35s | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def setup() -> None:
    """Initialize application-wide logging. Safe to call multiple times."""
    root = logging.getLogger("docudent")
    if root.handlers:
        return  # already configured

    root.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(_FMT, datefmt=_DATE_FMT))

    root.addHandler(console)


def get(name: str) -> logging.Logger:
    """Return a child logger under the 'docudent' namespace."""
    return logging.getLogger(f"docudent.{name}")
