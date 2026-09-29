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

        # Determine exact execution provider, accelerator, status, and reason
        if has_qnn:
            execution_provider = "QNNExecutionProvider"
            accelerator = "Qualcomm Hexagon NPU"
            status = "ACTIVE"
            reason = "QNN Execution Provider is registered and targeting the Qualcomm Hexagon NPU."
            active_provider_label = "QNNExecutionProvider (Qualcomm Hexagon NPU)"
            npu_status = "ACTIVE — Hardware Accelerated"
            acceleration_type = "NPU (45 TOPS Hexagon Engine Design Target)"
        elif has_dml and is_snapdragon:
            execution_provider = "DmlExecutionProvider"
            accelerator = "Snapdragon Adreno GPU / DirectML"
            status = "ACTIVE"
            reason = "DirectML provider active on Snapdragon architecture."
            active_provider_label = "DmlExecutionProvider (Snapdragon Adreno)"
            npu_status = "ACTIVE — DirectML Accelerated"
            acceleration_type = "DirectML GPU/NPU"
        elif has_dml:
            execution_provider = "DmlExecutionProvider"
            accelerator = "GPU (DirectML)"
            status = "FALLBACK"
            reason = "DirectML GPU active; QNN NPU provider not loaded on host."
            active_provider_label = "DmlExecutionProvider (DirectML)"
            npu_status = "DirectML Fallback"
            acceleration_type = "DirectML GPU"
        elif has_cpu:
            execution_provider = "CPUExecutionProvider"
            accelerator = "CPU"
            status = "FALLBACK"
            if is_snapdragon:
                reason = "CPU Fallback active on Snapdragon host — QNN EP driver required for Hexagon NPU."
            else:
                reason = "CPU Fallback — QNN Execution Provider is available on Windows 11 ARM64 Snapdragon hardware. Current host is x86_64."
            active_provider_label = "CPUExecutionProvider (Local CPU Fallback)"
            npu_status = "CPU FALLBACK — QNN provider unavailable on host"
            acceleration_type = "CPU Fallback"
        else:
            execution_provider = "PythonNative"
            accelerator = "CPU"
            status = "UNAVAILABLE"
            reason = "ONNX Runtime not initialized; running Python software fallback."
            active_provider_label = "Python Native Fallback"
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
                "npu_name": "Qualcomm® Hexagon™ NPU (Snapdragon® X Series Design Target)",
                "rated_tops_design_target": 45,
                "npu_status": npu_status,
                "execution_provider": execution_provider,
                "accelerator": accelerator,
                "status": status,
                "reason": reason,
                "active_execution_provider": active_provider_label,
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
