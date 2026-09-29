import pytest
from backend.ai.provider_manager import get_provider_manager
from backend.ai.local_llm_provider import LocalLLMProvider
from backend.ai.local_onnx_provider import LocalONNXProvider
from backend.ai.qualcomm_aihub_provider import QualcommAIHubProvider
from backend.ai.hardware_detector import HardwareDetector

def test_hardware_detector():
    hw = HardwareDetector.get_hardware_info()
    assert "platform" in hw
    assert "npu_telemetry" in hw
    assert "system_resources" in hw
    assert hw["npu_telemetry"]["rated_tops"] == 45
    # Must not falsely claim hardware NPU unless actually present
    if not hw["platform"]["is_arm64"]:
        assert hw["npu_telemetry"]["is_hardware_npu_active"] is False

def test_local_llm_provider_generation():
    provider = LocalLLMProvider()
    context = [{
        "chunk_id": "test_1",
        "doc_id": "doc_1",
        "document_name": "Test Whitepaper.pdf",
        "page_number": 2,
        "content": "Action Item: Finalize Qualcomm ONNX QNN driver before October 15, 2026.",
        "score": 0.95
    }]
    res = provider.generate("What action items are required?", context)
    assert "answer" in res
    assert len(res["citations"]) > 0
    assert res["citations"][0]["document_name"] == "Test Whitepaper.pdf"
    assert res["citations"][0]["page_number"] == 2
    assert res["latency_ms"] >= 0

def test_local_llm_provider_summarize():
    provider = LocalLLMProvider()
    text = (
        "Qualcomm Snapdragon X Elite revolutionizes on-device AI. "
        "The Hexagon NPU operates at 45 TOPS with high energy efficiency. "
        "Action Item: Submit presentation by October 15, 2026. "
        "Overall battery life reaches 20 hours on HP Copilot+ PCs."
    )
    summary = provider.summarize(text)
    assert "tldr" in summary
    assert "key_points" in summary
    assert len(summary["key_points"]) > 0
    assert len(summary["action_items"]) > 0
    assert "October 15, 2026" in str(summary["important_dates"])

def test_provider_manager_switching():
    mgr = get_provider_manager()
    assert mgr.set_active_provider("local_onnx") is True
    assert mgr.active_provider_key == "local_onnx"
    assert mgr.set_active_provider("qualcomm_ai_hub") is True
    assert mgr.active_provider_key == "qualcomm_ai_hub"
    assert mgr.set_active_provider("non_existent_key") is False
