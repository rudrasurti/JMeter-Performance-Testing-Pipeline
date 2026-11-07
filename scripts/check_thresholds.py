"""Fail the build when a JMeter run breaks its performance limits.

Reads a JMeter CSV results file (JTL), prints a Markdown summary per request,
and exits 1 if the error rate or the 95th percentile response time is too high.
Limits come from environment variables so CI can tune them per run.
"""
import csv
import math
import os
import sys
from collections import defaultdict

MAX_ERROR_PCT = float(os.getenv("MAX_ERROR_PCT", "2"))
MAX_P95_MS = float(os.getenv("MAX_P95_MS", "5000"))


def p95(values):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def main(path):
    rows = defaultdict(list)
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows[r["label"]].append((int(r["elapsed"]), r["success"].lower() == "true"))
    if not rows:
        print("No samples found in", path)
        return 1

    all_samples = [s for v in rows.values() for s in v]
    rows["ALL"] = all_samples
    failed = False
    print(f"### JMeter results (limits: errors <= {MAX_ERROR_PCT}%, p95 <= {MAX_P95_MS:.0f} ms)\n")
    print("| Request | Samples | Errors % | Avg ms | p95 ms | Result |")
    print("|---|---|---|---|---|---|")
    for label, samples in rows.items():
        times = [t for t, _ in samples]
        err = 100 * sum(1 for _, ok in samples if not ok) / len(samples)
        q = p95(times)
        ok = err <= MAX_ERROR_PCT and q <= MAX_P95_MS
        failed |= not ok
        print(f"| {label} | {len(samples)} | {err:.1f} | {sum(times) / len(times):.0f} | {q} | {'PASS' if ok else 'FAIL'} |")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "results/results.jtl"))
