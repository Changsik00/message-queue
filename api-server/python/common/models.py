import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'packages'))
from shared_python.models import ProcessedEvent

__all__ = ["ProcessedEvent"]
