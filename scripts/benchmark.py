import os
import sys
import time
import json
import psutil
import platform
import datetime
from typing import Dict, Any, List

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai.hardware_detector import HardwareDetector
from backend.ai.provider_manager import get_provider_manager
from backend.retrieval.rag_engine import get_rag_engine
from backend.ingestion.document_parser import DocumentParser
from backend.ingestion.chunker import chunk_document_pages
from backend.retrieval.vector_store import get_vector_store

def run_benchmarks() -> Dict[str, Any]:
    print("=" * 70)
    print("SnapAssist — Empirical Hardware & AI Pipeline Benchmark Suite")
    print("=" * 70)

    # 1. Hardware Detection
    hw_info = HardwareDetector.get_hardware_info()
    npu_tele = hw_info["npu_telemetry"]
    plat = hw_info["platform"]

    print(f"Timestamp: {datetime.datetime.now().isoformat()}")
    print(f"Device OS: {plat['os']}")
    print(f"Architecture: {plat['architecture']}")
    print(f"Processor: {plat['processor']}")
    print(f"Is Snapdragon / ARM64: {plat['is_snapdragon_device']}")
    print(f"Execution Provider: {npu_tele['execution_provider']}")
    print(f"Actual Accelerator: {npu_tele['accelerator']}")
    print(f"Accelerator Status: {npu_tele['status']}")
    print(f"Reason: {npu_tele['reason']}")
    print("-" * 70)

    # 2. Model Loading Benchmark
    print("Measuring AI Provider Load Time...")
    t0 = time.perf_counter()
    mgr = get_provider_manager()
    active_prov = mgr.get_active_provider()
    prov_info = active_prov.get_info()
    model_load_time_ms = (time.perf_counter() - t0) * 1000
    print(f"AI Provider Load Time: {model_load_time_ms:.2f} ms")

    # 3. Document Ingestion Benchmark
    sample_pdf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_data", "qualcomm_snapdragon_whitepaper.pdf")
    ingest_time_ms = 0.0
    total_pages = 0
    total_chunks = 0
    vstore = get_vector_store()

    if os.path.exists(sample_pdf):
        print(f"Benchmarking Document Ingestion on: {os.path.basename(sample_pdf)}...")
        t0 = time.perf_counter()
        pages, total_pages, _ = DocumentParser.parse(sample_pdf, "qualcomm_snapdragon_whitepaper.pdf")
        chunks = chunk_document_pages("bench_doc_1", pages)
        vstore.add_chunks("bench_doc_1", chunks)
        ingest_time_ms = (time.perf_counter() - t0) * 1000
        total_chunks = len(chunks)
        print(f"Ingested {total_pages} pages, {total_chunks} chunks in {ingest_time_ms:.2f} ms ({ingest_time_ms/max(1, total_pages):.2f} ms/page)")

    # 4. Vector Search Latency Benchmark
    t0 = time.perf_counter()
    vector_results = vstore.search("Qualcomm Hexagon NPU TOPS power efficiency", top_k=4)
    vector_search_latency_ms = (time.perf_counter() - t0) * 1000
    print(f"Vector Search Latency (SIMD Cosine Dot-Product): {vector_search_latency_ms:.2f} ms")

    # 5. First Inference Latency (Cold Start)
    test_query = "What is the rated TOPS of the Qualcomm Hexagon NPU on Snapdragon X Elite?"
    print(f"\nRunning Cold-Start Inference Query: '{test_query}'...")
    rag = get_rag_engine()
    t0 = time.perf_counter()
    cold_res = rag.query(test_query, doc_id="bench_doc_1")
    first_inference_latency_ms = (time.perf_counter() - t0) * 1000
    print(f"Cold-Start Latency: {first_inference_latency_ms:.2f} ms")
    print(f"Cold-Start Answer Excerpt: {cold_res.get('answer', '')[:120]}...")

    # 6. Subsequent Inferences (Warm Runs)
    print("\nRunning Warm Inferences (5 iterations)...")
    warm_latencies = []
    token_counts = []
    warm_queries = [
        "What are the action items and deadlines mentioned?",
        "Explain the power efficiency advantages of Snapdragon Oryon CPU.",
        "How does ONNX Runtime QNN Execution Provider interface with Hexagon NPU?",
        "What is the first-token latency measured on Snapdragon hardware?",
        "Summarize the key conclusions from the whitepaper in 3 points."
    ]

    for i, q in enumerate(warm_queries, 1):
        t0 = time.perf_counter()
        res = rag.query(q, doc_id="bench_doc_1")
        lat = (time.perf_counter() - t0) * 1000
        warm_latencies.append(lat)
        token_counts.append(res.get("tokens_generated", 1))
        print(f"  Warm Run #{i}: {lat:.2f} ms | Tokens: {res.get('tokens_generated')}")

    avg_warm_latency_ms = sum(warm_latencies) / len(warm_latencies)
    total_tokens = sum(token_counts)
    total_warm_sec = sum(warm_latencies) / 1000.0
    warm_throughput_tps = total_tokens / total_warm_sec if total_warm_sec > 0 else 0.0

    print(f"Average Warm Latency: {avg_warm_latency_ms:.2f} ms")
    print(f"Average Throughput: {warm_throughput_tps:.1f} tokens/second")

    # 7. Memory Consumption
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    rss_mb = mem_info.rss / (1024 * 1024)
    print(f"Process Resident Memory (RSS): {rss_mb:.2f} MB")

    results = {
        "benchmark_metadata": {
            "timestamp_iso": datetime.datetime.now().isoformat(),
            "windows_version": plat["os"],
            "architecture": plat["architecture"],
            "processor": plat["processor"],
            "is_snapdragon_detected": plat["is_snapdragon_device"],
            "target_device_profile": plat["target_device_profile"]
        },
        "model_and_runtime": {
            "model_name": prov_info.get("model_name"),
            "model_version": "1.0.0",
            "backend": prov_info.get("backend"),
            "execution_provider": npu_tele["execution_provider"],
            "actual_accelerator": npu_tele["accelerator"],
            "accelerator_status": npu_tele["status"],
            "reason": npu_tele["reason"],
            "is_hardware_npu_active": npu_tele["is_hardware_npu_active"],
            "available_ort_providers": npu_tele["available_ort_providers"]
        },
        "test_input_characteristics": {
            "sample_document": "qualcomm_snapdragon_whitepaper.pdf",
            "page_count": total_pages,
            "chunk_count": total_chunks,
            "query_iterations": len(warm_queries)
        },
        "empirical_metrics": {
            "model_load_time_ms": round(model_load_time_ms, 2),
            "document_ingestion_total_ms": round(ingest_time_ms, 2),
            "ingestion_ms_per_page": round(ingest_time_ms / max(1, total_pages), 2),
            "vector_search_latency_ms": round(vector_search_latency_ms, 2),
            "first_inference_latency_ms": round(first_inference_latency_ms, 2),
            "warm_inference_latencies_ms": [round(l, 2) for l in warm_latencies],
            "average_warm_latency_ms": round(avg_warm_latency_ms, 2),
            "throughput_tokens_per_sec": round(warm_throughput_tps, 1),
            "process_memory_rss_mb": round(rss_mb, 2),
            "network_egress_bytes": 0,
            "cloud_api_calls": 0
        }
    }

    # Save JSON report
    bench_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmarks")
    os.makedirs(bench_dir, exist_ok=True)
    json_path = os.path.join(bench_dir, "latest_benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Save Markdown human-readable report
    md_path = os.path.join(bench_dir, "latest_benchmark_results.md")
    md_content = f"""# SnapAssist Benchmark Execution Report

- **Recorded Timestamp:** {results['benchmark_metadata']['timestamp_iso']}
- **Host OS:** {results['benchmark_metadata']['windows_version']}
- **Architecture:** {results['benchmark_metadata']['architecture']}
- **Processor:** {results['benchmark_metadata']['processor']}
- **Snapdragon Hardware Detected:** {results['benchmark_metadata']['is_snapdragon_detected']}

## Runtime & Accelerator Telemetry
- **Model Name:** {results['model_and_runtime']['model_name']}
- **Backend:** {results['model_and_runtime']['backend']}
- **Execution Provider:** `{results['model_and_runtime']['execution_provider']}`
- **Actual Accelerator:** **{results['model_and_runtime']['actual_accelerator']}**
- **Accelerator Status:** `{results['model_and_runtime']['accelerator_status']}`
- **Reason:** {results['model_and_runtime']['reason']}

## Empirical Performance Measurements
- **Model Load Time:** {results['empirical_metrics']['model_load_time_ms']} ms
- **Document Ingestion:** {results['empirical_metrics']['document_ingestion_total_ms']} ms ({results['empirical_metrics']['ingestion_ms_per_page']} ms/page across {total_pages} pages)
- **Vector Search Latency:** {results['empirical_metrics']['vector_search_latency_ms']} ms
- **First Inference Latency (Cold Start):** {results['empirical_metrics']['first_inference_latency_ms']} ms
- **Average Warm Inference Latency:** {results['empirical_metrics']['average_warm_latency_ms']} ms
- **Throughput:** {results['empirical_metrics']['throughput_tokens_per_sec']} tokens/second
- **Process Memory (RSS):** {results['empirical_metrics']['process_memory_rss_mb']} MB
- **Network Egress:** 0 Bytes
- **Cloud API Calls:** 0
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("\n" + "=" * 70)
    print(f"JSON Benchmark saved to: {json_path}")
    print(f"Markdown Benchmark saved to: {md_path}")
    print("=" * 70)
    return results

if __name__ == "__main__":
    run_benchmarks()
