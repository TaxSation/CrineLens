# CrimeLens Prototype — SIH 2026 (Problem Statement 26189) Implementation Plan

Building an investigation-grade prototype for Smart India Hackathon 2026 based on the 26-page Software Design Document, SIH pitch deck, and synthetic dataset.

## Target Architecture & Aesthetics
- **Architecture**: Modular GitHub monorepo with `apps/` (FastAPI backend + React/Vite/TypeScript frontend), `packages/schemas`, `ml/`, `graph/`, `data/`, `scripts/`, `tests/`, `reports/`.
- **Aesthetic Direction**: Modern Intelligence Workstation + Investigative Evidence Archive.
  - Charcoal/warm black base (`#111215`, `#18191E`), warm parchment/cream accents (`#EDE8DF`), antique gold/bronze highlights (`#C59B4A`), desaturated moss/olive (`#587B58`), muted terracotta/rust (`#B8533E`).
  - Zero purple/violet/lavender SaaS tropes.
- **Rules Enforced**:
  - Fact $\neq$ Inference $\neq$ Recommendation.
  - Explainable *Investigation Priority* (never guilt/criminality).
  - Unresolved Conflict preservation (no silent overwriting).
  - Evidence provenance on every edge and finding.
  - No Login/RBAC, No Copilot/LLM (per user instructions).

## Execution Phases

### Phase 1 — Modular Structure & Startup Foundation
- Create the standard CrimeLens monorepo directory tree.
- Create placeholder modules with typed interfaces and `__init__.py` files.
- Verify backend and frontend initialization.

### Phase 2 — Data Pipeline & Ingestion
- Ingest the supplied `crimelens_mini_dataset/` CSV files.
- Validate schemas, clean identifiers, parse timestamps.
- Model entities (Person, Phone, Vehicle, Location, Account, Organization, Case, FIR, etc.).
- Construct NetworkX graph with full edge provenance (`source_record_id`, `timestamp`, `evidence_class`, `confidence`, `reliability`).

### Phase 3 — Core UI (Command Center, Network Explorer, Entity Profile, Evidence)
- **Command Center**: Investigation KPI banner, active case context (`CASE0001`), alerts, anomaly feed, priority leads.
- **Network Explorer**: Cytoscape.js canvas with custom styling, zoom/pan, 1/2-hop neighborhood expansion, Louvain community coloring, bridge node tagging (`P0005`), path finding (`P0007` to `P0012`).
- **Entity Profile**: 360-degree dossier, known aliases (`P0020` $\rightarrow$ `P0003`), relationships, activity list, flagged contradictions.
- **Evidence Provenance Drawer**: Detailed evidence cards showing exact source records (CDR, Surveillance, Transactions, FIRs, OSINT).

### Phase 4 — Core Intelligence (Graph Analytics, Timeline, Priority Engine)
- **Graph Analytics**: Degree, Betweenness, PageRank, Louvain communities, bridge detection.
- **Explainable Investigation Priority**: 6-component weighted formula computing HIGH / MEDIUM / LOW with human-readable rationale.
- **Timeline Analysis**: "What Changed?" 48-hour pre-incident window (`2026-08-18` to `2026-08-19`), communication spike (35 calls), transaction layering chain (`ACC00001` $\rightarrow \dots \rightarrow$ `ACC00016`).

### Phase 5 — Optional Enhancements (P2)
- **Anomaly Detection**: Flag night-time cash transfer (`TXN00037` ₹2,48,000 at 02:47) and rapid split transfers (`ACC00013`).
- **Hidden Link Discovery**: Flag `P0007` $\leftrightarrow$ `P0012` with 3 supporting signals (common neighbors, Surat co-location, money path).
- **Contradictions**: Flag `P0006` location conflict (Surat vs. Ahmedabad) and `SYN-GJ-1006` vehicle ownership conflict.
- **Report Generation**: Formatted printable/exportable Investigation Brief with Fact/Inference/Recommendation breakdown.

### Phase 6 — Verification & Polish
- End-to-end smoke testing of the 5-minute demo script.
- Single-command launcher (`scripts/start.py` or `start.bat`).
- Update `README.md` with complete architecture and contributor guide.
