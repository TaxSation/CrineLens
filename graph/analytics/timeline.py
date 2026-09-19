"""
CrimeLens Temporal Timeline Engine
Assembles chronological events across CDR, financial records, surveillance,
FIR reports, and social feeds, enabling before/incident/after comparison.
"""
from typing import List, Dict, Any, Optional
from graph.schema.loader import dataset


class TimelineEngine:
    def get_events(
        self,
        case_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        entity_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        events = []

        # 1. CDR events
        for r in dataset.cdr:
            p_a = dataset.person_map.get(r["caller_person_id"], {}).get("name", r["caller_person_id"])
            p_b = dataset.person_map.get(r["receiver_person_id"], {}).get("name", r["receiver_person_id"])
            is_spike = "PAT02" in r.get("tag", "")
            is_cross = "PAT06" in r.get("tag", "")
            is_bridge = "PAT01" in r.get("tag", "")
            rec_id = r.get("cdr_id") or r.get("id", "CDR")

            tag_labels = []
            if is_spike:
                tag_labels.append("48h Pre-Incident Spike")
            if is_cross:
                tag_labels.append("New Cross-Community Edge")
            if is_bridge:
                tag_labels.append("Bridge Communication")

            events.append({
                "id": rec_id,
                "timestamp": r["timestamp"],
                "type": "telecom",
                "subtype": r["call_type"],
                "title": f"{r['call_type'].upper()}: {p_a} → {p_b}",
                "description": f"Call duration: {r['duration_seconds']}s via cell {r['cell_location_id']}",
                "entities": [r["caller_person_id"], r["receiver_person_id"]],
                "entity_names": [p_a, p_b],
                "source_record_id": rec_id,
                "source_type": "CDR",
                "tags": tag_labels,
                "is_critical": is_spike or is_cross or is_bridge
            })

        # 2. Financial transactions
        for t in dataset.transactions:
            sender_person = dataset.account_map.get(t["sender_account_id"], {}).get("account_holder_person_id")
            rec_person = dataset.account_map.get(t["receiver_account_id"], {}).get("account_holder_person_id")
            s_name = dataset.person_map.get(sender_person, {}).get("name", t["sender_account_id"])
            r_name = dataset.person_map.get(rec_person, {}).get("name", t["receiver_account_id"])
            t_rec_id = t.get("transaction_id") or t.get("id", "TXN")

            is_chain = "PAT03" in t.get("tag", "")
            is_layering = "PAT04" in t.get("tag", "")
            is_mule = "PAT05" in t.get("tag", "")

            tag_labels = []
            if is_chain:
                tag_labels.append("Nocturnal Transfer")
            if is_layering:
                tag_labels.append("Layering Chain")
            if is_mule:
                tag_labels.append("Rapid Split Structuring")

            events.append({
                "id": t_rec_id,
                "timestamp": t["timestamp"],
                "type": "financial",
                "subtype": t.get("transaction_type", "transfer"),
                "title": f"Transfer: ₹{float(t['amount']):,.0f} ({s_name} → {r_name})",
                "description": f"Channel: {t.get('transaction_type', 'transfer')} | {t['sender_account_id']} → {t['receiver_account_id']}",
                "entities": [
                    t["sender_account_id"],
                    t["receiver_account_id"],
                    sender_person,
                    rec_person
                ],
                "entity_names": [s_name, r_name],
                "source_record_id": t_rec_id,
                "source_type": "Bank Transaction",
                "tags": tag_labels,
                "is_critical": is_chain or is_layering or is_mule
            })

        # 3. Surveillance events
        for s in dataset.surveillance:
            v_reg = dataset.vehicle_map.get(s["vehicle_id"], {}).get("registration_no", s["vehicle_id"]) if s.get("vehicle_id") else "Vehicle"
            loc_name = dataset.location_map.get(s["location_id"], {}).get("location_name", s["location_id"])
            is_alibi = "PAT07" in s.get("tag", "")
            surv_rec_id = s.get("surveillance_id") or s.get("id", "SURV")
            conf = float(s.get("detection_confidence", 0.85))

            tag_labels = []
            if is_alibi:
                tag_labels.append("Alibi Verification")

            events.append({
                "id": surv_rec_id,
                "timestamp": s["timestamp"],
                "type": "surveillance",
                "subtype": "camera_detection",
                "title": f"Surveillance: {v_reg} at {loc_name}",
                "description": f"Camera {s.get('camera_id', 'CAM')} [Confidence: {conf:.2f}] - Vehicle: {v_reg}",
                "entities": [e for e in [s.get("vehicle_id"), s.get("person_id"), s.get("location_id")] if e],
                "entity_names": [v_reg, loc_name],
                "source_record_id": surv_rec_id,
                "source_type": "Surveillance CAM",
                "tags": tag_labels,
                "is_critical": is_alibi or conf > 0.92
            })

        # 4. Social media posts
        for sp in dataset.social:
            p_name = dataset.person_map.get(sp["person_id"], {}).get("name", sp["person_id"])
            loc_name = dataset.location_map.get(sp["location_id"], {}).get("location_name", sp["location_id"])
            sp_rec_id = sp.get("post_id") or sp.get("id", "POST")

            events.append({
                "id": sp_rec_id,
                "timestamp": sp["timestamp"],
                "type": "social_intelligence",
                "subtype": "post",
                "title": f"Social Intel: {p_name} ({loc_name})",
                "description": f"\"{sp['text']}\" [Platform: {sp['platform']} | Sentiment: {sp['sentiment']}]",
                "entities": [sp["person_id"], sp["location_id"]],
                "entity_names": [p_name, loc_name],
                "source_record_id": sp_rec_id,
                "source_type": "OSINT / Social",
                "tags": [sp.get("tag")] if sp.get("tag") else [],
                "is_critical": bool(sp.get("tag"))
            })

        # 5. Incident Marker(s)
        active_target_case = case_id if (case_id and case_id != "ALL") else "CASE0001"
        case_info = dataset.case_map.get(active_target_case, {})
        loc_id = case_info.get("primary_location_id", "LOC0002")
        loc_name = dataset.location_map.get(loc_id, {}).get("location_name", loc_id)
        c_type = case_info.get("case_type", "incident").replace("_", " ").title()
        inc_date = case_info.get("incident_date", "2026-08-20")

        case_firs = [f for f in dataset.firs if f.get("case_id") == active_target_case]
        fir_text = case_firs[0].get("report_text", "") if case_firs else f"Official police record for {active_target_case} ({c_type}) at {loc_name}."
        fir_id = case_firs[0].get("fir_id", "FIR00001") if case_firs else "FIR"

        events.append({
            "id": f"INCIDENT-{active_target_case}",
            "timestamp": f"{inc_date} 18:00:00",
            "type": "incident",
            "subtype": "crime_event",
            "title": f"{active_target_case}: {c_type} at {loc_name}",
            "description": fir_text,
            "entities": [active_target_case, loc_id],
            "entity_names": [c_type, loc_name],
            "source_record_id": fir_id,
            "source_type": "Police FIR",
            "tags": ["PRIMARY INCIDENT", c_type.upper()],
            "is_critical": True
        })

        # Sort chronologically
        events.sort(key=lambda x: x["timestamp"])

        # Filter by active case if requested
        if case_id and case_id != "ALL":
            case_ents = set([case_id])
            for f in case_firs:
                case_ents.add(f.get("fir_id"))
                for p in dataset.persons:
                    if p["name"] in f.get("report_text", "") or p["person_id"] in f.get("report_text", ""):
                        case_ents.add(p["person_id"])
                for v in dataset.vehicles:
                    if v.get("registration_no", "") in f.get("report_text", "") or v["vehicle_id"] in f.get("report_text", ""):
                        case_ents.add(v["vehicle_id"])

            for h in dataset.criminal_history:
                if h.get("case_id") == case_id:
                    case_ents.add(h.get("person_id"))

            # Map related accounts and phones of case persons
            person_ids = set([e for e in case_ents if isinstance(e, str) and e.startswith("P")])
            for acc_id, acc in dataset.account_map.items():
                if acc.get("account_holder_person_id") in person_ids:
                    case_ents.add(acc_id)
            for ph in dataset.phones:
                if ph.get("owner_person_id") in person_ids:
                    case_ents.add(ph.get("phone_id"))

            case_scoped = [
                e for e in events
                if any(ent in case_ents for ent in e.get("entities", []))
                or case_id in e.get("entities", [])
                or case_id in e.get("title", "")
            ]
            if case_scoped:
                events = case_scoped

        # Filter by specific entity if provided
        if entity_id:
            events = [e for e in events if entity_id in e["entities"]]

        return events


timeline_engine = TimelineEngine()
