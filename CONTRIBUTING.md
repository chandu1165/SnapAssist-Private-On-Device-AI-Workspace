# Contributing to SnapAssist

Thank you for your interest in contributing to **SnapAssist — Private On-Device AI Workspace**, designed for the **Qualcomm Snapdragon® AI Lab Build & Present Challenge 2026**.

## Architecture & Code Philosophy

SnapAssist is governed by strict technical principles:
1. **Privacy & Local-First:** Core functionality must execute locally with zero cloud API reliance. Never transmit user file bytes, vector embeddings, or prompts to external servers without explicit disclosure.
2. **Snapdragon Acceleration:** Prioritize Qualcomm AI Hub models, Qualcomm Neural Network (QNN) execution provider, and DirectML hardware pipelines.
3. **Truth in Telemetry:** Never fabricate NPU execution or artificial benchmark numbers. Always query real hardware providers via `onnxruntime.get_available_providers()`.
4. **Resilience & Offline Mode:** The application must remain fully functional when network access is severed.

## Development Setup

1. Clone repository:
   ```powershell
   git clone https://github.com/adityabansal0210/SnapAssist.git
   cd snapassist
   ```

2. Run automated setup:
   ```powershell
   .\setup.ps1
   ```

3. Run test suite:
   ```powershell
   python -m pytest tests/
   ```

4. Build frontend:
   ```powershell
   cd frontend
   npm run build
   ```

## Pull Request Guidelines

- Ensure all 21+ unit and integration tests pass cleanly (`python -m pytest tests/`).
- Verify that `npm run build` generates the production bundle without TypeScript errors.
- Include benchmark measurements from `scripts/benchmark.py` if altering inference or vector indexing logic.
