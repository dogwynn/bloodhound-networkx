import pytest
from bloodhound_networkx import bloodhound
from bloodhound_networkx.toolz import md5


def test_toolz_md5():
    """Unit test for toolz hashing."""
    hashed = md5(b"test")
    assert isinstance(hashed, str)
    assert len(hashed) == 32