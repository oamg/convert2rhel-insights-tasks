import pytest
from scripts.conversion_script import is_eligible_releases


@pytest.mark.parametrize(
    ("release", "expected"), (("6.10", False), ("7.9", True), ("8.9", False))
)
def test_is_eligible_releases(release, expected):
    assert is_eligible_releases(release) == expected
