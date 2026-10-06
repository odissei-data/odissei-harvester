import os

# auth reads API_KEY at import; the route tests import it.
os.environ.setdefault("API_KEY", "test")
