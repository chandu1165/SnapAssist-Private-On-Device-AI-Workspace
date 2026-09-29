from typing import Dict, Any, Optional
from backend.ai.provider_base import AIProvider
from backend.ai.local_llm_provider import LocalLLMProvider
from backend.ai.local_onnx_provider import LocalONNXProvider
from backend.ai.qualcomm_aihub_provider import QualcommAIHubProvider
from backend.ai.hardware_detector import HardwareDetector

class ProviderManager:
    """
    Manages AIProvider selection and routing.
    Automatically identifies Snapdragon NPU acceleration and configures providers.
    """
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {
            "local_onnx": LocalONNXProvider(),
            "qualcomm_ai_hub": QualcommAIHubProvider(),
            "local_llm": LocalLLMProvider(),
        }
        self.active_provider_key = self._auto_select_provider()

    def _auto_select_provider(self) -> str:
        """
        Auto-detection hierarchy:
        1. Snapdragon/Qualcomm accelerated backend (QNN or DirectML on Snapdragon)
        2. Local ONNX CPU
        3. Local LLM native
        """
        hw = HardwareDetector.get_hardware_info()
        npu = hw["npu_telemetry"]
        
        if npu.get("is_hardware_npu_active") or "QNN" in npu.get("active_execution_provider", ""):
            return "qualcomm_ai_hub"
        elif "Dml" in npu.get("active_execution_provider", ""):
            return "local_onnx"
        else:
            return "local_onnx"

    def get_active_provider(self) -> AIProvider:
        return self.providers.get(self.active_provider_key, self.providers["local_onnx"])

    def set_active_provider(self, key: str) -> bool:
        if key in self.providers:
            self.active_provider_key = key
            return True
        return False

    def list_providers(self) -> Dict[str, Any]:
        return {
            "active_key": self.active_provider_key,
            "providers": {k: p.get_info() for k, p in self.providers.items()}
        }

_manager_instance = None
def get_provider_manager() -> ProviderManager:
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ProviderManager()
    return _manager_instance
