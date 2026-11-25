import os
import sys

# Add repository root to Python path so backend packages import seamlessly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
