from prometheus_client import Counter

example_metric = Counter("example_metric", "This is an example metric.", labelnames=["event"])
