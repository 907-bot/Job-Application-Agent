"""
Tests Package
Unit tests for Job Application Agent
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Version
__version__ = "1.0.0"
