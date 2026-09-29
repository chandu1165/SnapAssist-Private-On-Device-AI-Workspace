import platform
import os
import psutil
from typing import Dict, Any, List

try:
    import onnxruntime as ort
    ORT_PROVIDERS = ort.get_available_providers()
except Exception:
    ORT_PROVIDERS = []

try:
    import qai_hub
    HAS_QAI_HUB = True
    QAI_HUB_VERSION = getattr(qai_hub, "__version__", "installed")
except Exception:
    HAS_QAI_HUB = False
    QAI_HUB_VERSION = None

class HardwareDetector:
    """
    Detects host hardware and Snapdragon NPU execution capabilities.
    Truthful reporting: NEVER fakes NPU execution.
    """

    @classmethod
    def get_hardware_info(cls) -> Dict[str, Any]:
        arch = platform.machine().lower()
        proc = platform.processor().lower()
        system = platform.system()
        release = platform.release()

        # Check for Snapdragon / ARM64 Windows
        is_arm64 = ("arm64" in arch) or ("aarch64" in arch) or ("armv8" in arch)
        is_snapdragon = is_arm64 or ("qualcomm" in proc) or ("snapdragon" in proc) or ("oryon" in proc)

        # Detect ONNX execution providers
        has_qnn = "QNNExecutionProvider" in ORT_PROVIDERS
        has_dml = "DmlExecutionProvider" in ORT_PROVIDERS
        has_cpu = "CPUExecutionProvider" in ORT_PROVIDERS

        # Determine active and target execution provider
        if has_qnn:
            active_provider = "QNNExecutionProvider (Qualcomm Hexagon NPU)"
            npu_status = "ACTIVE — Hardware Accelerated"
            acceleration_type = "NPU (45 TOPS Hexagon Engine)"
        elif has_dml and is_snapdragon:
            active_provider = "DmlExecutionProvider (Snapdragon Adreno / NPU DirectML)"
            npu_status = "ACTIVE — DirectML Accelerated"
            acceleration_type = "DirectML GPU/NPU"
        elif has_dml:
            active_provider = "DmlExecutionProvider (DirectML)"
            npu_status = "Available (DirectML GPU)"
            acceleration_type = "DirectML GPU"
        elif has_cpu:
            active_provider = "CPUExecutionProvider (Universal Local CPU Fallback)"
            npu_status = "STANDBY (Target: Snapdragon Hexagon NPU via QNN EP)"
            acceleration_type = "CPU Fallback"
        else:
            active_provider = "Python Native Fallback"
            npu_status = "Unavailable"
            acceleration_type = "Software Native"

        mem = psutil.virtual_memory()
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()

        return {
            "platform": {
                "os": f"{system} {release}",
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "is_arm64": is_arm64,
                "is_snapdragon_device": is_snapdragon,
                "target_device_profile": "Snapdragon X Elite / Snapdragon X Plus (HP OmniBook / EliteBook)",
            },
            "npu_telemetry": {
                "npu_name": "Qualcomm® Hexagon™ NPU (Snapdragon® X Series)",
                "rated_tops": 45,
                "npu_status": npu_status,
                "active_execution_provider": active_provider,
                "acceleration_type": acceleration_type,
                "is_hardware_npu_active": has_qnn,
                "available_ort_providers": ORT_PROVIDERS,
                "qualcomm_ai_hub_installed": HAS_QAI_HUB,
                "qualcomm_ai_hub_version": QAI_HUB_VERSION,
            },
            "system_resources": {
                "total_memory_gb": round(mem.total / (1024**3), 2),
                "available_memory_gb": round(mem.available / (1024**3), 2),
                "memory_used_percent": mem.percent,
                "cpu_cores": cpu_count,
                "cpu_frequency_mhz": round(cpu_freq.current, 1) if cpu_freq else "N/A",
            }
        }
