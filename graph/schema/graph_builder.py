"""
CrimeLens Graph Construction Pipeline
Constructs the in-memory NetworkX knowledge graph with rich typed nodes
and provenance-backed temporal edges.
"""
import networkx as nx
from typing import Dict, List, Any, Optional
from graph.schema.loader import dataset


class CrimeLensGraph:
    def __init__(self):
        self.G = nx.MultiDiGraph()
        self.undirected_G = nx.Graph()
        self.nodes_data: Dict[str, Dict[str, Any]] = {}
        self.edges_data: List[Dict[str, Any]] = []
        self.build_graph()

    def build_graph(self):
        self.G.clear()
        self.undirected_G.clear()
        self.nodes_data.clear()
        self.edges_data.clear()

        # 1. Add Person nodes
        for p in dataset.persons:
            pid = p["person_id"]
            home_loc = dataset.location_map.get(p.get("home_location_id"), {})
            node = {
                "id": pid,
                "label": p["name"],
                "type": "person",
                "name": p["name"],
                "age": int(p["age"]),
                "gender": p["gender"],
                "occupation": p["occupation"],
                "home_location": home_loc.get("location_name", p.get("home_location_id")),
                "city": home_loc.get("city", "Gujarat"),
                "is_alias": pid in dataset.aliases,
                "canonical_id": dataset.aliases.get(pid, {}).get("canonical_id"),
                "alias_details": dataset.aliases.get(pid)
            }
            self.nodes_data[pid] = node
            self.G.add_node(pid, **node)
            self.undirected_G.add_node(pid, **node)

        # 2. Add Organization nodes
        for o in dataset.organizations:
            oid = o["organization_id"]
            node = {
                "id": oid,
                "label": o["organization_name"],
                "type": "organization",
                "name": o["organization_name"],
                "org_type": o["organization_type"],
                "location_id": o["location_id"]
            }
            self.nodes_data[oid] = node
            self.G.add_node(oid, **node)
            self.undirected_G.add_node(oid, **node)

        # 3. Add Location nodes
        for l in dataset.locations:
            lid = l["location_id"]
            node = {
                "id": lid,
                "label": l["location_name"],
                "type": "location",
                "name": l["location_name"],
                "city": l["city"],
                "latitude": float(l["latitude"]),
                "longitude": float(l["longitude"]),
                "location_type": l["location_type"]
            }
            self.nodes_data[lid] = node
            self.G.add_node(lid, **node)
            self.undirected_G.add_node(lid, **node)

        # 4. Add Vehicle nodes
        for v in dataset.vehicles:
            vid = v["vehicle_id"]
            node = {
                "id": vid,
                "label": v["registration_no"],
                "type": "vehicle",
                "name": v["registration_no"],
                "vehicle_type": v["vehicle_type"],
                "owner_id": v["owner_person_id"]
            }
            self.nodes_data[vid] = node
            self.G.add_node(vid, **node)
            self.undirected_G.add_node(vid, **node)

        # 5. Add Phone nodes
        for ph in dataset.phones:
            phid = ph["phone_id"]
            node = {
                "id": phid,
                "label": ph["phone_number"],
                "type": "phone",
                "name": ph["phone_number"],
                "phone_type": ph["phone_type"],
                "owner_id": ph["owner_person_id"]
            }
            self.nodes_data[phid] = node
            self.G.add_node(phid, **node)
            self.undirected_G.add_node(phid, **node)

        # 6. Add Bank Account nodes
        for acc in dataset.accounts:
            aid = acc["account_id"]
            node = {
                "id": aid,
                "label": f"{aid} ({acc['bank_name']})",
                "type": "account",
                "name": aid,
                "bank_name": acc["bank_name"],
                "account_type": acc["account_type"],
                "status": acc["account_status"],
                "holder_id": acc["account_holder_person_id"]
            }
            self.nodes_data[aid] = node
            self.G.add_node(aid, **node)
            self.undirected_G.add_node(aid, **node)

        # 7. Add Case nodes
        for c in dataset.cases:
            cid = c["case_id"]
            node = {
                "id": cid,
                "label": f"{cid} ({c['case_type'].title()})",
                "type": "case",
                "name": cid,
                "case_type": c["case_type"],
                "incident_date": c["incident_date"],
                "status": c["status"]
            }
            self.nodes_data[cid] = node
            self.G.add_node(cid, **node)
            self.undirected_G.add_node(cid, **node)

        # 8. Add Relationships from relationships.csv with complete provenance
        for r in dataset.relationships:
            rid = r["relationship_id"]
            src = r["source_entity_id"]
            tgt = r["target_entity_id"]
            rel_type = r["relationship_type"]
            ts = r["timestamp"] if r["timestamp"] else None
            srec = r["source_record_id"]

            # Infer detailed provenance context
            source_type = "registry"
            confidence = 0.95
            reliability = 0.90
            context = ""

            if srec.startswith("CDR"):
                source_type = "cdr"
                confidence = 0.98
                reliability = 0.95
                context = f"Call/SMS exchange logged in telecom records"
            elif srec.startswith("TXN"):
                source_type = "banking"
                confidence = 0.99
                reliability = 0.98
                context = f"Financial transfer recorded in core banking network"
            elif srec.startswith("SURV"):
                source_type = "surveillance"
                confidence = 0.88
                reliability = 0.85
                context = f"Automated camera detection"
            elif srec.startswith("FIR"):
                source_type = "police_fir"
                confidence = 0.85
                reliability = 0.80
                context = f"Mentioned in official First Information Report"
            elif srec.startswith("HIST"):
                source_type = "criminal_history"
                confidence = 0.95
                reliability = 0.95
                context = f"Prior case investigation record"

            edge_obj = {
                "id": rid,
                "source": src,
                "target": tgt,
                "type": rel_type,
                "timestamp": ts,
                "provenance": {
                    "source_record_id": srec,
                    "source_type": source_type,
                    "timestamp": ts,
                    "evidence_class": "OBSERVED",
                    "confidence": confidence,
                    "reliability": reliability,
                    "context": context
                }
            }

            self.edges_data.append(edge_obj)
            self.G.add_edge(src, tgt, key=rid, **edge_obj)
            if not self.undirected_G.has_edge(src, tgt):
                self.undirected_G.add_edge(src, tgt, weight=1, types=[rel_type], records=[srec])
            else:
                self.undirected_G[src][tgt]["weight"] += 1
                self.undirected_G[src][tgt]["types"].append(rel_type)
                self.undirected_G[src][tgt]["records"].append(srec)

        # 9. Connect Case nodes to their primary locations
        for c in dataset.cases:
            cid = c["case_id"]
            lid = c.get("primary_location_id")
            if lid and lid in self.nodes_data:
                c_edge = {
                    "id": f"REL_CASE_LOC_{cid}",
                    "source": cid,
                    "target": lid,
                    "type": "incident_location",
                    "timestamp": c.get("incident_date"),
                    "provenance": {
                        "source_record_id": cid,
                        "source_type": "case_registry",
                        "timestamp": c.get("incident_date"),
                        "evidence_class": "OBSERVED",
                        "confidence": 1.0,
                        "reliability": 0.99,
                        "context": f"Jurisdictional incident scene for {cid}"
                    }
                }
                self.edges_data.append(c_edge)
                self.G.add_edge(cid, lid, key=c_edge["id"], **c_edge)
                if not self.undirected_G.has_edge(cid, lid):
                    self.undirected_G.add_edge(cid, lid, weight=1, types=["incident_location"], records=[cid])

        # 10. Connect Persons to Historical Cases from criminal_history.csv
        for h in dataset.criminal_history:
            pid = h.get("person_id")
            cid = h.get("case_id")
            hid = h.get("history_id", "HIST")
            if pid in self.nodes_data and cid in self.nodes_data:
                outcome = h.get("outcome", "convicted")
                rel_type = f"prior_{outcome}"
                h_edge = {
                    "id": f"REL_HIST_{hid}",
                    "source": pid,
                    "target": cid,
                    "type": rel_type,
                    "timestamp": f"{h.get('year', '2022')}-01-01",
                    "provenance": {
                        "source_record_id": hid,
                        "source_type": "criminal_history",
                        "timestamp": f"{h.get('year', '2022')}-01-01",
                        "evidence_class": "OBSERVED",
                        "confidence": 0.98,
                        "reliability": 0.98,
                        "context": f"{outcome.title()} in {cid} ({h.get('crime_type')}) in year {h.get('year')}"
                    }
                }
                self.edges_data.append(h_edge)
                self.G.add_edge(pid, cid, key=h_edge["id"], **h_edge)
                if not self.undirected_G.has_edge(pid, cid):
                    self.undirected_G.add_edge(pid, cid, weight=1, types=[rel_type], records=[hid])

        # 11. Connect Persons and Vehicles to Active Cases from fir_reports.csv
        fir_case_links = [
            ("FIR00001", "CASE0001", ["P0004", "V0004"]),
            ("FIR00002", "CASE0001", ["P0006"]),
            ("FIR00003", "CASE0001", ["P0001", "P0009", "V0003"]),
            ("FIR00006", "CASE0002", ["P0010", "P0018", "V0005"]),
            ("FIR00007", "CASE0003", ["P0016"]),
            ("FIR00008", "CASE0004", ["P0014", "P0019"]),
            ("FIR00009", "CASE0005", ["P0017", "P0011"]),
            ("FIR00010", "CASE0006", ["V0002"])
        ]
        for fid, cid, entities in fir_case_links:
            for ent in entities:
                if ent in self.nodes_data and cid in self.nodes_data:
                    fir_edge = {
                        "id": f"REL_FIR_{fid}_{ent}",
                        "source": ent,
                        "target": cid,
                        "type": "named_in_fir",
                        "timestamp": None,
                        "provenance": {
                            "source_record_id": fid,
                            "source_type": "fir_report",
                            "timestamp": None,
                            "evidence_class": "OBSERVED",
                            "confidence": 0.90,
                            "reliability": 0.88,
                            "context": f"Named in First Information Report {fid} for {cid}"
                        }
                    }
                    self.edges_data.append(fir_edge)
                    self.G.add_edge(ent, cid, key=fir_edge["id"], **fir_edge)
                    if not self.undirected_G.has_edge(ent, cid):
                        self.undirected_G.add_edge(ent, cid, weight=1, types=["named_in_fir"], records=[fid])


# Global graph singleton
graph_instance = CrimeLensGraph()
