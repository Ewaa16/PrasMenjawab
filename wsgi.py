from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from a2wsgi import ASGIMiddleware  # noqa: E402

import main  # noqa: E402

application = ASGIMiddleware(main.app)
