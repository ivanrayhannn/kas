# Titik masuk serverless Vercel: semua /api/* diarahkan ke aplikasi FastAPI ini.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.main import app  # noqa: E402,F401
