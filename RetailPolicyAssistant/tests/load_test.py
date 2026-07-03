"""
Load Testing for SLO Validation

Tests system performance under concurrent load to validate:
- Latency targets (avg ≤1.5s, P95 ≤3s)
- Throughput capacity
- Resource utilization
- Degradation patterns
"""

import time
import concurrent.futures
import statistics
from datetime import datetime, timezone
import json
from pathlib import Path

from app.orchestrator import Orchestrator
from app.database.session import SessionLocal
from app.evaluation.golden_set import GOLDEN_SET


class LoadTestRunner:
    """Execute load tests against the orchestrator."""

    def __init__(self, output_file: str = "load_test_results.json"):
        self.db = SessionLocal()
        self.orchestrator = Orchestrator(self.db)
        self.output_file = Path(output_file)
        self.results = []

    def test_single_query(self, query: str, test_id: int) -> dict:
        """Execute a single query and measure latency."""
        try:
            start_time = time.time()
            response = self.orchestrator.run(query)
            latency = time.time() - start_time

            return {
                "test_id": test_id,
                "query": query[:50],
                "status": "success",
                "latency": latency,
                "route": response.get("route", "unknown"),
                "risk": response.get("risk", {}).get("risk_level", "unknown"),
                "escalate": response.get("escalate", False),
            }
        except Exception as e:
            return {
                "test_id": test_id,
                "query": query[:50],
                "status": "error",
                "latency": 0.0,
                "error": str(e),
            }

    def run_sequential_load(self, num_queries: int = 50):
        """Test 1 query at a time (baseline)."""
        print("\n📊 SEQUENTIAL LOAD TEST (1 concurrent query)")
        print("=" * 60)

        latencies = []
        start_time = time.time()

        # Use a subset of golden queries, repeat if needed
        queries = [item["query"] for item in GOLDEN_SET]
        for i in range(num_queries):
            query = queries[i % len(queries)]
            result = self.test_single_query(query, i)
            latencies.append(result["latency"])
            self.results.append(result)

            status_icon = "✅" if result["status"] == "success" else "❌"
            print(
                f"{status_icon} Query {i+1}/{num_queries}: {result['latency']:.3f}s ({result['status']})"
            )

        total_time = time.time() - start_time
        self.print_stats(latencies, total_time, num_queries)
        return latencies

    def run_concurrent_load(self, concurrent_queries: int = 5, num_batches: int = 10):
        """Test multiple concurrent queries."""
        print(f"\n📊 CONCURRENT LOAD TEST ({concurrent_queries} concurrent queries)")
        print("=" * 60)

        latencies = []
        query_count = 0

        queries = [item["query"] for item in GOLDEN_SET]
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrent_queries
        ) as executor:
            futures = []

            for batch in range(num_batches):
                # Submit concurrent tasks
                for i in range(concurrent_queries):
                    query_idx = (batch * concurrent_queries + i) % len(queries)
                    query = queries[query_idx]
                    test_id = query_count
                    futures.append(
                        executor.submit(self.test_single_query, query, test_id)
                    )
                    query_count += 1

                # Wait for batch to complete before submitting next batch
                batch_results = []
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    latencies.append(result["latency"])
                    self.results.append(result)
                    batch_results.append(result)

                successful = sum(
                    1 for r in batch_results if r["status"] == "success"
                )
                avg_latency = statistics.mean([r["latency"] for r in batch_results])
                print(
                    f"Batch {batch+1}/{num_batches}: {successful}/{concurrent_queries} success, "
                    f"avg latency: {avg_latency:.3f}s"
                )

                futures.clear()

        total_time = time.time() - start_time
        self.print_stats(latencies, total_time, query_count)
        return latencies

    def run_stress_test(self, duration_seconds: int = 60):
        """Run as many queries as possible within time limit."""
        print(f"\n📊 STRESS TEST ({duration_seconds}s duration)")
        print("=" * 60)

        latencies = []
        query_count = 0
        queries = [item["query"] for item in GOLDEN_SET]
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []

            # Keep submitting queries until time expires
            while time.time() - start_time < duration_seconds:
                query_idx = query_count % len(queries)
                query = queries[query_idx]

                future = executor.submit(self.test_single_query, query, query_count)
                futures.append(future)
                query_count += 1

                # Check for completed futures
                done, futures = concurrent.futures.wait(
                    futures, timeout=0.1, return_when=concurrent.futures.FIRST_COMPLETED
                )

                for future in done:
                    result = future.result()
                    latencies.append(result["latency"])
                    self.results.append(result)

            # Wait for remaining futures to complete
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                latencies.append(result["latency"])
                self.results.append(result)

        total_time = time.time() - start_time
        print(f"Completed {query_count} queries in {total_time:.1f}s")
        print(f"Throughput: {query_count/total_time:.1f} queries/sec")
        self.print_stats(latencies, total_time, query_count)
        return latencies

    def print_stats(self, latencies, total_time, query_count):
        """Print latency statistics."""
        if not latencies:
            print("❌ No successful queries!")
            return

        sorted_latencies = sorted(latencies)
        success_rate = (
            sum(1 for r in self.results[-query_count:] if r["status"] == "success")
            / query_count
            * 100
        )

        print("\n📈 Results:")
        print(f"  Total Queries: {query_count}")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Throughput: {query_count/total_time:.2f} queries/sec")
        print()
        print(f"  Min Latency: {min(latencies):.3f}s")
        print(f"  Max Latency: {max(latencies):.3f}s")
        print(f"  Avg Latency: {statistics.mean(latencies):.3f}s")
        print(f"  Median Latency: {statistics.median(latencies):.3f}s")
        if len(latencies) > 1:
            print(f"  StdDev: {statistics.stdev(latencies):.3f}s")
        print(f"  P50 Latency: {sorted_latencies[len(sorted_latencies)//2]:.3f}s")
        print(f"  P95 Latency: {sorted_latencies[int(len(sorted_latencies)*0.95)]:.3f}s")
        print(f"  P99 Latency: {sorted_latencies[int(len(sorted_latencies)*0.99)]:.3f}s")

        # Check SLO compliance
        avg_latency = statistics.mean(latencies)
        p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)]

        print("\n🎯 SLO Compliance:")
        avg_target = 1.5
        p95_target = 3.0
        avg_status = "✅ PASS" if avg_latency <= avg_target else "❌ FAIL"
        p95_status = "✅ PASS" if p95_latency <= p95_target else "❌ FAIL"
        print(f"  Avg Latency ≤ {avg_target}s: {avg_status} ({avg_latency:.3f}s)")
        print(f"  P95 Latency ≤ {p95_target}s: {p95_status} ({p95_latency:.3f}s)")

    def save_results(self):
        """Save test results to JSON file."""
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_queries": len(self.results),
            "successful_queries": sum(
                1 for r in self.results if r["status"] == "success"
            ),
            "failed_queries": sum(1 for r in self.results if r["status"] == "error"),
            "latencies": [r["latency"] for r in self.results],
        }

        if summary["latencies"]:
            summary["stats"] = {
                "min": min(summary["latencies"]),
                "max": max(summary["latencies"]),
                "avg": statistics.mean(summary["latencies"]),
                "p95": sorted(summary["latencies"])[
                    int(len(summary["latencies"]) * 0.95)
                ],
                "p99": sorted(summary["latencies"])[
                    int(len(summary["latencies"]) * 0.99)
                ],
            }

        output_data = {"summary": summary, "results": self.results}

        with open(self.output_file, "w") as f:
            json.dump(output_data, f, indent=2)

        print(f"\n💾 Results saved to {self.output_file}")

    def run_all_tests(self):
        """Run all load test scenarios."""
        print("\n" + "=" * 60)
        print("🚀 RETAIL POLICY SYSTEM - LOAD TEST SUITE")
        print("=" * 60)
        print(f"Start time: {datetime.now(timezone.utc).isoformat()}")
        print()

        # Test 1: Baseline sequential
        self.run_sequential_load(num_queries=20)

        # Test 2: Light concurrent (5 queries)
        self.run_concurrent_load(concurrent_queries=5, num_batches=5)

        # Test 3: Heavy concurrent (20 queries)
        self.run_concurrent_load(concurrent_queries=20, num_batches=3)

        # Test 4: Stress test
        self.run_stress_test(duration_seconds=30)

        # Save results
        self.save_results()

        print("\n" + "=" * 60)
        print("✅ Load test suite completed!")
        print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load test the orchestrator")
    parser.add_argument(
        "--test",
        choices=["sequential", "concurrent", "stress", "all"],
        default="all",
        help="Which test to run",
    )
    parser.add_argument(
        "--output", default="load_test_results.json", help="Output file"
    )

    args = parser.parse_args()

    runner = LoadTestRunner(output_file=args.output)

    try:
        if args.test == "sequential":
            runner.run_sequential_load(num_queries=50)
        elif args.test == "concurrent":
            runner.run_concurrent_load(concurrent_queries=10, num_batches=5)
        elif args.test == "stress":
            runner.run_stress_test(duration_seconds=60)
        else:  # all
            runner.run_all_tests()

        runner.save_results()

    finally:
        runner.db.close()
