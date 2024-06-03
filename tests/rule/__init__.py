import os

import pytest


@pytest.fixture(autouse=True)
def skip_remote_api_2():
    # if "CI" in os.environ:
    #     pytest.skip("Remote API tests are disable in CI")
    if os.environ.get("REMOTE_API_TEST", "1") != "1":
        pytest.skip("Remote API tests are disable by explicit REMOTE_API_TEST != 1")
    else:
        yield
