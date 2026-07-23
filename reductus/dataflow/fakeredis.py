"""
Redis-like interface to an in-memory cache

:class:`MemoryCache` provides a minimal redis-like interface to an in memory
cache.  It always uses least-recently-used eviction so the cache stays bounded:
the optional *pylru* package when installed, otherwise the equivalent
standard-library :class:`_SimpleLRU`.
"""
from __future__ import print_function

import os
import threading
from collections import OrderedDict


class _SimpleLRU(object):
    """Size-bounded least-recently-used cache using only the standard library.

    A drop-in replacement for ``pylru.lrucache(size)`` covering the subset of
    behaviour :class:`MemoryCache` relies on: item get/set/delete, ``in`` and
    ``keys()``.  Used when the optional *pylru* package is not installed, so the
    cache is always bounded instead of growing without limit (which matters for
    long-running desktop/server sessions).
    """
    def __init__(self, size=1000):
        self.size = max(1, int(size))
        self._data = OrderedDict()

    def __getitem__(self, key):
        value = self._data[key]         # raises KeyError if missing, like dict
        self._data.move_to_end(key)     # mark as most-recently used
        return value

    def __setitem__(self, key, value):
        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value
        while len(self._data) > self.size:
            self._data.popitem(last=False)   # evict least-recently used

    def __delitem__(self, key):
        del self._data[key]

    def __contains__(self, key):
        return key in self._data

    def keys(self):
        return self._data.keys()

    def __len__(self):
        return len(self._data)


def lrucache(size):
    try:
        import pylru
        return pylru.lrucache(size)
    except ImportError:
        # pylru is an optional third-party dependency; fall back to an
        # equivalent stdlib LRU so the cache never grows without bound. No
        # warning: this fallback is fully functional, not a degraded mode.
        return _SimpleLRU(size)


class MemoryCache(object):
    """
    In memory cache with redis interface.

    Use this for running tests without having to start up the redis server.

    *size* is the maximum number of elements to cache; the least-recently-used
    entries are evicted once the cache is full.
    """
    def __init__(self, size=1000):
        self.cache = lrucache(size)

    def exists(self, key):
        return key in self.cache

    def keys(self):
        return self.cache.keys()

    def delete(self, *key):
        for k in key:
            del self.cache[k]

    def set(self, key, value):
        self.cache[key] = value

    def get(self, key):
        """Note: doesn't provide default value for missing key like dict.get"""
        return self.cache[key]

    __delitem__ = delete
    __setitem__ = set
    __getitem__ = get

    def rpush(self, key, value):
        if key not in self.cache:
            self.cache[key] = [value]
        else:
            self.cache[key].append(value)

    def lrange(self, key, low, high):
        """Note: returned range includes high index, not high-1 like lists"""
        return self.cache[key][low:(high+1 if high != -1 else None)]

class FileBasedCache(object):
    """
    Disk-based cache with redis interface.

    Use this for running tests without having to start up the redis server.
    """
    def __init__(self, size=1000, cachedir='~/.reductus/cache'):
        self.size = size
        self.lock = threading.Lock()
        self.cachedir = os.path.expanduser(cachedir)
        if not os.path.exists(self.cachedir):
            os.mkdir(self.cachedir)

    def exists(self, key):
        return os.path.exists(os.path.join(self.cachedir, key))

    def keys(self):
        return os.listdir(self.cachedir)

    def delete(self, *key):
        for k in key:
            kp = os.path.join(self.cachedir, k)
            if os.path.isdir(kp):
                for f in os.listdir(kp):
                    os.remove(os.path.join(kp, f))
                os.rmdir(kp)
            else:
                os.remove(kp)

    def set(self, key, value):
        #open(os.path.join(self.cachedir, key), "wb").write(pickle.dumps(value))
        with self.lock:
            open(os.path.join(self.cachedir, key), "wb").write(value)

    def get(self, key):
        """Note: doesn't provide default value for missing key like dict.get"""
        try:
            #ret = pickle.loads(open(os.path.join(self.cachedir, key), "rb").read())
            ret = open(os.path.join(self.cachedir, key), "rb").read()
        except IOError:
            raise KeyError(key)
        return ret

    __delitem__ = delete
    __setitem__ = set
    __getitem__ = get
    __contains__ = exists

    def rpush(self, key, value):
        with self.lock:
            keydir = os.path.join(self.cachedir, key)
            if not os.path.isdir(keydir):
                if os.path.exists(keydir):
                    raise KeyError(key)
                os.mkdir(keydir)
                new_filenum = 0
            else:
                filenums = map(int, os.listdir(keydir))
                if len(filenums) == 0:
                    new_filenum = 0
                else:
                    new_filenum = max(filenums) + 1
            open(os.path.join(keydir, str(new_filenum)), "wb").write(value)

    def lrange(self, key, low, high):
        """Note: returned range includes high index, not high-1 like lists"""
        keydir = os.path.join(self.cachedir, key)
        if not os.path.isdir(keydir):
            raise KeyError(key)
        with self.lock:
            filenums = sorted(map(int, os.listdir(keydir)))
            lookups = filenums[low:(high+1 if high != -1 else None)]
            return [open(os.path.join(keydir, str(n)), "rb").read() for n in lookups]

    def __repr__(self):
        return "<%s.%s %s>" % (
            self.__class__.__module__, self.__class__.__name__, self.cachedir)


def demo():
    class Expensive(object):
        def __del__(self):
            print('(Deleting %d)' % self.a)
        def __init__(self, a):
            self.a = a
            print('(Creating %s)' % self.a)
    print("test using get/set interface")
    cache = MemoryCache(5)
    for k in range(5):
        print("=== inserting %d"%k)
        cache.set(k, Expensive(k))
    for k in range(5):
        print("=== inserting %d, deleting %d"%(k+5, k))
        cache.set(k+5, Expensive(k+5))
    print("=== accessing oldest element, 5")
    a = cache.get(5)
    print("=== inserting 10 and deleting 6")
    cache.set(10, Expensive(10))

    print("="*50)
    print("test using dict-like interface")
    cache2 = MemoryCache(5)
    for k in range(5):
        print("=== inserting %d"%k)
        cache2[k] = Expensive(k)
    for k in range(5):
        print("=== inserting %d, deleting %d"%(k+5, k))
        cache2[k+5] = Expensive(k+5)
    print("=== accessing oldest element, 5")
    a = cache2[5]
    print("=== inserting 10 and deleting 6")
    cache2[10] = Expensive(10)

    print("=== cleanup of cache and cache2 can happen in any order")

if __name__ == "__main__":
    demo()

