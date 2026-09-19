"""
CrimeLens Intelligence Platform — Core FastAPI Application
Provides REST endpoints for Command Center, Network Explorer, Entity Dossiers,
Timeline Analysis, Anomaly Detection, Unresolved Contradictions, and Briefs.
"""
import os
import sys
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from graph.schema.loader import dataset
from graph.schema.graph_builder import graph_instance
from graph.analytics.analyzer import analytics
from ml.scoring.priority_engine import priority_engine
from ml.anomaly.detector import anomaly_detector
from ml.entity_resolution.hidden_links import hidden_link_engine
from graph.analytics.contradictions import contradiction_detector
from graph.analytics.timeline import timeline_engine
from reports.generator import report_generator

app = FastAPI(
    title="CrimeLens Intelligence Platform API",
    version="1.0.0",
    description="Problem Statement 26189 — CrimeLens (Team Cyber Titans)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "CrimeLens Intelligence Engine",
        "version": "1.0.0",
        "problem_statement": "26189",
        "team": "Cyber Titans",
        "dataset_records": {
            "persons": len(dataset.persons),
            "locations": len(dataset.locations),
            "vehicles": len(dataset.vehicles),
            "phones": len(dataset.phones),
            "accounts": len(dataset.accounts),
            "cdr": len(dataset.cdr),
            "transactions": len(dataset.transactions),
            "surveillance": len(dataset.surveillance),
            "firs": len(dataset.firs)
        }
    }


@app.get("/api/cases")
def list_cases():
    return [
        {
            "case_id": c["case_id"],
            "case_type": c["case_type"].title(),
            "incident_date": c["incident_date"],
            "location": dataset.location_map.get(c["primary_location_id"], {}).get("location_name", c["primary_location_id"]),
            "status": c["status"].replace("_", " ").title(),
            "is_active": c["case_id"] == "CASE0001"
        }
        for c in dataset.cases
    ]


from reports.generator import report_generator, CASE_BRIEFS

CASE_SIGNALS = {
    "CASE0001": [
        {"type": "SPIKE", "label": "48h Pre-Incident Surge", "detail": "35 inter-suspect calls between Aug 18–19 (vs 0.5/day June-July baseline)"},
        {"type": "BRIDGE", "label": "Cross-Network Conduit", "detail": "Nisha Shah (P0005) bridges Net A & Net B via secondary phone PH0021"},
        {"type": "LAYERING", "label": "Velocity Transaction Chain", "detail": "4 hops in 9 hours on Aug 19 transferring Rs 95,000 ending in cash"},
        {"type": "CONFLICT", "label": "Physical Alibi Impossibility", "detail": "Vijay Solanki claimed in Surat while CCTV captures him in Ahmedabad (210 km in 10 mins)"},
        {"type": "ALIAS", "label": "Identity Ambiguity Resolved", "detail": "R. Mehta (P0020) resolved to Rahul Mehta (P0003) via shared phone and BlueStar_01"}
    ],
    "CASE0002": [
        {"type": "THEFT", "label": "Overnight Vehicle Breached", "detail": "Vehicle SYN-GJ-1005 reported stolen from Vadodara_Zone_4 overnight on 2026-07-04"},
        {"type": "SURVEILLANCE", "label": "Corridor Transit Match", "detail": "ANPR toll logs confirm stolen vehicle traversed NH-48 towards Surat"},
        {"type": "SUSPECT", "label": "Proximity Sighting", "detail": "Witness statement (FIR00006) places Farida Sheikh (P0018) in perimeter"},
        {"type": "LOGISTICS", "label": "Syndicate Transport Link", "detail": "Vehicle linked to secondary phone PH0022 and logistics coordinator Imran Qureshi"}
    ],
    "CASE0003": [
        {"type": "BURGLARY", "label": "Perimeter Breach", "detail": "Store security compromised and merchandise removed in Ahmedabad_Zone_5 on 2026-06-18"},
        {"type": "RECON", "label": "Pre-Incident Drive-by", "detail": "Harsh Vyas (P0016) spotted in delivery van during reconnaissance window"},
        {"type": "CELLULAR", "label": "Tower Registration", "detail": "Phone PH0016 active on cell tower 15 mins prior to alarm trip"}
    ],
    "CASE0004": [
        {"type": "CYBER", "label": "Phishing Siphon", "detail": "Rs 48,000 extracted from Pooja Joshi (P0014) via spoofed gateway on 2026-07-28"},
        {"type": "MULE", "label": "Mule Account Settlement", "detail": "Immediate credit to beneficiary account ACC00019 controlled by Sanjay Bhatt (P0019)"},
        {"type": "CASHOUT", "label": "Rapid ATM Liquidation", "detail": "Cash withdrawn at Surat ATM within 12 minutes of credit"}
    ],
    "CASE0005": [
        {"type": "INVOICE", "label": "Shell Billing Claim", "detail": "Complainant Tarun Sharma (P0017) billed Rs 15,500 for non-existent inventory on 2026-08-05"},
        {"type": "BENEFICIARY", "label": "Account Diverted", "detail": "Funds credited to account held by Anjali Kulkarni (P0011)"},
        {"type": "REPEATED MO", "label": "Historical Parallel", "detail": "Identical shell company invoicing format seen in 2022 fraud case CASE0102"}
    ],
    "CASE0006": [
        {"type": "ROBBERY", "label": "Highway Ambush", "detail": "Commercial transport vehicle forced off highway on 2026-08-25 night"},
        {"type": "VEHICLE", "label": "ANPR Toll Log", "detail": "Getaway vehicle SYN-GJ-1002 captured by toll surveillance 8 km downstream"},
        {"type": "SYNDICATE", "label": "Transit Interception", "detail": "Tactical execution matches historical MO of Ritu Shah transit crew"}
    ],
    "CASE0101": [
        {"type": "CONVICTED", "label": "Judicial Conviction", "detail": "Kiran Desai (P0001) and Anil Trivedi (P0004) sentenced under IPC 384/34 in 2021"},
        {"type": "ORIGIN", "label": "Syndicate Genesis", "detail": "Establishes 5-year operating history and command structure in Ahmedabad"},
        {"type": "MO MATCH", "label": "Direct Precedent", "detail": "Extortion script and vehicle intimidation identical to active CASE0001"}
    ],
    "CASE0102": [
        {"type": "CONVICTED", "label": "Conviction of Hawala Operator", "detail": "Vijay Solanki (P0006) convicted in 2022 for shell entity invoicing in Surat"},
        {"type": "CO-ACCUSED", "label": "Acquitted Accomplice", "detail": "Anil Trivedi (P0004) co-charged; acquitted on technical evidentiary grounds"},
        {"type": "CROSS-CITY", "label": "Conduit Established", "detail": "Proves pre-existing Surat-to-Ahmedabad money laundering bridge"}
    ],
    "CASE0103": [
        {"type": "CONVICTED", "label": "Transport Theft Ring", "detail": "Imran Qureshi (P0009) and Ramesh Jha (P0011) convicted in 2020"},
        {"type": "LOGISTICS", "label": "Vehicle Supply Network", "detail": "Supplied fake-plate utility vehicles for interstate criminal runs"}
    ],
    "CASE0104": [
        {"type": "ACQUITTED", "label": "Forensic Trial", "detail": "Suresh Patel (P0008) acquitted due to chain-of-custody gaps in 2023"},
        {"type": "ROLE", "label": "Operational Lookout", "detail": "Specialized in security alarm tampering and perimeter bypass"}
    ],
    "CASE0105": [
        {"type": "CONVICTED", "label": "Armed Robbery Sentence", "detail": "Ritu Shah (P0013) convicted for armed highway transit robbery in 2019"},
        {"type": "ENFORCEMENT", "label": "Syndicate Enforcer", "detail": "Provides physical deterrence and vehicle interception capabilities"}
    ],
    "CASE0106": [
        {"type": "PENDING", "label": "Charge-sheet Filed", "detail": "Manish Verma (P0015) booked under IT Act Section 66D; trial ongoing"},
        {"type": "TELECOM", "label": "SIM Procurement", "detail": "Specialized in procuring forged KYC SIM cards and burner accounts"}
    ]
}


@app.get("/api/cases/{case_id}/summary")
def get_case_summary(case_id: str = "CASE0001"):
    priorities = priority_engine.compute_all()
    anomalies = anomaly_detector.detect_for_case(case_id)
    contradictions = contradiction_detector.get_for_case(case_id)
    hidden_links = hidden_link_engine.discover_all()

    # Priority breakdown
    high_leads = [v for v in priorities.values() if v["priority"] == "HIGH"]
    high_leads.sort(key=lambda x: x["priority_score"], reverse=True)

    evidence_count = (
        len(dataset.cdr) +
        len(dataset.transactions) +
        len(dataset.surveillance) +
        len(dataset.firs) +
        len(dataset.intels) +
        len(dataset.social)
    )

    case_info = dataset.case_map.get(case_id, {
        "case_id": case_id,
        "case_type": "extortion",
        "incident_date": "2026-08-20",
        "primary_location_id": "LOC0002",
        "status": "under_investigation"
    })

    loc_obj = dataset.location_map.get(case_info.get("primary_location_id"), {})
    loc_name = loc_obj.get("location_name", "Ahmedabad_Zone_5")
    city_name = loc_obj.get("city", "Ahmedabad")

    case_signals = CASE_SIGNALS.get(case_id, CASE_SIGNALS["CASE0001"])

    # If specific case, prioritize leads mentioned in FIRs / History for that case
    case_pids = set()
    for f in dataset.firs:
        if f.get("case_id") == case_id:
            for p in dataset.persons:
                if p["name"] in f.get("report_text", "") or p["person_id"] in f.get("report_text", ""):
                    case_pids.add(p["person_id"])
    for h in dataset.criminal_history:
        if h.get("case_id") == case_id:
            case_pids.add(h.get("person_id"))

    if case_pids:
        tailored_leads = [v for v in priorities.values() if v["person_id"] in case_pids]
        tailored_leads.sort(key=lambda x: x["priority_score"], reverse=True)
        # Fallback to high_leads if empty
        if not tailored_leads:
            tailored_leads = high_leads
    else:
        tailored_leads = high_leads

    c_type = case_info.get("case_type", "extortion").replace("_", " ").upper()
    title_text = f"{c_type}: {'REPEAT OFFENDER CONVICTION' if 'CASE01' in case_id else 'SYNDICATE INVESTIGATION'}"

    return {
        "case_id": case_id,
        "title": title_text,
        "incident_date": case_info.get("incident_date", "2026-08-20"),
        "primary_location": loc_name,
        "city": city_name,
        "status": case_info.get("status", "under_investigation").replace("_", " ").upper(),
        "stats": {
            "total_entities": len(graph_instance.nodes_data),
            "persons_count": len(dataset.persons),
            "total_relationships": len(graph_instance.edges_data),
            "evidence_records_count": evidence_count,
            "communities_count": 2,
            "anomalies_count": len(anomalies),
            "contradictions_count": len(contradictions),
            "hidden_links_count": len(hidden_links),
            "high_priority_leads_count": len(tailored_leads)
        },
        "key_signals": case_signals,
        "priority_leads": tailored_leads[:6]
    }


@app.get("/api/cases/{case_id}/graph")
def get_case_graph(
    case_id: str = "CASE0001",
    entity_type: Optional[str] = Query(None),
    community_id: Optional[int] = Query(None),
    only_bridges: bool = Query(False),
    search: Optional[str] = Query(None),
    focus_node: Optional[str] = Query(None),
    hops: int = Query(2)
):
    nodes = []
    edges = []
    priorities = priority_engine.compute_all()

    # Pre-calculate active subgraph if focus_node provided
    allowed_nodes = set(graph_instance.nodes_data.keys())
    if focus_node and focus_node in graph_instance.G:
        import networkx as nx
        # Compute k-hop ego graph
        ego_nodes = set([focus_node])
        curr_frontier = set([focus_node])
        for _ in range(hops):
            next_frontier = set()
            for n in curr_frontier:
                next_frontier.update(graph_instance.undirected_G.neighbors(n))
            ego_nodes.update(next_frontier)
            curr_frontier = next_frontier
        allowed_nodes = ego_nodes

    for nid, ndata in graph_instance.nodes_data.items():
        if nid not in allowed_nodes:
            continue

        ntype = ndata.get("type", "entity")
        if entity_type and ntype != entity_type:
            continue

        an_stats = analytics.get_node_analytics(nid)
        p_info = priorities.get(nid, {})

        if only_bridges and not an_stats["is_bridge"]:
            continue

        if community_id is not None and an_stats["community_id"] != community_id:
            continue

        if search:
            s_low = search.lower()
            if s_low not in nid.lower() and s_low not in ndata.get("label", "").lower() and s_low not in ndata.get("name", "").lower():
                continue

        nodes.append({
            "data": {
                "id": nid,
                "label": ndata.get("label", nid),
                "name": ndata.get("name", nid),
                "type": ntype,
                "community": an_stats["community_id"],
                "is_bridge": an_stats["is_bridge"],
                "degree": an_stats["degree"],
                "betweenness": an_stats["betweenness"],
                "pagerank": an_stats["pagerank"],
                "priority": p_info.get("priority", "LOW"),
                "priority_score": p_info.get("priority_score", 0.0),
                "priority_reason": p_info.get("reason", ""),
                "is_alias": ndata.get("is_alias", False),
                "city": ndata.get("city", "")
            }
        })

    valid_node_ids = set(n["data"]["id"] for n in nodes)

    for e in graph_instance.edges_data:
        if e["source"] in valid_node_ids and e["target"] in valid_node_ids:
            edges.append({
                "data": {
                    "id": e["id"],
                    "source": e["source"],
                    "target": e["target"],
                    "type": e["type"],
                    "timestamp": e.get("timestamp"),
                    "source_record_id": e["provenance"]["source_record_id"],
                    "source_type": e["provenance"]["source_type"],
                    "confidence": e["provenance"]["confidence"],
                    "reliability": e["provenance"]["reliability"],
                    "evidence_class": e["provenance"]["evidence_class"],
                    "context": e["provenance"]["context"]
                }
            })

    return {
        "elements": {
            "nodes": nodes,
            "edges": edges
        },
        "stats": {
            "nodes_count": len(nodes),
            "edges_count": len(edges)
        }
    }


@app.get("/api/entities/{entity_id}")
def get_entity_profile(entity_id: str):
    if entity_id not in graph_instance.nodes_data:
        raise HTTPException(status_code=404, detail="Entity not found")

    ndata = graph_instance.nodes_data[entity_id]
    an_stats = analytics.get_node_analytics(entity_id)
    priorities = priority_engine.compute_all()
    p_info = priorities.get(entity_id, {
        "priority": "LOW",
        "priority_score": 0.0,
        "reason": "Not prioritized for this case.",
        "signals": []
    })

    # Connected edges and entities
    connected_edges = [
        e for e in graph_instance.edges_data
        if e["source"] == entity_id or e["target"] == entity_id
    ]

    connected_entity_ids = set()
    for e in connected_edges:
        other = e["target"] if e["source"] == entity_id else e["source"]
        connected_entity_ids.add(other)

    connected_entities = [
        {
            "id": oid,
            "name": graph_instance.nodes_data.get(oid, {}).get("name", oid),
            "type": graph_instance.nodes_data.get(oid, {}).get("type", "unknown"),
            "relationship": [e["type"] for e in connected_edges if e["source"] == oid or e["target"] == oid]
        }
        for oid in connected_entity_ids if oid in graph_instance.nodes_data
    ]

    # Associated evidence records
    cdr_records = [c for c in dataset.cdr if c["caller_person_id"] == entity_id or c["receiver_person_id"] == entity_id]
    txn_records = [
        t for t in dataset.transactions
        if dataset.account_map.get(t["sender_account_id"], {}).get("account_holder_person_id") == entity_id or
           dataset.account_map.get(t["receiver_account_id"], {}).get("account_holder_person_id") == entity_id
    ]
    surv_records = [s for s in dataset.surveillance if s["person_id"] == entity_id]
    fir_records = [f for f in dataset.firs if entity_id in f["report_text"] or ndata.get("name", "") in f["report_text"]]

    # Associated contradictions
    contradictions = [c for c in contradiction_detector.get_all() if c["entity_id"] == entity_id or entity_id in str(c)]

    return {
        "entity_id": entity_id,
        "name": ndata.get("name", entity_id),
        "type": ndata.get("type", "entity"),
        "attributes": ndata,
        "analytics": an_stats,
        "investigation_priority": {
            "level": p_info["priority"],
            "score": p_info["priority_score"],
            "reason": p_info["reason"],
            "signals": p_info["signals"],
            "components": p_info.get("components", {}),
            "label": "INVESTIGATION PRIORITY (NOT GUILT)"
        },
        "connected_entities": connected_entities,
        "connected_edges": connected_edges[:30],
        "evidence_summary": {
            "telecom_calls": len(cdr_records),
            "transactions": len(txn_records),
            "surveillance_sightings": len(surv_records),
            "fir_mentions": len(fir_records)
        },
        "contradictions": contradictions
    }


@app.get("/api/cases/{case_id}/timeline")
def get_timeline(case_id: str = "CASE0001", entity_id: Optional[str] = None):
    events = timeline_engine.get_events(case_id=case_id, entity_id=entity_id)
    case_info = dataset.case_map.get(case_id, {})
    inc_date = case_info.get("incident_date", "2026-08-20")
    return {
        "case_id": case_id,
        "total_events": len(events),
        "incident_date": inc_date,
        "pre_incident_window": f"Pre-incident window for {case_id}",
        "events": events
    }


@app.get("/api/cases/{case_id}/anomalies")
def get_anomalies(case_id: str = "CASE0001"):
    return anomaly_detector.detect_for_case(case_id)


@app.get("/api/cases/{case_id}/contradictions")
def get_contradictions(case_id: str = "CASE0001"):
    return contradiction_detector.get_for_case(case_id)


@app.get("/api/cases/{case_id}/hidden-links")
def get_hidden_links(case_id: str = "CASE0001"):
    return hidden_link_engine.discover_all()


@app.get("/api/cases/{case_id}/priority-leads")
def get_priority_leads(case_id: str = "CASE0001"):
    priorities = priority_engine.compute_all()
    case_pids = set()
    for f in dataset.firs:
        if f.get("case_id") == case_id:
            for p in dataset.persons:
                if p["name"] in f.get("report_text", "") or p["person_id"] in f.get("report_text", ""):
                    case_pids.add(p["person_id"])
    for h in dataset.criminal_history:
        if h.get("case_id") == case_id:
            case_pids.add(h.get("person_id"))

    if case_pids:
        leads = [v for v in priorities.values() if v["person_id"] in case_pids]
        leads.sort(key=lambda x: x["priority_score"], reverse=True)
        if not leads:
            leads = list(priorities.values())
            leads.sort(key=lambda x: x["priority_score"], reverse=True)
    else:
        leads = list(priorities.values())
        leads.sort(key=lambda x: x["priority_score"], reverse=True)
    return leads


@app.get("/api/cases/{case_id}/report")
def get_report(case_id: str = "CASE0001"):
    return report_generator.generate_brief(case_id=case_id)


web_dir = os.path.join(BASE_DIR, "apps", "web")
if os.path.exists(os.path.join(web_dir, "vendor")):
    app.mount("/vendor", StaticFiles(directory=os.path.join(web_dir, "vendor")), name="vendor")


@app.get("/")
def serve_root():
    index_html = os.path.join(web_dir, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)
    return {"message": "CrimeLens Intelligence Platform API online. Open frontend UI."}


@app.get("/styles.css")
def serve_css():
    return FileResponse(os.path.join(web_dir, "styles.css"), media_type="text/css")


@app.get("/app.js")
def serve_js():
    return FileResponse(os.path.join(web_dir, "app.js"), media_type="application/javascript")

