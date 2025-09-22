import time
import pytest
from app.store import InMemoryStorage

def test_set_get_no_ttl():
    s = InMemoryStorage()
    s.set('a', '1')
    assert s.get('a') == '1'
    assert s.ttl('a') == -1


def test_set_with_ttl_expires_and_lazy_cleanup():
    s = InMemoryStorage()
    s.set("t", "42", ex_seconds=1)
    assert s.get("t") == "42"
    ttl_now = s.ttl("t")
    assert ttl_now in (0, 1)
    time.sleep(1.2)

    assert s.get("t") is None
    assert s.ttl("t") == -2

def test_overwrite_ttl_and_value():
    s = InMemoryStorage()
    s.set('k', 'old', ex_seconds=3)
    s.set('k', 'new')
    assert s.get('k') == 'new'
    assert s.ttl('k') == -1


@pytest.mark.parametrize("bad", [0, -1, -100])
def test_invalid_ttl_value(bad):
    s = InMemoryStorage()
    with pytest.raises(ValueError):
        s.set("x", "v", ex_seconds=bad)

def test_invalid_empty_key():
    s = InMemoryStorage()
    with pytest.raises(ValueError):
        s.set('', 'v')

def test_ttl_floor_semantics_non_negative_before_expire():
    s = InMemoryStorage()
    s.set("t", "v", ex_seconds=2)
    first = s.ttl("t")
    assert first in (1, 2)
    time.sleep(0.6)
    second = s.ttl("t")
    assert second <= first and second >= 0

