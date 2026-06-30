from contextlib import contextmanager
from time import perf_counter

from prometheus_client import Counter, Histogram

REQUEST_LATENCY_SECONDS = Histogram(
    "laep_request_latency_seconds",
    "HTTP request latency",
    ["path", "method"],
)
REQUEST_COUNT = Counter(
    "laep_request_total",
    "HTTP request count",
    ["path", "method", "status"],
)


@contextmanager
def observe_request(path: str, method: str):
    start = perf_counter()
    try:
        yield
    finally:
        REQUEST_LATENCY_SECONDS.labels(path=path, method=method).observe(perf_counter() - start)
