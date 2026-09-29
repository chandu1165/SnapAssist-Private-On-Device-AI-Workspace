# SnapAssist: 2–3 Minute Live Spoken Pitch Script

> **Setting:** Qualcomm Snapdragon® AI Lab Build & Present Challenge 2026  
> **Presenter:** Aditya  
> **Pacing:** Clear, professional, confident (~140 words per minute, 2:45 total duration)

---

### [0:00 – 0:30] Hook & The Problem
*"Good day, esteemed judges and fellow engineers. Over the last two years, generative AI has transformed productivity. But that productivity has come with a critical risk: every time you ask a cloud chatbot to summarize a legal contract, debug proprietary code, analyze an internal financial report, or review student research notes, that confidential data leaves your machine.*

*Cloud AI introduces compliance liabilities, creates persistent internet dependency, racks up API costs, and introduces unpredictable latency. For confidential work, cloud processing isn't always appropriate."*

---

### [0:30 – 1:00] Solution & Core Value Proposition
*"That is why I built **SnapAssist** — a private, on-device AI workspace engineered specifically for Snapdragon-powered Windows Copilot+ PCs.*

*Our tagline: **'Your files. Your AI. Your device.'***

*SnapAssist allows users to drag in PDFs, Word documents, technical logs, and screenshots, and immediately search, summarize, and converse with their personal files. Every single step—file parsing, chunking, vector embeddings, semantic retrieval, and contextual synthesis—executes locally on this laptop with zero external data egress."*

---

### [1:00 – 1:45] Live Demonstration (Guided Walkthrough)
*"Let me show you how it works in real time:*

*First, we open the **Privacy Dashboard**. Notice our verifiable local audit log showing 'Cloud Uploads: 0', 'AI API Calls: 0', 'Network Egress: 0 Bytes'.*

*Now, I’ll drag and drop this 4-page technical whitepaper on Qualcomm Snapdragon architecture. In just 27 milliseconds—under 7 milliseconds per page—our PyMuPDF parser extracts the structure, creates overlapping semantic chunks, and builds a dense vector index in local SQLite.*

*Let’s switch to the **AI Workspace** and ask:*  
> *'Summarize this document and identify the three most important action items.'*

*SnapAssist searches the local vector space using SIMD cosine dot-products, extracts matching passages, and generates a grounded response. Notice the citation badges next to every claim: `[Whitepaper Page 4]`. If I click a citation, the drawer opens showing the exact verified source text.*

*Next, let's test our local vision pipeline in **Image Analysis**. I’ll upload a system architecture screenshot. Our OpenCV engine analyzes the visual contours, classifies it as a Dark Mode Dashboard, and extracts text so we can query the image directly.*

*Finally, we open the **Performance Dashboard**. Here is our truthful hardware telemetry displaying active execution providers, accelerator status, and detailed reasons."*

---

### [1:45 – 2:20] Why Snapdragon & Technical Architecture
*"Why is Snapdragon critical to SnapAssist?*

*Snapdragon X Elite introduces a dedicated Hexagon NPU with a 45 TOPS design target and high-bandwidth unified LPDDR5x memory.*

*Our architecture leverages ONNX Runtime with the Qualcomm Neural Network (QNN) Execution Provider (`QNNExecutionProvider`) and DirectML, offloading neural execution from the CPU.*

*Crucially, we do not fake NPU usage or fabricate benchmark numbers. Our automated test suite features 21 unit and security tests, and our hardware detector honestly reports active providers across both ARM64 Snapdragon hardware and x86_64 host CPU fallbacks."*

---

### [2:20 – 2:45] Conclusion & Future Impact
*"To prove our offline resilience, I can sever the Wi-Fi completely: every single query, summary, and vector search continues running with identical speed.*

*SnapAssist is open-source, fully functional, and ready for immediate deployment with a single PowerShell command (`.\run.ps1`).*

*SnapAssist proves that privacy, speed, and intelligence can live harmoniously on Snapdragon PCs. Your files, your AI, on your device. Thank you."*
