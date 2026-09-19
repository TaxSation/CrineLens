"""
CrimeLens Automated Smoke & Pipeline Test Suite
Tests dataset ingestion, graph generation, centralities, priority scoring,
and API response contracts.
"""
from graph.schema.loader import dataset
from graph.schema.graph_builder import graph_instance
from graph.analytics.analyzer import analytics
from ml.scoring.priority_engine import priority_engine
from ml.anomaly.detector import anomaly_detector
from ml.entity_resolution.hidden_links import hidden_link_engine
from graph.analytics.contradictions import contradiction_detector
from graph.analytics.timeline import timeline_engine


def test_dataset_loaded():
    assert len(dataset.persons) == 20
    assert len(dataset.cdr) == 198
    assert len(dataset.transactions) == 51
    assert len(dataset.surveillance) == 34
    assert len(dataset.cases) == 12


def test_graph_construction():
    assert len(graph_instance.nodes_data) == 96
    assert len(graph_instance.edges_data) >= 364
    assert "P0001" in graph_instance.nodes_data
    assert "P0005" in graph_instance.nodes_data


def test_bridge_node_detection():
    # PAT01: P0005 links Network A and Network B
    stats = analytics.get_node_analytics("P0005")
    assert stats["is_bridge"] is True
    assert stats["betweenness"] > 0.05


def test_priority_engine_output():
    priorities = priority_engine.compute_all()
    assert len(priorities) == 20
    high_leads = [v for v in priorities.values() if v["priority"] == "HIGH"]
    assert len(high_leads) >= 4
    # Anil Trivedi should be marked HIGH due to case 0001 direct involvement
    assert priorities["P0004"]["priority"] == "HIGH"


def test_anomaly_detector():
    anomalies = anomaly_detector.detect_all()
    assert len(anomalies) == 4
    types = [a["type"] for a in anomalies]
    assert "Nocturnal High-Value Transfer" in types
    assert "Pre-Incident Communication Spike" in types


def test_contradiction_preservation():
    conflicts = contradiction_detector.get_all()
    assert len(conflicts) == 2
    for c in conflicts:
        assert c["status"] == "UNRESOLVED CONFLICT"
        assert "claim_a" in c and "claim_b" in c


def test_timeline_events():
    events = timeline_engine.get_events()
    assert len(events) >= 300
    pre_incident = [e for e in events if e["timestamp"].startswith("2026-08-18") or e["timestamp"].startswith("2026-08-19")]
    assert len(pre_incident) >= 35


def test_hidden_link_discovery():
    links = hidden_link_engine.discover_all()
    assert len(links) == 1
    assert links[0]["source_id"] == "P0007"
    assert links[0]["target_id"] == "P0012"
