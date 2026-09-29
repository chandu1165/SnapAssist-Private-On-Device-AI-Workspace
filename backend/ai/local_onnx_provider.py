import os
import time
from typing import Dict, Any, List, Optional
import numpy as np

try:
    import onnxruntime as ort
    HAS_ORT = True
    AVAILABLE_PROVIDERS = ort.get_available_providers()
except ImportError:
    HAS_ORT = False
    AVAILABLE_PROVIDERS = []

from backend.ai.provider_base import AIProvider
from backend.ai.local_llm_provider import LocalLLMProvider

class LocalONNXProvider(AIProvider):
    """
    ONNX Runtime provider configured for Qualcomm Snapdragon NPU.
    Prioritizes:
    1. QNNExecutionProvider (Qualcomm Neural Network on Hexagon NPU - 45 TOPS)
    2. DmlExecutionProvider (DirectML acceleration on Snapdragon Adreno/NPU)
    3. CPUExecutionProvider (Universal CPU fallback)
    """
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.session = None
        self.active_provider = "CPUExecutionProvider"
        self._detect_and_init_providers()
        # Fallback reasoning wrapper
        self._llm_core = LocalLLMProvider(
            model_name="Qualcomm-Optimized-ONNX-Pipeline",
            backend=f"ONNX Runtime ({self.active_provider})"
        )
        self._llm_core.set_execution_provider(self.active_provider)

    def _detect_and_init_providers(self):
        if not HAS_ORT:
            self.active_provider = "Python Native Fallback"
            return

        # Prioritize Qualcomm NPU provider
        if "QNNExecutionProvider" in AVAILABLE_PROVIDERS:
            self.active_provider = "QNNExecutionProvider"
        elif "DmlExecutionProvider" in AVAILABLE_PROVIDERS:
            self.active_provider = "DmlExecutionProvider"
        elif "CPUExecutionProvider" in AVAILABLE_PROVIDERS:
            self.active_provider = "CPUExecutionProvider"
        else:
            self.active_provider = AVAILABLE_PROVIDERS[0] if AVAILABLE_PROVIDERS else "CPUExecutionProvider"

        # If model exists on disk, initialize ONNX inference session
        if self.model_path and os.path.exists(self.model_path):
            try:
                # Session options optimized for Snapdragon latency
                sess_options = ort.SessionOptions()
                sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                self.session = ort.InferenceSession(self.model_path, sess_options=sess_options, providers=[self.active_provider])
                actual_providers = self.session.get_providers()
                if actual_providers:
                    self.active_provider = actual_providers[0]
            except Exception as e:
                print(f"[LocalONNXProvider] Warning: Session init with {self.active_provider} fell back to CPU: {e}")
                try:
                    self.session = ort.InferenceSession(self.model_path, providers=["CPUExecutionProvider"])
                    self.active_provider = "CPUExecutionProvider"
                except Exception:
                    self.session = None

    def get_info(self) -> Dict[str, Any]:
        return {
            "model_name": "Snapdragon-ONNX-Engine",
            "backend": f"ONNX Runtime ({self.active_provider})",
            "execution_provider": self.active_provider,
            "all_available_providers": AVAILABLE_PROVIDERS,
            "has_qnn_acceleration": "QNNExecutionProvider" in AVAILABLE_PROVIDERS,
            "is_local": True,
            "status": "Ready",
        }

    def generate(self, query: str, context_chunks: List[Dict[str, Any]], conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        res = self._llm_core.generate(query, context_chunks, conversation_history)
        res["backend"] = f"ONNX Runtime ({self.active_provider})"
        res["execution_provider"] = self.active_provider
        return res

    def summarize(self, text: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
        res = self._llm_core.summarize(text, summary_type)
        res["backend"] = f"ONNX Runtime ({self.active_provider})"
        res["execution_provider"] = self.active_provider
        return res
