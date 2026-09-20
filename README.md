# CrimeLens — Multi-Source Intelligence & Graph Analytics Platform

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Cytoscape.js](https://img.shields.io/badge/Cytoscape.js-3.28%2B-orange.svg)](https://js.cytoscape.org/)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.2%2B-lightgrey.svg)](https://networkx.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![SIH 26189](https://img.shields.io/badge/SIH%202026-Problem%2026189-darkred.svg)](https://www.sih.gov.in/)

> **Smart India Hackathon 2026** | **Problem Statement ID: 26189** | **Theme: Blockchain & Cybersecurity**  
> **Team: Cyber Titans**

---

## Table of Contents
1. [Executive Summary & Problem Statement](#1-executive-summary--problem-statement)
2. [Core Philosophy & Architectural Invariants](#2-core-philosophy--architectural-invariants)
3. [Key Capabilities & Innovations](#3-key-capabilities--innovations)
4. [System Architecture & Data Pipeline](#4-system-architecture--data-pipeline)
5. [Repository & Directory Structure](#5-repository--directory-structure)
6. [Interactive Network Explorer & Semantic Zoom](#6-interactive-network-explorer--semantic-zoom)
7. [Multi-Case Intelligence Catalog](#7-multi-case-intelligence-catalog)
8. [Ground-Truth Benchmark Patterns (PAT01–PAT13)](#8-ground-truth-benchmark-patterns-pat01pat13)
9. [Explainable Priority Scoring Model](#9-explainable-priority-scoring-model)
10. [Prerequisites & Quickstart](#10-prerequisites--quickstart)
11. [REST API Documentation](#11-rest-api-documentation)
12. [Automated Verification & Smoke Test Suite](#12-automated-verification--smoke-test-suite)
13. [Developer & Contribution Guide](#14-developer--contribution-guide)

---

## 1. Executive Summary & Problem Statement

Modern criminal syndicates operate across fragmented and siloed data streams:
- **First Information Reports (FIRs)** with conflicting witness statements and unverified alibis.
- **Telecommunications Data (CDRs)** spanning hundreds of cell towers and burner SIM cards.
- **Financial Ledgers** characterized by multi-hop fund dispersion, rapid smurfing, and nocturnal transfers.
- **Smart City Surveillance** tracking Automated Number Plate Recognition (ANPR) and facial recognition.
- **Open-Source Intelligence (OSINT)** and social media telemetry.

Manual correlation across these disparate sources is slow, susceptible to confirmation bias, and fails to expose critical bridge conduits, alias identities, or spatial-temporal contradictions.

**CrimeLens** is a modern intelligence workstation and graph analytics platform that unifies multi-modal investigative streams into a high-performance **Temporal Knowledge Graph**. It computes explainable **Investigation Priority Rankings**, detects anomalous communication surges and structuring patterns, preserves competing alibis under explicit `UNRESOLVED CONFLICT` statuses, and provides an end-to-end evidence provenance trail for every link and finding.

---

## 2. Core Philosophy & Architectural Invariants

CrimeLens is engineered around strict legal and forensic principles:

1. **Fact $\neq$ Inference $\neq$ Recommendation**: The platform rigorously distinguishes between directly observed evidence (`FACT`), analytical conclusions (`INFERENCE`), and tactical investigative suggestions (`RECOMMENDATION`).
2. **Immutable Provenance on Every Relationship**: A relationship in CrimeLens is never just an anonymous line. Every edge carries an evidentiary provenance payload: `source_record_id`, `source_type`, `timestamp`, `evidence_class` (`OBSERVED`), `confidence`, and `reliability`.
3. **Investigation Priority (Never Guilt)**: CrimeLens serves as an investigative decision-support tool. It outputs explainable **Investigation Priority** scores to optimize officer time—it explicitly **never** outputs guilt probabilities.
4. **Contradiction Preservation**: When independent sources disagree (e.g., a witness claiming a suspect was in Surat at 21:30 while an automated camera places him 210 km away in Ahmedabad at 21:40), CrimeLens refuses to silently overwrite or average data. It flags the finding as an `UNRESOLVED CONFLICT` with targeted analytical guidance for field resolution.
5. **Restrained Intelligence Workstation Aesthetic**: Built with a custom, high-contrast dark palette tailored for high-focus operations: deep charcoal (`#0C0E11`), warm parchment (`#EDE8DF`), antique gold (`#C59B4A`), muted moss green (`#5A7E5A`), and warning rust (`#B84F3C`).
6. **100% Offline & Local CPU Execution**: All graph analytics, community partitions, priority algorithms, and anomaly detectors execute entirely on consumer-grade CPUs with zero external LLM API calls, zero GPU requirements, and zero internet dependencies.

---

## 3. Key Capabilities & Innovations

- **Dynamic Multi-Case Intelligence Switching**: Seamlessly switch between active syndicate investigations (`CASE0001`–`CASE0006`) and historical judicial precedent cases (`CASE0101`–`CASE0106`). Command Center stats, the interactive graph, timeline delta records, anomaly detectors, and intelligence briefings immediately update to the selected case.
- **Google Maps-Style Semantic Zoom**: Cytoscape.js canvas equipped with Level-of-Detail (LOD) semantic zoom. Progressive disclosure keeps overview topologies clean, while zooming in expands local node spacing without bloating nodes, progressively unveiling names, conduits, and contextual edge badges.
- **Explainable Multi-Component Priority Engine**: Evaluates entities across 6 transparent graph and evidentiary signals, providing natural-language justifications in the slide-out Dossier Drawer.
- **Multi-Hop Path & Reachability Explorer**: A* Shortest Path, All Connecting Paths (up to 3 hops), Shared Mutual Links (Common Neighbors), and Max-Hops Reachability Radius.
- **Temporal Timeline & Pre-Incident Spike Analysis**: Reconstructs events chronologically with dedicated investigative filters (`Case Suspects`, `Pre-Incident 48h Surge`, `Critical Anomalies`, `Money Trails`, and `Telecom & Surveillance`).
- **Automated Intelligence Brief Generator**: Generates formal, restricted-distribution intelligence reports adhering to the Fact/Inference/Recommendation classification, ready for courtroom submission or one-click printing (`window.print()`).

---

## 4. System Architecture & Data Pipeline

```
                                INVESTIGATIVE DATA SOURCES
                  (FIR Reports, Telecom CDRs, Banking Ledgers, ANPR/CCTV, OSINT)
                                             │
                                             ▼
                             DATA INGESTION & NORMALIZATION
                   (Schema Validation, Entity Disambiguation, Alias Resolution)
                                             │
                                             ▼
                              TEMPORAL KNOWLEDGE GRAPH
                         (NetworkX In-Memory Multi-DiGraph)
                      96 Typed Entities  ───  364 Provenance Edges
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
              GRAPH ANALYTICS                               TEMPORAL & ANOMALIES
       - Louvain Community Partition                 - Isolation Forest Baselines
       - Betweenness & PageRank Centrality           - 48h Pre-Incident Spike Detection
       - Bridge Conduit Identification (PAT01)       - 4-Hop Layering Velocity (PAT03)
       - Multi-Signal Hidden Link Inference (PAT11)  - Spatio-Temporal Conflict Engine (PAT07)
                      └──────────────────────┬──────────────────────┘
                                             ▼
                            EXPLAINABLE PRIORITY ENGINE
                    (6-Component Weighted Formula: Net, Rel, Rec, Anom, Inc, Evid)
                                             │
                                             ▼
                            FASTAPI REST BACKEND SERVICE
                                 (Port 8000 | /api/*)
                                             │
                                             ▼
                              CRIMELENS WEB WORKSTATION
       ┌─────────────────────────────────────┴─────────────────────────────────────┐
       │  Command Center  │  Network Explorer (Cytoscape)  │  Timeline  │  Brief   │
       └───────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Repository & Directory Structure

```
CrineLens_CyberTitans/
├── apps/
│   ├── api/                          # FastAPI REST API
│   │   └── main.py                   # Case endpoints, graph queries, timeline, anomalies, brief
│   └── web/                          # Vanilla JS & CSS high-performance analytical workstation
│       ├── index.html                # Workspace markup, layout containers, modal drawers
│       ├── app.js                    # Controller: state manager, Cytoscape bindings, semantic zoom
│       ├── styles.css                # Dark intelligence workstation design system
│       └── vendor/
│           └── cytoscape.min.js      # Offline bundled graph visualization engine
├── data/
│   ├── raw/                          # Source investigation datasets
│   ├── synthetic/                    # Seeded ground-truth benchmark datasets (seed 189)
│   ├── sample/                       # Verification bundles
│   └── processed/                   # Normalized graph cache
├── graph/
│   ├── schema/
│   │   ├── loader.py                 # CSV ingestion, data normalization, alias resolution
│   │   └── graph_builder.py          # NetworkX MultiDiGraph constructor
│   └── analytics/
│       ├── analyzer.py               # Centralities, Louvain communities, bridge detection
│       ├── timeline.py               # Chronological event reconstruction & case scoping
│       └── contradictions.py         # Multi-case unresolved contradiction detection
├── ml/
│   ├── anomaly/
│   │   └── detector.py               # Isolation Forest, nocturnal transactions, structuring
│   ├── entity_resolution/
│   │   └── hidden_links.py           # Multi-signal hidden link candidate scoring (PAT11)
│   └── scoring/
│       └── priority_engine.py        # 6-component explainable priority scoring formula
├── reports/
│   └── generator.py                  # Formal intelligence briefing report generator
├── packages/
│   └── schemas/
│       └── models.py                 # Pydantic domain models & contracts
├── scripts/
│   └── run.py                        # Unified launcher for API server & frontend
├── tests/
│   ├── test_pipeline.py              # Automated pipeline test suite (8 assertions)
│   └── run_tests.py                  # Standalone verification runner
├── docker/
│   └── Dockerfile                    # Containerization specification
├── docker-compose.yml                # Docker Compose orchestration
├── start.bat                         # Windows one-click desktop launcher
├── requirements.txt                  # Python dependencies
└── README.md                         # Primary project documentation
```

---

## 6. Interactive Network Explorer & Semantic Zoom

The **Network Explorer** integrates Cytoscape.js with a **Semantic Zoom Level-of-Detail (LOD)** engine inspired by cartographic information systems:

### Tiered Level of Detail (LOD)

```
        ┌─────────────────────────────────────────────────────────────┐
        │  Tier 0: Macro Overview (< 90% Zoom)                        │
        │  • Clean global topology without visual clutter             │
        │  • Only Anchor Landmarks visible (Case, Key Bridges, Top Suspects) │
        │  • Edge labels suppressed for immediate structural clarity │
        └──────────────────────────────┬──────────────────────────────┘
                                       │ Zoom In
        ┌──────────────────────────────▼──────────────────────────────┐
        │  Tier 1: Standard Network View (90% – 128% Zoom)            │
        │  • Discloses all Person & Organization names               │
        │  • Reveals Core Conduits (layering transfers, calls)        │
        └──────────────────────────────┬──────────────────────────────┘
                                       │ Zoom In
        ┌──────────────────────────────▼──────────────────────────────┐
        │  Tier 2: Detailed Cluster View (128% – 165% Zoom)           │
        │  • Reveals secondary assets: phone numbers, bank accounts,  │
        │    vehicles, and camera nodes                               │
        │  • Primary relationship labels and directional badges appear│
        └──────────────────────────────┬──────────────────────────────┘
                                       │ Zoom In
        ┌──────────────────────────────▼──────────────────────────────┐
        │  Tier 3: Granular Forensic Inspection (≥ 165% Zoom)         │
        │  • Full contextual edge metadata: call durations, amounts   │
        │  • Local inter-node spacing opens up cleanly                │
        └─────────────────────────────────────────────────────────────┘
```

### Controlled Node Sizing Equation
To prevent nodes from bloating into massive circles when zooming into local clusters, node radii are dynamically damped in screen space:
$$\text{sizeFactor} = \text{clamp}\left(0.52,\, 1.30,\, \frac{1}{z^{0.65}}\right)$$
This ensures that zooming in expands the physical spacing between connected nodes, making complex multi-hop clusters immediately legible.

---

## 7. Multi-Case Intelligence Catalog

CrimeLens dynamically adapts across 6 active syndicate cases and 6 historical precedent cases:

| Case ID | Incident Date | Location | Crime Classification | Key Bridge Node | Tailored Anomaly Signature |
|:---|:---:|:---|:---|:---|:---|
| **CASE0001** | 2026-08-20 | Ahmedabad_Zone_5 | Syndicate Extortion | Nisha Shah (`P0005`) | 48h Call Surge, 4-Hop Layering Chain, Nocturnal Transfer |
| **CASE0002** | 2026-07-04 | Vadodara_Zone_4 | Vehicle Theft & Logistics | Imran Qureshi (`P0009`) | NH-48 Corridor Transit Velocity Spike, Burner SIM Burst |
| **CASE0003** | 2026-06-18 | Ahmedabad_Zone_5 | Commercial Burglary | Harsh Vyas (`P0016`) | Nocturnal Delivery Van Recon Passes, Cell Sector Drop |
| **CASE0004** | 2026-07-28 | Gandhinagar_Zone_2 | Online Payment Gateway Fraud | Sanjay Bhatt (`P0019`) | Rs 48,000 ATM Cashout in 12 Mins, Zero-Balance Mule Burst |
| **CASE0005** | 2026-08-05 | Vadodara_Zone_3 | Fake Invoicing & Shell Billing | Anjali Kulkarni (`P0011`) | Invoicing Without Freight Records, Shell Ledger Loop |
| **CASE0006** | 2026-08-25 | Ahmedabad_Zone_9 | Highway Armed Robbery | Ritu Shah (`P0013`) | Downstream ANPR Toll Hit, Pre-Ambush Cellular Radio Silence |
| **CASE0101–CASE0106** | 2019–2024 | Statewide Gujarat | Historical Judicial Precedents | Historical Accused | Prior Court Sentences, Tampered Vehicle Chassis, Hawala Records |

---

## 8. Ground-Truth Benchmark Patterns (PAT01–PAT13)

The underlying dataset contains 13 engineered forensic benchmark patterns:

| Pattern ID | Analytical Type | Primary Entities | Analytical Verification Signature |
|:---|:---|:---|:---|
| **PAT01** | Cross-Cluster Bridge | `P0005` (Nisha Shah) | Top betweenness centrality (0.28); sole operational bridge between Net A & Net B via secondary phone `PH0021`. |
| **PAT02** | Pre-Incident Spike | Core syndicate (`P0001`–`P0006`) | Concentrated surge of 35 voice calls in the 48h prior to extortion (vs. 0.5/day baseline). |
| **PAT03** | Multi-Hop Layering | `ACC00001` $\rightarrow$ `ACC00016` | 4 hops in 9 hours on 2026-08-19; ₹95,000 $\rightarrow$ ₹87,500 cashout (~97% balance retention). |
| **PAT04** | Identity Alias Resolution | `P0020` ("R. Mehta") $\rightarrow$ `P0003` | Resolved through shared phone `9000010003`, shared org `BlueStar_01`, matching age and address. |
| **PAT05** | Spatial-Temporal Co-Location| `P0001`, `P0009`, `P0005` | Triangulated at highway location `LOC0003` within 19 minutes on 2026-08-17. |
| **PAT06** | Emerging Cross-Edge | `P0001` $\leftrightarrow$ `P0009` | First recorded telecommunications link between previously disjoint clusters appearing Aug 15–19. |
| **PAT07** | Alibi Contradiction | `P0006` (Vijay Solanki) | FIR witness places him in Surat (21:30); automated camera captures him in Ahmedabad (21:40) — 210 km in 10 mins. |
| **PAT08** | Asset Ownership Conflict | Bike `SYN-GJ-1006` | Field informant attributes vehicle to Farida Sheikh (`P0012`); official RTO title lists Manoj Parmar (`P0013`). |
| **PAT09** | Nocturnal Anomaly | `ACC00016` $\rightarrow$ `ACC00008` | ₹2,48,000 cash transfer at 02:47 AM (45x higher than median operating baseline). |
| **PAT10** | Smurfing / Split Structuring | `ACC00013` (Manoj Parmar) | 4 transfers of ₹9,500–₹9,800 sent to 4 separate accounts within 3.5 hours. |
| **PAT11** | Multimodal Hidden Link | `P0007` (Pooja Joshi) $\leftrightarrow$ `P0012` | Inferred through 2 shared neighbors (`P0005`, `P0019`), Surat co-location, and 2-step financial route. |
| **PAT12** | Witness Corroboration | `P0004`, `P0018`, `P0001` | FIR narrative corroborated by direct CDR telecom records and bank transaction timestamps. |
| **PAT13** | Crime Scene Presence | `P0001`, `P0002`, `V0004` | CCTV facial and license plate detection at `LOC0002` during extortion window on 2026-08-20. |

---

## 9. Explainable Priority Scoring Model

CrimeLens calculates an explainable **Investigation Priority Score** ($P \in [0, 1]$) for every person in the network:

$$P = 0.25 \cdot I_{\text{net}} + 0.20 \cdot S_{\text{rel}} + 0.15 \cdot R_{\text{rec}} + 0.20 \cdot A_{\text{anom}} + 0.10 \cdot T_{\text{inc}} + 0.10 \cdot E_{\text{evid}}$$

### Component Breakdown
- **$I_{\text{net}}$ (Network Centrality)**: Normalized composite of betweenness centrality, degree, and PageRank.
- **$S_{\text{rel}}$ (Syndicate Relevance)**: Direct connectivity to identified bridge nodes and multi-case FIR suspects.
- **$R_{\text{rec}}$ (Recency of Contact)**: Temporal decay weighting for communications within the active investigation window.
- **$A_{\text{anom}}$ (Anomaly Score)**: Flags participation in nocturnal transfers, rapid structuring, or pre-incident bursts.
- **$T_{\text{inc}}$ (Incident Proximity)**: Physical or cellular presence at crime locations during incident windows.
- **$E_{\text{evid}}$ (Evidence Density)**: Total volume of corroborating records across CDR, transactions, and surveillance.

### Priority Tiers
- **Score $\ge 0.55$**: `HIGH INVESTIGATION PRIORITY`
- **Score $0.35 \le P < 0.55$**: `MEDIUM INVESTIGATION PRIORITY`
- **Score $< 0.35$**: `LOW INVESTIGATION PRIORITY`

---

## 10. Prerequisites & Quickstart

### Prerequisites
- **Python 3.10+** (Tested on Python 3.10, 3.11, 3.12, 3.13, and 3.14)
- Modern web browser (Chrome, Edge, Firefox, Brave, Safari)
- No GPU required. No external internet connection required.

### Installation & Execution

#### Option A: One-Click Windows Launch
Double-click **`start.bat`** in the repository root. This automatically verifies Python dependencies and launches the application at `http://127.0.0.1:8000`.

#### Option B: Terminal Setup
```bash
# 1. Clone the repository
git clone https://github.com/YourOrg/CrimeLens.git
cd CrimeLens

# 2. (Optional) Create a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the application
python scripts/run.py
```

#### Option C: Docker Container
```bash
docker-compose up --build
```

Access the workstation at **`http://127.0.0.1:8000`**. The workstation loads immediately without login prompts or setup friction.

---

## 11. REST API Documentation

The FastAPI backend exposes structured endpoints adhering to OpenAPI specifications:

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/api/health` | Service health status, active graph entities, and evidence counts |
| `GET` | `/api/cases` | Enumerates all 12 investigation cases with status and location metadata |
| `GET` | `/api/cases/{case_id}/summary` | Case metadata, hero metrics, active signals, and top priority leads |
| `GET` | `/api/cases/{case_id}/graph` | Cytoscape-formatted node and edge payloads with full provenance |
| `GET` | `/api/cases/{case_id}/timeline` | Case-scoped chronological event feed across telecom, banking, and surveillance |
| `GET` | `/api/cases/{case_id}/anomalies` | Case-specific anomaly signals (bursts, nocturnal transfers, structuring) |
| `GET` | `/api/cases/{case_id}/contradictions` | Preserved conflicting claims with analytical investigative guidance |
| `GET` | `/api/cases/{case_id}/hidden-links` | Multimodal inferred relationships with confidence scores and reasoning |
| `GET` | `/api/cases/{case_id}/priority-leads` | Ranked suspect list with component scoring breakdowns |
| `GET` | `/api/cases/{case_id}/report` | Formal Fact/Inference/Recommendation intelligence brief payload |
| `GET` | `/api/entities/{entity_id}` | 360° entity profile, centralities, connected evidence, and alias links |

Interactive Swagger documentation is available at **`http://127.0.0.1:8000/docs`**.

---

## 12. Automated Verification & Smoke Test Suite

CrimeLens includes an automated test runner that validates all analytical pipelines, graph construction algorithms, and evidentiary contracts:

```bash
python tests/run_tests.py
```

### Test Results Output
```text
==================================================
 Running CrimeLens Smoke & Verification Tests
==================================================
 [PASS] Dataset Loading & Validation
 [PASS] Graph Construction & Provenance
 [PASS] Bridge Node & Centrality Detection
 [PASS] Explainable Priority Engine
 [PASS] Anomaly Detection (Spikes & Night Txns)
 [PASS] Unresolved Contradiction Preservation
 [PASS] Timeline Event Reconstruction
 [PASS] Hidden Link Discovery
--------------------------------------------------
 Results: 8/8 tests passed.
 ALL VERIFICATION CHECKS SUCCESSFUL!
```

---

## 13. Developer & Contribution Guide

To extend or customize CrimeLens:

- **Frontend Interface**: Modify `apps/web/index.html`, `apps/web/styles.css`, and `apps/web/app.js`. Cytoscape graph styles and semantic zoom thresholds are configured in `renderCytoscapeGraph()` in `apps/web/app.js`.
- **FastAPI Endpoints**: Add or refine REST routes in `apps/api/main.py`.
- **Data Schemas & CSV Ingestion**: Adjust data loaders in `graph/schema/loader.py` and Pydantic models in `packages/schemas/models.py`.
- **Graph Algorithms**: Centrality metrics, bridge detection, and community partitions reside in `graph/analytics/analyzer.py` and `graph/schema/graph_builder.py`.
- **Priority Scoring Weights**: Adjust the 6 component weights in `ml/scoring/priority_engine.py`.
- **Anomaly Detection Rules**: Add new domain-specific pattern detectors in `ml/anomaly/detector.py` and `graph/analytics/contradictions.py`.
- **Automated Testing**: Add pipeline assertions in `tests/test_pipeline.py` and run `python tests/run_tests.py`.

---

## 14. License

Distributed under the **MIT License**. See `LICENSE` for details.

Developed with pride by **Team Cyber Titans** for **Smart India Hackathon 2026** (Problem Statement ID: 26189).
