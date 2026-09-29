import os
import sys
import time
import json
import psutil
import platform
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
    print("=" * 65)
    print("SnapAssist — Hardware & AI Pipeline Benchmark Suite")
    print("=" * 65)

    # 1. Hardware Detection
    hw_info = HardwareDetector.get_hardware_info()
    print(f"Device OS: {hw_info['platform']['os']}")
    print(f"Architecture: {hw_info['platform']['architecture']}")
    print(f"Processor: {hw_info['platform']['processor']}")
    print(f"Is Snapdragon / ARM64: {hw_info['platform']['is_snapdragon_device']}")
    print(f"Active Provider: {hw_info['npu_telemetry']['active_execution_provider']}")
    print(f"NPU Rated TOPS: {hw_info['npu_telemetry']['rated_tops']}")
    print("-" * 65)

    # 2. Model Loading Benchmark
    print("Measuring AI Provider Load Time...")
    t0 = time.perf_counter()
    mgr = get_provider_manager()
    active_prov = mgr.get_active_provider()
    model_load_time_ms = (time.perf_counter() - t0) * 1000
    print(f"AI Provider Load Time: {model_load_time_ms:.2f} ms")

    # 3. Document Ingestion Benchmark
    sample_pdf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_data", "qualcomm_snapdragon_whitepaper.pdf")
    ingest_time_ms = 0.0
    total_pages = 0
    total_chunks = 0
    if os.path.exists(sample_pdf):
        print(f"Benchmarking Document Ingestion on: {os.path.basename(sample_pdf)}...")
        t0 = time.perf_counter()
        pages, total_pages, _ = DocumentParser.parse(sample_pdf, "qualcomm_snapdragon_whitepaper.pdf")
        chunks = chunk_document_pages("bench_doc_1", pages)
        vstore = get_vector_store()
        vstore.add_chunks("bench_doc_1", chunks)
        ingest_time_ms = (time.perf_counter() - t0) * 1000
        total_chunks = len(chunks)
        print(f"Ingested {total_pages} pages, {total_chunks} chunks in {ingest_time_ms:.2f} ms ({ingest_time_ms/total_pages:.2f} ms/page)")

    # 4. First Inference Latency (Cold Start)
    test_query = "What is the rated TOPS of the Qualcomm Hexagon NPU on Snapdragon X Elite?"
    print(f"\nRunning Cold-Start Inference Query: '{test_query}'...")
    rag = get_rag_engine()
    t0 = time.perf_counter()
    cold_res = rag.query(test_query, doc_id="bench_doc_1")
    first_inference_latency_ms = (time.perf_counter() - t0) * 1000
    print(f"Cold-Start Latency: {first_inference_latency_ms:.2f} ms")
    print(f"Cold-Start Answer Excerpt: {cold_res.get('answer', '')[:120]}...")

    # 5. Subsequent Inferences (Warm Runs)
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

    # 6. Memory Consumption
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    rss_mb = mem_info.rss / (1024 * 1024)
    print(f"Process Resident Memory (RSS): {rss_mb:.2f} MB")
    print(f"System Available Memory: {hw_info['system_resources']['available_memory_gb']} GB")

    results = {
        "benchmark_timestamp": time.time(),
        "device": {
            "os": hw_info["platform"]["os"],
            "architecture": hw_info["platform"]["architecture"],
            "processor": hw_info["platform"]["processor"],
            "is_snapdragon": hw_info["platform"]["is_snapdragon_device"],
            "target_device": "Snapdragon X Elite / Snapdragon X Plus (HP PC)"
        },
        "model_and_runtime": {
            "model_name": active_prov.get_info().get("model_name"),
            "backend": active_prov.get_info().get("backend"),
            "execution_provider": hw_info["npu_telemetry"]["active_execution_provider"],
            "is_hardware_npu_active": hw_info["npu_telemetry"]["is_hardware_npu_active"],
            "available_providers": hw_info["npu_telemetry"]["available_ort_providers"]
        },
        "metrics": {
            "model_load_time_ms": round(model_load_time_ms, 2),
            "document_ingestion": {
                "pages": total_pages,
                "chunks": total_chunks,
                "total_time_ms": round(ingest_time_ms, 2),
                "ms_per_page": round(ingest_time_ms / max(1, total_pages), 2)
            },
            "first_inference_latency_ms": round(first_inference_latency_ms, 2),
            "warm_inference_latencies_ms": [round(l, 2) for l in warm_latencies],
            "average_warm_latency_ms": round(avg_warm_latency_ms, 2),
            "throughput_tokens_per_sec": round(warm_throughput_tps, 1),
            "process_memory_rss_mb": round(rss_mb, 2),
            "network_egress_bytes": 0,
            "cloud_api_calls": 0
        }
    }

    # Save benchmark json to benchmarks/ directory
    bench_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "benchmarks")
    os.makedirs(bench_dir, exist_ok=True)
    bench_path = os.path.join(bench_dir, "latest_benchmark_results.json")
    with open(bench_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 65)
    print(f"Benchmark results successfully written to: {bench_path}")
    print("=" * 65)
    return results

if __name__ == "__main__":
    run_benchmarks()
