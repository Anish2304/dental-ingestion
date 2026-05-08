import os
import pytest


def pytest_configure(config):
    missing = [
        k for k in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY")
        if not os.getenv(k)
    ]
    if missing:
        pytest.exit(
            f"Missing required env vars: {', '.join(missing)}\n"
            "Set them in your .env file or environment before running tests.",
            returncode=1,
        )
