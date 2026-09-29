# SnapAssist Benchmark Execution Report

- **Recorded Timestamp:** 2026-09-30T03:18:07.451674
- **Host OS:** Windows 10
- **Architecture:** AMD64
- **Processor:** Intel64 Family 6 Model 154 Stepping 3, GenuineIntel
- **Snapdragon Hardware Detected:** False

## Runtime & Accelerator Telemetry
- **Model Name:** Snapdragon-ONNX-Engine
- **Backend:** ONNX Runtime (CPUExecutionProvider)
- **Execution Provider:** `CPUExecutionProvider`
- **Actual Accelerator:** **CPU**
- **Accelerator Status:** `FALLBACK`
- **Reason:** CPU Fallback — QNN Execution Provider is available on Windows 11 ARM64 Snapdragon hardware. Current host is x86_64.

## Empirical Performance Measurements
- **Model Load Time:** 0.14 ms
- **Document Ingestion:** 27.76 ms (6.94 ms/page across 4 pages)
- **Vector Search Latency:** 0.28 ms
- **First Inference Latency (Cold Start):** 11.45 ms
- **Average Warm Inference Latency:** 11.87 ms
- **Throughput:** 15118.9 tokens/second
- **Process Memory (RSS):** 116.15 MB
- **Network Egress:** 0 Bytes
- **Cloud API Calls:** 0
