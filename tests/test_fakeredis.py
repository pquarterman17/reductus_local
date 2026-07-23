"""
Tests for the in-memory cache in reductus.dataflow.fakeredis.

Regression guard: the cache must stay bounded. It previously fell back to a
plain dict (growing without limit) when the optional *pylru* package was not
installed; it now falls back to a stdlib LRU (:class:`_SimpleLRU`) instead.
"""

import sys
import os
import warnings

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reductus.dataflow.fakeredis import _SimpleLRU, lrucache, MemoryCache


def test_simplelru_evicts_least_recently_used():
    c = _SimpleLRU(3)
    for k in range(3):
        c[k] = k * 10
    assert list(c.keys()) == [0, 1, 2]
    _ = c[0]                 # touch 0 -> most-recently used; 1 is now the LRU
    c[3] = 30                # inserting a 4th evicts the LRU (key 1)
    assert len(c) == 3
    assert 1 not in c
    assert 0 in c and 2 in c and 3 in c


def test_simplelru_getitem_raises_keyerror():
    # MemoryCache.get relies on missing keys raising KeyError, like a dict.
    c = _SimpleLRU(2)
    try:
        _ = c["missing"]
    except KeyError:
        pass
    else:
        raise AssertionError("expected KeyError for a missing key")


def test_simplelru_overwrite_does_not_grow():
    c = _SimpleLRU(2)
    c["a"] = 1
    c["a"] = 2
    assert len(c) == 1
    assert c["a"] == 2


def test_lrucache_factory_is_always_bounded():
    # Whichever backend lrucache() selects (pylru or _SimpleLRU), it must bound.
    cache = lrucache(2)
    for i in range(1, 6):
        cache[i] = str(i)
    n = len(cache) if hasattr(cache, "__len__") else len(list(cache.keys()))
    assert n <= 2, "cache grew without bound: %d entries" % n


def test_fallback_emits_no_warning():
    # Simulate pylru being absent; the stdlib fallback must not warn.
    saved = sys.modules.get("pylru", "__unset__")
    sys.modules["pylru"] = None      # forces `import pylru` to raise ImportError
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            cache = lrucache(4)
            cache["x"] = 1
        assert cache["x"] == 1
    finally:
        if saved == "__unset__":
            sys.modules.pop("pylru", None)
        else:
            sys.modules["pylru"] = saved


def test_memorycache_redis_interface():
    m = MemoryCache(size=2)
    m.set("k", "v")
    assert m.exists("k")
    assert m.get("k") == "v"
    m.rpush("list", "a")
    m.rpush("list", "b")
    assert m.lrange("list", 0, -1) == ["a", "b"]
    m.delete("k")
    assert not m.exists("k")
