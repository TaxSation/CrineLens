"""
Standalone Smoke Test Runner for CrimeLens
Runs all validation checks without external test runner dependencies.
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from tests.test_pipeline import (
    test_dataset_loaded,
    test_graph_construction,
    test_bridge_node_detection,
    test_priority_engine_output,
    test_anomaly_detector,
    test_contradiction_preservation,
    test_timeline_events,
    test_hidden_link_discovery
)

TESTS = [
    ("Dataset Loading & Validation", test_dataset_loaded),
    ("Graph Construction & Provenance", test_graph_construction),
    ("Bridge Node & Centrality Detection", test_bridge_node_detection),
    ("Explainable Priority Engine", test_priority_engine_output),
    ("Anomaly Detection (Spikes & Night Txns)", test_anomaly_detector),
    ("Unresolved Contradiction Preservation", test_contradiction_preservation),
    ("Timeline Event Reconstruction", test_timeline_events),
    ("Hidden Link Discovery", test_hidden_link_discovery)
]

if __name__ == "__main__":
    print("==================================================")
    print(" Running CrimeLens Smoke & Verification Tests")
    print("==================================================")
    passed = 0
    for name, test_fn in TESTS:
        try:
            test_fn()
            print(f" [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f" [FAIL] {name}: {e}")

    print("--------------------------------------------------")
    print(f" Results: {passed}/{len(TESTS)} tests passed.")
    if passed == len(TESTS):
        print(" ALL VERIFICATION CHECKS SUCCESSFUL!")
    else:
        sys.exit(1)
