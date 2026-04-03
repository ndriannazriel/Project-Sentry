# Project Sentinel - Main README

# 🛡️ Project Sentinel: SOC-in-a-Box for Malaysian SMEs

**Project Sentinel** is a self-hosted, AI-driven Security Intelligence Platform designed specifically for Malaysian Small and Medium-sized Enterprises (SMEs). It bridges the gap between enterprise-grade security tools and small-business usability by providing autonomous threat detection, enrichment, and prescriptive remediation advice.

## 📋 Project Overview

### The 3-Student Architecture Model

```
┌─────────────────────────────────────────────────────────────────┐
│  Student 3: Intelligence Layer (The Commander)                  │
│  ├─ Risk Scoring Engine (0-100 dynamic scoring)                 │
│  ├─ AI Advisory Brain (LLM-powered RAG)                         │
│  ├─ Automated Playbook Generator                                │
│  └─ ChatOps Integration (Telegram/Discord)                      │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│  Student 2: Enrichment Layer (The Detective)                    │
│  ├─ Local Geo-Network Engine (GeoIP-based risk flagging)        │
│  ├─ CTI Ingestion Pipeline (MyCERT threat feeds)                │
│  ├─ MITRE ATT&CK Behavioral Mapping                             │
│  └─ Historical Trend Analysis                                   │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│  Student 1: Input Layer (The Senses)                            │
│  ├─ Hybrid Discovery Engine (Nmap + PCAP)                       │
│  ├─ Event Collector API (FastAPI)                               │
│  ├─ Custom SBOM Generation (CycloneDX)                          │
│  └─ Golden Image Drift Detection                                │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB+ RAM
- 20GB+ Disk Space (for threat intel DBs)
- Python 3.11+ (for development)
- Node.js 20+ (for frontend development)

### Setup

1. **Clone & Navigate**
   ```bash
   git clone https://github.com/yourusername/project-sentinel.git
   cd project-sentinel
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (especially database password & LLM API key)
   ```

3. **Start the Stack**
   ```bash
   docker-compose up -d
   ```

4. **Verify Health**
   ```bash
   docker-compose ps
   curl http://localhost:8001/health  # Student 1
   curl http://localhost:8002/health  # Student 2
   curl http://localhost:8003/health  # Student 3
   ```

5. **Access Dashboard**
   - Frontend: http://localhost:3000
   - Student 1 (Input): http://localhost:8001
   - Student 2 (Enrichment): http://localhost:8002
   - Student 3 (Intelligence): http://localhost:8003

## 📁 Project Structure

```
project-sentinel/
├── student-1-input-layer/          # Raw visibility & event ingestion
│   ├── src/
│   │   ├── discovery/               # Nmap/PCAP scanning engine
│   │   ├── event-collector/         # FastAPI ingestion service
│   │   ├── sbom-generator/          # Software Bill of Materials
│   │   └── drift-detection/         # Golden image comparison
│   ├── requirements.txt
│   └── main.py
│
├── student-2-enrichment-layer/     # Context enrichment & analysis
│   ├── src/
│   │   ├── geo-engine/              # MaxMind GeoIP processing
│   │   ├── cti-pipelines/           # MyCERT STIX/TAXII ingestion
│   │   ├── mitre-mapper/            # ATT&CK framework mapping
│   │   └── trend-analysis/          # Time-series pattern detection
│   ├── requirements.txt
│   └── main.py
│
├── student-3-intelligence-layer/   # Risk scoring & AI advisory
│   ├── src/
│   │   ├── risk-engine/             # Dynamic 0-100 scoring algorithm
│   │   ├── ai-advisor/              # LLM + RAG integration
│   │   └── playbook-engine/         # Automated remediation playbooks
│   ├── requirements.txt
│   └── main.py
│
├── frontend/                        # React dashboard & ChatOps UI
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker/                          # Multi-stage Dockerfiles
├── infra/                           # Infrastructure & data stores
│   ├── postgres/                    # Database schemas
│   ├── geoip-db/                    # MaxMind GeoIP2 databases
│   ├── cti/                         # Threat intelligence feeds
│   ├── golden-images/               # Baseline configurations
│   └── playbooks/                   # Automated remediation playbooks
│
├── docs/                            # Architecture & deployment docs
├── docker-compose.yml               # Orchestration
├── .env.example                     # Configuration template
└── README.md
```

## 🔧 Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11 (FastAPI), Node.js (n8n) |
| Frontend | React 18, Tailwind CSS, WebSockets |
| Database | PostgreSQL 16 (time-series optimized) |
| Cache | Redis 7 |
| Orchestration | Docker Compose |
| Threat Intel | STIX/TAXII, MyCERT feeds |
| GeoIP | MaxMind GeoLite2 (self-hosted) |
| LLM Integration | Gemini Pro, GPT-4, Claude 3 |

## 📊 Core Features

### Student 1: Input Layer (The Senses)
- ✅ **Hybrid Asset Discovery**: Nmap active + PCAP passive scanning
- ✅ **Event Ingestion**: Auth, Access, Admin, System event types
- ✅ **SBOM Generation**: CycloneDX format with NVD/CVE integration
- ✅ **Drift Detection**: Real-time comparison vs. golden baseline

### Student 2: Enrichment Layer (The Detective)
- ✅ **Geolocation Analysis**: Impossible travel, VPN/Tor flagging
- ✅ **Local CTI Pipeline**: MyCERT-specific threat indicators
- ✅ **MITRE ATT&CK Mapping**: Automated technique classification
- ✅ **Trend Detection**: Recurring attack pattern analysis

### Student 3: Intelligence Layer (The Commander)
- ✅ **Risk Scoring**: Dynamic 0-100 algorithm based on severity + criticality
- ✅ **AI Advisory**: RAG-powered LLM for prescriptive guidance
- ✅ **Playbook Generator**: Context-aware CLI command suggestions
- ✅ **ChatOps**: Telegram/Discord bot for natural language queries

## 🔐 Security & Privacy

- ✅ **Self-Hosted**: All threat intel processed locally; zero data exfil
- ✅ **Encryption**: TLS for inter-service communication, encrypted DB secrets
- ✅ **RBAC**: Role-based access control (Admin, Analyst, Operator)
- ✅ **Audit Logs**: All actions logged with user context
- ✅ **Dashboard Separation**: Read-only analyst vs. admin console

## 📚 Documentation

- [Architecture Deep Dive](./docs/ARCHITECTURE.md)
- [Student 1 - Input Layer](./docs/STUDENT1_README.md)
- [Student 2 - Enrichment Layer](./docs/STUDENT2_README.md)
- [Student 3 - Intelligence Layer](./docs/STUDENT3_README.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [API Reference](./docs/API_REFERENCE.md)

## 🛠️ Development

### Running Locally (Without Docker)

1. **Install dependencies**
   ```bash
   cd student-1-input-layer && pip install -r requirements.txt
   ```

2. **Start the service**
   ```bash
   python main.py
   ```

### Running Tests

```bash
pytest --cov=src tests/
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes (`git commit -m "Add feature"`)
4. Push to branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 📞 Support & Contact

For questions or issues:
- 📧 Email: sentinel@yourdomain.my
- 🐛 GitHub Issues: [Report a bug](https://github.com/yourusername/project-sentinel/issues)
- 💬 Discord: [Join our community](https://discord.gg/sentinel)

---

**Project Sentinel** © 2026 - Built with 🛡️ for Malaysian SMEs
