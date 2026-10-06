import asyncio

from api import health, router
from version import get_version


def test_health():
    assert "/health" in {route.path for route in router.routes}
    assert asyncio.run(health()) == {"status": "ok", "version": get_version()}
