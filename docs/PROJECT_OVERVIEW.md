# Project Detail — AI-Driven Event-Based Security Intelligence (EBSI)

## Project Overview
SMEs in Malaysia often lack the budget for enterprise-grade SIEM/SOC solutions. Sentinel-Node is a custom-built, lightweight security platform designed to provide a self-hosted, event-driven security operations center. The system treats every network change, login attempt, or administrative action as a "Security Event."

By building a proprietary ingestion pipeline and enrichment engines, the platform provides real-time visibility into the attack surface without the recurring costs or privacy concerns of external third-party services. It focuses on three core pillars: Event-Driven Asset Discovery, Local Geo-Network Enrichment, and AI-Driven Scoring & Advisory.

## Key Technologies
- **Event-Driven Asset Discovery:** Hybrid active/passive scanners, custom SBOM generation, and drift detection against a golden baseline.
- **Geo-Network Intelligence:** Self-hosted enrichment modules powered by local MaxMind/IP2Location datasets and STIX/TAXII threat feeds.
- **Behavioral Correlation:** Automated MITRE ATT&CK mapping and time-series trend analysis to surface anomalous chains of events.
- **AI Scoring & Advisory:** RAG-enabled LLM assistants that explain risks, recommend actions, and power ChatOps workflows.

## Project Breakdown

### Phase 1: Event-Driven Discovery & Surface Telemetry
**Objective:** Build the input layer that eliminates inventory drift by combining scheduled scans with live event ingestion.

**Key Responsibilities:**
- **Hybrid Discovery Engine:** Use Active (Nmap/Zmap) and Passive (PCAP/sniffing) techniques to maintain an always-current asset inventory.
- **Custom Event Collector:** Capture and classify Auth, Access, Admin, and System events via a lightweight local ingestion API.
- **SBOM & Dependency Insight:** Generate SBOM artifacts from local runtimes to expose vulnerable packages and hidden services.
- **Golden Image Watcher:** Compare inbound signals against a known-good baseline to immediately flag unauthorized changes.
- **Skills:** API development with FastAPI, Python networking, CVE/NVD data integration.

### Phase 2: Geo-Network Intelligence & Behavioral Correlation
**Objective:** Build the enrichment layer that adds high-fidelity context to every event before it reaches analysts.

**Key Responsibilities:**
- **Local Enrichment Modules:** Operate a sovereign Geo-Network engine that spots "Impossible Travel" and high-risk origins such as VPNs, proxies, and Tor exits.
- **Localized CTI Pipeline:** Ingest STIX/TAXII indicators from MyCERT to highlight Malaysia-specific adversary activity.
- **Behavioral Mapping:** Chain multi-step event sequences (e.g., "Admin Login" → "VPN Detected" → "Unauthorized DB Access") into MITRE ATT&CK narratives.
- **Historical Trend Analysis:** Store time-series telemetry to compute rolling posture scores and surface recurring campaigns.
- **Skills:** Data engineering with Pandas, network protocol analysis, time-series database optimization.

### Phase 3: Dynamic Threat Scoring & AI Strategic Advisory
**Objective:** Build the intelligence layer that converts raw telemetry into prioritized actions and human-friendly guidance.

**Key Responsibilities:**
- **Real-time Scoring Engine:** Calculate a live 0–100 Threat Score using event severity, asset criticality, and enrichment metadata.
- **AI Advisory Brain:** Apply RAG-enabled LLMs (Gemini/GPT-4) to summarize risks and propose remediation grounded in local playbooks.
- **Automated Playbook Generator:** Recommend executable responses (e.g., "Block IP via IPTables") aligned with the current threat narrative.
- **Interactive ChatOps & Dashboard:** Deliver natural-language status checks through React dashboards and Telegram/Discord integrations.
- **Skills:** LangChain-based LLM orchestration, React + Tailwind CSS, Node.js/WebSocket messaging.

## Project Benefits
- **Cost Efficiency:** All enrichment, GeoIP, and CTI modules run locally, eliminating recurring API spend.
- **Event-Driven Fidelity:** The pipeline elevates authentication, administration, and data-access telemetry into actionable security evidence.
- **Operational Simplicity:** SMEs gain a "Virtual SOC" without third-party data sharing or heavy hardware footprints.
- **Career Readiness:** Team members master ingestion pipelines, CTI processing, AI copilots, and full-stack telemetry visualization.

## Programming Languages & Tools
- **Backend:** Python (FastAPI) for ingestion/orchestration, Node.js for ChatOps services.
- **Databases:** PostgreSQL (inventory state), Redis (event queue), InfluxDB (scoring and trend analytics).
- **Intelligence Sources:** MyCERT API, MITRE ATT&CK, local MaxMind datasets.
- **AI & Automation:** LangChain, Google Gemini API, Docker, n8n for workflow automation.

## Conclusion
EBSI layers continuous discovery, sovereign enrichment, and AI-powered guidance into a single Sentinel-Node stack—providing Malaysian SMEs with real-time visibility and prescriptive defense without the overhead of traditional SIEM/SOC products.