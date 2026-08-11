"""ChatZulip package."""

from .client import ZulipClient
from .config import ZulipConfig

__all__ = ["ZulipClient", "ZulipConfig", "__version__"]

__version__ = "0.1.1"
