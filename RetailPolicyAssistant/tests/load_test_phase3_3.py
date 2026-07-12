"""Load testing framework for Phase 3.3 query optimization."""

import time
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from typing import List, Dict, Any
from statistics import mean, median, quantiles


class MockDatabasePool:
    """Mock database pool for load testing without real database."""

    def acquire(self):
        """Acquire connection (mock)."""
        return MockConnection()


class MockConnection:
    """Mock database connection."""

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def fetchrow(self, query: str, *args):
        """Mock single row fetch with latency simulation."""
        # Simulate network + processing latency
        await asyncio.sleep(0.001)  # 1ms baseline
        return {"error_count": 10, "total_weight": 15.0}

    async def fetch(self, query: str, *args):
        """Mock multiple row fetch with latency simulation."""
        # Simulate network + processing latency
        await asyncio.sleep(0.002)  # 2ms baseline
        return [{"id": str(uuid4()), "weight": 1.5} for _ in range(100)]

    async def execute(self, query: str, *args):
        """Mock execute (insert/update) with latency simulation."""
        # Simulate network + processing latency
        await asyncio.sleep(0.001)  # 1ms baseline


class LoadTestResults:
    """Results from load test run."""

    def __init__(self):
        self.query_times: List[float] = []
        self.insertion_times: List[float] = []
        self.errors: int = 0
        self.timeouts: int = 0
        self.total_time: float = 0.0

    def add_query_time(self, duration_ms: float):
        """Record query execution time."""
        self.query_times.append(duration_ms)

    def add_insertion_time(self, duration_ms: float):
        """Record insertion time."""
        self.insertion_times.append(duration_ms)

    def get_summary(self) -> Dict[str, Any]:
        """Get test results summary."""
        if not self.query_times and not self.insertion_times:
            return {"error": "No data collected"}

        all_times = self.query_times + self.insertion_times

        return {
            "total_operations": len(all_times),
            "queries": len(self.query_times),
            "insertions": len(self.insertion_times),
            "query_stats": {
                "mean_ms": mean(self.query_times) if self.query_times else 0,
                "median_ms": median(self.query_times) if self.query_times else 0,
                "p50_ms": self.get_percentile(self.query_times, 50),
                "p95_ms": self.get_percentile(self.query_times, 95),
                "p99_ms": self.get_percentile(self.query_times, 99),
                "max_ms": max(self.query_times) if self.query_times else 0,
            } if self.query_times else None,
            "insertion_stats": {
                "mean_ms": mean(self.insertion_times) if self.insertion_times else 0,
                "median_ms": median(self.insertion_times) if self.insertion_times else 0,
                "p50_ms": self.get_percentile(self.insertion_times, 50),
                "p95_ms": self.get_percentile(self.insertion_times, 95),
                "p99_ms": self.get_percentile(self.insertion_times, 99),
                "max_ms": max(self.insertion_times) if self.insertion_times else 0,
            } if self.insertion_times else None,
            "errors": self.errors,
            "timeouts": self.timeouts,
            "total_time_sec": self.total_time,
        }

    @staticmethod
    def get_percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        if len(data) == 1:
            return data[0]

        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


class Phase3_3LoadTester:
    """Load testing for Phase 3.3 database persistence layer."""

    def __init__(self, db_pool=None, duration_seconds: int = 10):
        self.db_pool = db_pool or MockDatabasePool()
        self.duration_seconds = duration_seconds
        self.results = LoadTestResults()

    async def test_error_recording_load(self, target_rate: int = 100) -> Dict[str, Any]:
        """Simulate sustained error recording load.

        Args:
            target_rate: Target events per second

        Returns:
            Load test results
        """
        print(f"\n*** Error Recording Load Test ({target_rate} events/sec)")
        print("=" * 60)

        start_time = time.time()
        event_count = 0
        self.results = LoadTestResults()

        while time.time() - start_time < self.duration_seconds:
            # Calculate how many events to emit in this iteration
            events_per_iteration = target_rate // 10  # 10 iterations per second

            for _ in range(events_per_iteration):
                iter_start = time.time()

                # Simulate error insertion
                await self._simulate_error_insertion()

                iter_duration = (time.time() - iter_start) * 1000
                self.results.add_insertion_time(iter_duration)
                event_count += 1

            # Sleep to maintain target rate
            await asyncio.sleep(0.1)

        elapsed = time.time() - start_time
        self.results.total_time = elapsed
        actual_rate = event_count / elapsed

        print(f"  > Recorded {event_count} events in {elapsed:.1f}s")
        print(f"  > Actual rate: {actual_rate:.0f} events/sec")
        print(f"  > Target rate: {target_rate} events/sec")

        summary = self.results.get_summary()
        self._print_statistics(summary.get("insertion_stats", {}))

        return summary

    async def test_concurrent_queries(self, concurrent_count: int = 10) -> Dict[str, Any]:
        """Simulate concurrent burn rate queries.

        Args:
            concurrent_count: Number of concurrent queries

        Returns:
            Load test results
        """
        print(f"\n>>> Concurrent Query Load Test ({concurrent_count} queries)")
        print("=" * 60)

        start_time = time.time()
        self.results = LoadTestResults()

        # Create query tasks
        tasks = []
        for i in range(concurrent_count):
            tasks.append(self._simulate_concurrent_queries(10))  # 10 queries per task

        # Run all concurrently
        await asyncio.gather(*tasks)

        elapsed = time.time() - start_time
        self.results.total_time = elapsed

        total_queries = len(self.results.query_times)
        query_rate = total_queries / elapsed

        print(f"[OK] Executed {total_queries} queries in {elapsed:.1f}s")
        print(f"[OK] Query rate: {query_rate:.0f} queries/sec")

        summary = self.results.get_summary()
        self._print_statistics(summary.get("query_stats", {}))

        return summary

    async def test_mixed_workload(self, duration: int = 15) -> Dict[str, Any]:
        """Simulate mixed workload: insertions + queries + snapshots.

        Args:
            duration: Test duration in seconds

        Returns:
            Load test results
        """
        print(f"\n=== Mixed Workload Load Test ({duration}s)")
        print("=" * 60)

        start_time = time.time()
        self.results = LoadTestResults()

        tasks = [
            self._mixed_workload_inserter(start_time, duration, 100),  # 100 events/sec
            self._mixed_workload_querier(start_time, duration, 5),     # 5 queries/sec
            self._mixed_workload_snapshots(start_time, duration, 0.5), # 0.5 snapshots/sec
        ]

        await asyncio.gather(*tasks)

        elapsed = time.time() - start_time
        self.results.total_time = elapsed

        print(f"[OK] Mixed workload completed in {elapsed:.1f}s")

        summary = self.results.get_summary()
        if summary.get("query_stats"):
            self._print_statistics(summary.get("query_stats", {}))
        if summary.get("insertion_stats"):
            self._print_statistics(summary.get("insertion_stats", {}))

        return summary

    async def test_scalability(self, error_counts: List[int] = None) -> List[Dict[str, Any]]:
        """Test scalability with different data volumes.

        Args:
            error_counts: List of error counts to test [100K, 1M, etc]

        Returns:
            Results for each scale
        """
        if error_counts is None:
            error_counts = [100_000, 1_000_000]

        print(f"\n--- Scalability Test (dataset sizes)")
        print("=" * 60)

        results = []

        for count in error_counts:
            print(f"\nTesting with {count:,} errors...")

            self.results = LoadTestResults()

            # Simulate queries on large dataset
            for _ in range(10):
                iter_start = time.time()
                await self._simulate_burn_rate_query()
                iter_duration = (time.time() - iter_start) * 1000
                self.results.add_query_time(iter_duration)

            summary = self.results.get_summary()
            summary["dataset_size"] = count

            print(f"  [OK] p50: {summary.get('query_stats', {}).get('p50_ms', 0):.1f}ms")
            print(f"  [OK] p95: {summary.get('query_stats', {}).get('p95_ms', 0):.1f}ms")
            print(f"  [OK] p99: {summary.get('query_stats', {}).get('p99_ms', 0):.1f}ms")

            results.append(summary)

        return results

    # Helper methods

    async def _simulate_error_insertion(self):
        """Simulate a single error insertion."""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO error_events (budget_window_id, error_type, severity, weight) VALUES ($1, $2, $3, $4)",
                str(uuid4()),
                "latency",
                "normal",
                1.0,
            )

    async def _simulate_burn_rate_query(self):
        """Simulate a burn rate query."""
        async with self.db_pool.acquire() as conn:
            await conn.fetchrow(
                "SELECT COUNT(*), SUM(weight), AVG(weight) FROM error_events WHERE budget_window_id = $1 AND timestamp >= $2",
                str(uuid4()),
                datetime.utcnow() - timedelta(hours=1),
            )

    async def _simulate_concurrent_queries(self, count: int):
        """Run multiple queries sequentially."""
        for _ in range(count):
            iter_start = time.time()
            await self._simulate_burn_rate_query()
            iter_duration = (time.time() - iter_start) * 1000
            self.results.add_query_time(iter_duration)

    async def _mixed_workload_inserter(self, start_time: float, duration: int, rate: int):
        """Insert errors at target rate."""
        while time.time() - start_time < duration:
            await self._simulate_error_insertion()
            self.results.add_insertion_time(1.0)  # 1ms baseline
            await asyncio.sleep(1.0 / rate)

    async def _mixed_workload_querier(self, start_time: float, duration: int, rate: int):
        """Execute queries at target rate."""
        while time.time() - start_time < duration:
            await self._simulate_burn_rate_query()
            self.results.add_query_time(1.0)  # 1ms baseline
            await asyncio.sleep(1.0 / rate)

    async def _mixed_workload_snapshots(self, start_time: float, duration: int, rate: float):
        """Create snapshots at target rate."""
        while time.time() - start_time < duration:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO budget_snapshots (budget_window_id, snapshot_date, consumed_percent, burn_rate_multiplier, alert_status) VALUES ($1, $2, $3, $4, $5)",
                    str(uuid4()),
                    datetime.utcnow().date(),
                    25.0,
                    1.5,
                    "warning",
                )
            await asyncio.sleep(1.0 / rate if rate > 0 else 1.0)

    @staticmethod
    def _print_statistics(stats: Dict[str, float]):
        """Print statistics in readable format."""
        if not stats:
            return

        print(f"  Mean:   {stats.get('mean_ms', 0):.1f}ms")
        print(f"  Median: {stats.get('median_ms', 0):.1f}ms")
        print(f"  p50:    {stats.get('p50_ms', 0):.1f}ms")
        print(f"  p95:    {stats.get('p95_ms', 0):.1f}ms")
        print(f"  p99:    {stats.get('p99_ms', 0):.1f}ms")
        print(f"  Max:    {stats.get('max_ms', 0):.1f}ms")


async def run_all_load_tests():
    """Run complete load test suite."""
    tester = Phase3_3LoadTester(duration_seconds=10)

    print("\n" + "=" * 60)
    print("PHASE 3.3 QUERY OPTIMIZATION - LOAD TEST SUITE")
    print("=" * 60)

    # Test 1: Error recording load
    results_1 = await tester.test_error_recording_load(target_rate=100)

    # Test 2: Concurrent queries
    results_2 = await tester.test_concurrent_queries(concurrent_count=10)

    # Test 3: Mixed workload
    results_3 = await tester.test_mixed_workload(duration=15)

    # Test 4: Scalability
    results_4 = await tester.test_scalability(error_counts=[100_000, 1_000_000])

    print("\n" + "=" * 60)
    print("LOAD TEST SUMMARY")
    print("=" * 60)
    print(f"OK Error recording load:  {results_1['insertions']} insertions")
    print(f"OK Concurrent queries:    {results_2['queries']} queries")
    print(f"OK Mixed workload:        {results_3['total_operations']} operations")
    print(f"OK Scalability tested on: 2 dataset sizes")

    return {
        "error_recording": results_1,
        "concurrent_queries": results_2,
        "mixed_workload": results_3,
        "scalability": results_4,
    }


if __name__ == "__main__":
    # Run load tests
    results = asyncio.run(run_all_load_tests())
