from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class AIProvider(ABC):
    """
    Abstract Base Class for SnapAssist AI inference backends.
    Modular interface allowing seamless transitions between:
    - Qualcomm AI Hub accelerated models (QNN on Snapdragon NPU)
    - Local ONNX Runtime execution (QNN / DirectML / CPU)
    - Local transformer / quantized lightweight LLM
    - Mock/testing provider
    """

    @abstractmethod
    def generate(self, query: str, context_chunks: List[Dict[str, Any]], conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generates grounded response given query and retrieved context chunks.
        Returns: {
            "answer": str,
            "citations": List[Dict[str, Any]],
            "latency_ms": float,
            "tokens_generated": int,
            "model_name": str,
            "backend": str,
            "execution_provider": str
        }
        """
        pass

    @abstractmethod
    def summarize(self, text: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Summarizes document content.
        summary_type: 'tldr', 'key_points', 'action_items', 'dates', 'comprehensive'
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Returns provider metadata, model name, and acceleration status."""
        pass
