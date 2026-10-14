"""Token bucket in-memory theo (uid, key_index).

Per-worker (đủ cho pilot); nhiều worker thì mỗi worker
một bucket riêng, tổng thực tế = limit × số worker, chấp nhận xấp xỉ.
"""
import threading
import time

_BUCKETS = {}
_LOCK = threading.Lock()


def check(uid, key_index, limit=60, window=60.0):
    now = time.monotonic()
    with _LOCK:
        b = _BUCKETS.setdefault((uid, key_index), {'tokens': float(limit), 'ts': now})
        b['tokens'] = min(float(limit), b['tokens'] + (now - b['ts']) * (limit / window))
        b['ts'] = now
        if b['tokens'] >= 1:
            b['tokens'] -= 1
            return True
        return False


def reset():
    with _LOCK:
        _BUCKETS.clear()
