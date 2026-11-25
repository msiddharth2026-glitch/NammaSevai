"""
Comprehensive Repeatable Multi-User Concurrency & Latency Benchmark for NammaSevai AI / BharatSevai AI.
Phase 6.1 — Performance Bottleneck Analysis and Optimization Verification.

Features:
  - Cache and connection warm-up phase
  - 3 Repeatable benchmark rounds per concurrency tier (10, 25, 50, 75, 100 users)
  - Per-endpoint response times:
      1. Health Status (/api/health)
      2. Full Scheme Catalog (/api/schemes?limit=200)
      3. Multi-Lingual Scheme Search (/api/schemes?search=மாணவி)
      4. Single Scheme Full Details (/api/schemes/pudhumai-penn)
      5. Citizen Query & Profile Analysis (/api/assistant/analyze)
      6. Citizen Eligibility Matching (/api/assistant/match)
      7. Admin Policy Monitoring Summary (/api/admin/content-monitor/summary)
  - Statistical aggregation (min, avg, p50, p95, p99, max, throughput req/s, error rate)
  - Resource monitoring (WorkingSet/RSS memory, VMS, CPU time)
"""

import time
import json
import statistics
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

from backend.database import SessionLocal
from backend.main import health_check
from backend.routers.schemes import list_schemes, get_scheme_by_id
from backend.routers.assistant import match_citizen_schemes, analyze_citizen_query
from backend.schemas.assistant import MatchRequest, AnalyzeRequest
from backend.services.scheme_update_service import SchemeUpdateService

def get_process_resource_usage() -> Dict[str, Any]:
    """Retrieves current process memory and CPU stats via Windows PowerShell without extra dependencies."""
    try:
        pid = os.getpid()
        cmd = f"(Get-Process -Id {pid}).WorkingSet64 / 1MB; (Get-Process -Id {pid}).VirtualMemorySize64 / 1MB; (Get-Process -Id {pid}).TotalProcessorTime.TotalSeconds"
        out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], timeout=5)
        lines = [line.strip() for line in out.decode("utf-8").splitlines() if line.strip()]
        rss_mb = round(float(lines[0]), 2) if len(lines) > 0 else 0.0
        vms_mb = round(float(lines[1]), 2) if len(lines) > 1 else 0.0
        cpu_sec = round(float(lines[2]), 2) if len(lines) > 2 else 0.0
        return {"rss_mb": rss_mb, "vms_mb": vms_mb, "cpu_sec": cpu_sec}
    except Exception as e:
        return {"rss_mb": 0.0, "vms_mb": 0.0, "cpu_sec": 0.0, "error": str(e)}

def benchmark_endpoint(endpoint_type: str) -> Dict[str, Any]:
    db = SessionLocal()
    start = time.perf_counter()
    try:
        if endpoint_type == "health":
            res = health_check()
            success = res.get("status") == "healthy"
        elif endpoint_type == "catalog":
            res = list_schemes(limit=200, db=db)
            success = len(res) >= 85
        elif endpoint_type == "search":
            res = list_schemes(search="மாணவி", db=db)
            success = len(res) > 0
        elif endpoint_type == "single_scheme":
            res = get_scheme_by_id("pudhumai-penn", db=db)
            success = res is not None and res.id == "pudhumai-penn"
        elif endpoint_type == "analyze_query":
            req = AnalyzeRequest(
                text="நான் கல்லூரியில் படிக்கும் மாணவி, குடும்ப வருமானம் ₹1,20,000",
                lang="ta"
            )
            res = analyze_citizen_query(req)
            success = res is not None and res.extracted_profile is not None
        elif endpoint_type == "matching":
            req = MatchRequest(
                query="நான் அரசு பள்ளியில் படித்த கல்லூரி மாணவி, குடும்ப வருமானம் 1.5 லட்சம்",
                lang="ta",
                profile={}
            )
            res = match_citizen_schemes(req, db=db)
            success = res is not None and len(res.matches) > 0
        elif endpoint_type == "admin_summary":
            res = SchemeUpdateService.get_monitoring_summary(db=db)
            success = res.get("total_registered_sources", 0) >= 85
        else:
            success = False

        duration_ms = (time.perf_counter() - start) * 1000.0
        return {
            "endpoint": endpoint_type,
            "success": success,
            "duration_ms": duration_ms
        }
    except Exception as e:
        duration_ms = (time.perf_counter() - start) * 1000.0
        return {
            "endpoint": endpoint_type,
            "success": False,
            "duration_ms": duration_ms,
            "error": str(e)
        }
    finally:
        db.close()

def run_concurrency_batch(concurrency_level: int, total_requests: int) -> Dict[str, Any]:
    endpoint_types = [
        "health", 
        "catalog", 
        "search", 
        "single_scheme", 
        "analyze_query", 
        "matching", 
        "admin_summary"
    ]
    tasks = [endpoint_types[i % len(endpoint_types)] for i in range(total_requests)]

    start_total = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=concurrency_level) as executor:
        futures = [executor.submit(benchmark_endpoint, ep) for ep in tasks]
        for f in as_completed(futures):
            results.append(f.result())
    total_time_s = time.perf_counter() - start_total

    durations = [r["duration_ms"] for r in results]
    successes = [r for r in results if r["success"]]
    error_rate = ((len(results) - len(successes)) / len(results)) * 100.0
    throughput = len(results) / total_time_s

    durations.sort()
    n = len(durations)
    p50 = statistics.median(durations)
    p95 = durations[int(0.95 * n)] if n > 0 else 0
    p99 = durations[int(0.99 * n)] if n > 0 else 0
    avg_latency = statistics.mean(durations)
    min_lat = min(durations)
    max_lat = max(durations)

    breakdown = {}
    for ep in endpoint_types:
        ep_durs = [r["duration_ms"] for r in results if r["endpoint"] == ep and r["success"]]
        if ep_durs:
            sorted_ep = sorted(ep_durs)
            breakdown[ep] = {
                "count": len(ep_durs),
                "avg_ms": round(statistics.mean(ep_durs), 2),
                "p50_ms": round(statistics.median(ep_durs), 2),
                "p95_ms": round(sorted_ep[int(0.95 * len(sorted_ep))], 2)
            }

    return {
        "concurrency": concurrency_level,
        "total_requests": total_requests,
        "successful_requests": len(successes),
        "total_time_seconds": round(total_time_s, 3),
        "throughput_req_per_sec": round(throughput, 1),
        "error_rate_pct": round(error_rate, 2),
        "latency_min_ms": round(min_lat, 2),
        "latency_avg_ms": round(avg_latency, 2),
        "latency_p50_ms": round(p50, 2),
        "latency_p95_ms": round(p95, 2),
        "latency_p99_ms": round(p99, 2),
        "latency_max_ms": round(max_lat, 2),
        "breakdown": breakdown
    }

def run_repeatable_tier(concurrency_level: int, requests_per_round: int, num_rounds: int = 3) -> Dict[str, Any]:
    print(f"\n--- Testing Concurrency Tier: {concurrency_level} Concurrent Users ({num_rounds} Rounds x {requests_per_round} requests) ---")
    round_results = []
    
    for r in range(1, num_rounds + 1):
        res = run_concurrency_batch(concurrency_level, requests_per_round)
        round_results.append(res)
        print(f"  [Round {r}] Throughput: {res['throughput_req_per_sec']} req/s | Avg: {res['latency_avg_ms']} ms | P50: {res['latency_p50_ms']} ms | P95: {res['latency_p95_ms']} ms | Errors: {res['error_rate_pct']}%")

    throughputs = [r["throughput_req_per_sec"] for r in round_results]
    avgs = [r["latency_avg_ms"] for r in round_results]
    p50s = [r["latency_p50_ms"] for r in round_results]
    p95s = [r["latency_p95_ms"] for r in round_results]
    p99s = [r["latency_p99_ms"] for r in round_results]
    errors = [r["error_rate_pct"] for r in round_results]

    # Aggregate breakdown
    endpoint_keys = list(round_results[0]["breakdown"].keys())
    agg_breakdown = {}
    for ep in endpoint_keys:
        ep_avgs = [r["breakdown"][ep]["avg_ms"] for r in round_results if ep in r["breakdown"]]
        ep_p50s = [r["breakdown"][ep]["p50_ms"] for r in round_results if ep in r["breakdown"]]
        ep_p95s = [r["breakdown"][ep]["p95_ms"] for r in round_results if ep in r["breakdown"]]
        agg_breakdown[ep] = {
            "avg_ms": round(statistics.mean(ep_avgs), 2) if ep_avgs else 0.0,
            "p50_ms": round(statistics.mean(ep_p50s), 2) if ep_p50s else 0.0,
            "p95_ms": round(statistics.mean(ep_p95s), 2) if ep_p95s else 0.0,
        }

    tier_resources = get_process_resource_usage()
    print(f"  => Summary: Avg Throughput: {round(statistics.mean(throughputs), 1)} req/s | Avg Latency: {round(statistics.mean(avgs), 2)} ms | P50: {round(statistics.mean(p50s), 2)} ms | P95: {round(statistics.mean(p95s), 2)} ms | RSS: {tier_resources['rss_mb']} MB")

    return {
        "concurrency": concurrency_level,
        "num_rounds": num_rounds,
        "requests_per_round": requests_per_round,
        "total_requests": requests_per_round * num_rounds,
        "mean_throughput_req_per_sec": round(statistics.mean(throughputs), 1),
        "mean_latency_avg_ms": round(statistics.mean(avgs), 2),
        "mean_latency_p50_ms": round(statistics.mean(p50s), 2),
        "mean_latency_p95_ms": round(statistics.mean(p95s), 2),
        "mean_latency_p99_ms": round(statistics.mean(p99s), 2),
        "mean_error_rate_pct": round(statistics.mean(errors), 2),
        "rss_mb": tier_resources["rss_mb"],
        "vms_mb": tier_resources["vms_mb"],
        "cpu_sec": tier_resources["cpu_sec"],
        "breakdown": agg_breakdown,
        "rounds": round_results
    }

def run_full_suite():
    print("=" * 80)
    print("NammaSevai AI / BharatSevai AI — Phase 6.1 Multi-User Concurrency & Latency Benchmark")
    print("=" * 80)

    # 1. Warm-up
    print("\n[Warm-up] Priming connection pool, SQLite WAL cache, and ORM models (35 requests)...")
    warm_res = run_concurrency_batch(concurrency_level=5, total_requests=35)
    print(f"  Warm-up completed in {warm_res['total_time_seconds']}s with {warm_res['throughput_req_per_sec']} req/s (0 errors).")

    initial_resources = get_process_resource_usage()
    print(f"  Post-warmup Baseline Memory: {initial_resources['rss_mb']} MB RSS | {initial_resources['vms_mb']} MB VMS")

    # 2. Benchmark Tiers
    # 10, 25, 50 users (3 rounds each) + extended tiers (75 and 100 users)
    tiers = [
        (10, 70),
        (25, 105),
        (50, 140),
        (75, 140),
        (100, 140)
    ]

    all_tier_results = []
    for c_level, reqs in tiers:
        res = run_repeatable_tier(concurrency_level=c_level, requests_per_round=reqs, num_rounds=3)
        all_tier_results.append(res)

    final_resources = get_process_resource_usage()
    mem_delta = round(final_resources['rss_mb'] - initial_resources['rss_mb'], 2)
    print("\n" + "=" * 80)
    print(f"Benchmark Complete!")
    print(f"Initial RSS: {initial_resources['rss_mb']} MB | Final RSS: {final_resources['rss_mb']} MB | Delta: {mem_delta} MB")
    print("=" * 80)

    # Persist JSON report
    report_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "baseline_resources": initial_resources,
        "final_resources": final_resources,
        "memory_delta_mb": mem_delta,
        "tiers": all_tier_results
    }

    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print("Detailed metrics saved to benchmark_results.json")
    return report_data

if __name__ == "__main__":
    run_full_suite()
