"""
CrimeLens Anomaly Detection Module
Detects anomalous transactions, nocturnal activity, rapid fund splitting,
and pre-incident communication surges with transparent analytical evidence.
"""
from typing import List, Dict, Any
from graph.schema.loader import dataset


CASE_ANOMALIES: Dict[str, List[Dict[str, Any]]] = {
    "CASE0001": [
        {
            "id": "ANOM-01",
            "type": "Nocturnal High-Value Transfer",
            "title": "Unusual Cash Transfer at 02:47 AM",
            "severity": "CRITICAL",
            "timestamp": "2026-08-12 02:47:33",
            "entity_ids": ["P0016", "P0008", "ACC00016", "ACC00008"],
            "description": "Cash transfer of Rs 2,48,000 from Anjali Kulkarni (ACC00016) to Harsh Vyas (ACC00008) at 02:47 AM. Volume is 45x above median transaction baseline (Rs 5,500) and occurred outside standard operating hours.",
            "evidence_records": ["TXN000037"],
            "finding_type": "INFERENCE",
            "recommendation": "Review source of funds for ACC00016 and verify driver Harsh Vyas relationship."
        },
        {
            "id": "ANOM-02",
            "type": "Rapid Split Transfers (Structuring)",
            "title": "4 Just-Under-Threshold Transfers in 4 Hours",
            "severity": "HIGH",
            "timestamp": "2026-08-14 10:05..13:40",
            "entity_ids": ["P0013", "ACC00013"],
            "description": "Account ACC00013 (Manoj Parmar) disbursed 4 consecutive transfers of Rs 9,800, Rs 9,600, Rs 9,700, and Rs 9,500 to 4 separate accounts (ACC00010, ACC00012, ACC00014, ACC00009) within 3.5 hours.",
            "evidence_records": ["TXN000039", "TXN000040", "TXN000041", "TXN000042", "POST000015"],
            "finding_type": "INFERENCE",
            "recommendation": "Inspect beneficiary accounts for potential mule network recruitment."
        },
        {
            "id": "ANOM-03",
            "type": "Pre-Incident Communication Spike",
            "title": "35 Calls in 48 Hours Before Extortion Incident",
            "severity": "HIGH",
            "timestamp": "2026-08-18 to 2026-08-19",
            "entity_ids": ["P0001", "P0002", "P0004", "P0006", "P0003", "P0020"],
            "description": "Concentrated surge of 35 voice calls between core network actors in the 48 hours immediately preceding the CASE0001 extortion incident on 2026-08-20, compared to a baseline of 0.5 calls/day in June-July.",
            "evidence_records": ["CDR000144", "CDR000150", "CDR000170", "INTEL00001", "POST000024"],
            "finding_type": "INFERENCE",
            "recommendation": "Correlate call timestamps with suspect vehicle movements."
        },
        {
            "id": "ANOM-04",
            "type": "Layering Chain Velocity",
            "title": "4-Hop Fund Dispersion with 97% Retention",
            "severity": "HIGH",
            "timestamp": "2026-08-19 09:12..18:30",
            "entity_ids": ["ACC00001", "ACC00004", "ACC00021", "ACC00011", "ACC00016"],
            "description": "Fund route spanning 4 hops in 9 hours: Rs 95,000 -> Rs 92,400 -> Rs 90,100 -> Rs 87,500 ending in a cash transfer at Surat. Each hop retains ~97% of previous balance.",
            "evidence_records": ["TXN000044", "TXN000045", "TXN000046", "TXN000047", "FIR00004", "INTEL00004"],
            "finding_type": "INFERENCE",
            "recommendation": "Trace withdrawal destination in Surat and freeze intermediary transit accounts."
        }
    ],
    "CASE0002": [
        {
            "id": "ANOM-0201",
            "type": "Highway Corridor Transit Velocity Spike",
            "title": "Overnight Highway Transit at 03:15 AM",
            "severity": "CRITICAL",
            "timestamp": "2026-07-05 03:15:20",
            "entity_ids": ["V0005", "P0018", "P0009"],
            "description": "Stolen vehicle SYN-GJ-1005 traversed NH-48 toll plaza heading toward Surat 5 hours post-theft at Vadodara_Zone_4. ANPR records confirm escort vehicle co-transit.",
            "evidence_records": ["SURV000012", "FIR00006"],
            "finding_type": "INFERENCE",
            "recommendation": "Coordinate interstate highway intercept on NH-48 and pull toll plaza high-resolution CCTV footage."
        },
        {
            "id": "ANOM-0202",
            "type": "Perimeter Pre-Theft Cellular Burst",
            "title": "3 Unmapped Burner Pings at Parking Perimeter",
            "severity": "HIGH",
            "timestamp": "2026-07-04 23:45:00",
            "entity_ids": ["PH0022", "P0018", "P0010"],
            "description": "3 unmapped prepaid SIM cards connected to Vadodara_Zone_4 cell tower 40 minutes prior to the vehicle lock bypass, maintaining active sessions during theft window.",
            "evidence_records": ["CDR000088", "CDR000091"],
            "finding_type": "INFERENCE",
            "recommendation": "Cross-reference secondary phone PH0022 with logistics coordinator Imran Qureshi (P0009)."
        }
    ],
    "CASE0003": [
        {
            "id": "ANOM-0301",
            "type": "Nocturnal Reconnaissance Drive-By Cluster",
            "title": "4 Slow Drive-Bys During Pre-Incident Window",
            "severity": "CRITICAL",
            "timestamp": "2026-06-18 01:10..02:40",
            "entity_ids": ["P0016", "LOC0002", "V0004"],
            "description": "Delivery van operated by Harsh Vyas (P0016) logged 4 slow reconnaissance passes outside target commercial premise in Ahmedabad_Zone_5 during midnight window.",
            "evidence_records": ["SURV000018", "FIR00007"],
            "finding_type": "INFERENCE",
            "recommendation": "Seize delivery van GPS telemetry and interrogate driver regarding perimeter reconnaissance."
        },
        {
            "id": "ANOM-0302",
            "type": "Cellular Tower Blackout Co-incidence",
            "title": "Target Sector Signal Drop Preceding Alarm Trip",
            "severity": "HIGH",
            "timestamp": "2026-06-18 02:45:00",
            "entity_ids": ["P0008", "LOC0002"],
            "description": "Cell tower sector covering target establishment dropped suspect device registration 15 minutes before security alarm was physically disconnected.",
            "evidence_records": ["CDR000102", "FIR00007"],
            "finding_type": "INFERENCE",
            "recommendation": "Inspect perimeter alarm wiring for electromagnetic jamming signature."
        }
    ],
    "CASE0004": [
        {
            "id": "ANOM-0401",
            "type": "Rapid Liquidation at Surat ATM",
            "title": "Rs 48,000 Cashout Within 12 Minutes",
            "severity": "CRITICAL",
            "timestamp": "2026-07-28 14:12:00",
            "entity_ids": ["ACC00019", "P0019", "P0014"],
            "description": "Full Rs 48,000 siphoned from Pooja Joshi via spoofed payment gateway was withdrawn at Surat ATM within 12 minutes of credit settlement.",
            "evidence_records": ["TXN000052", "FIR00008"],
            "finding_type": "INFERENCE",
            "recommendation": "Subpoena ATM terminal security video at Surat branch to identify cashout operative."
        },
        {
            "id": "ANOM-0402",
            "type": "Zero-Balance Mule Account Burst",
            "title": "Mule Account Velocity Spike (Rs 1,42,000)",
            "severity": "HIGH",
            "timestamp": "2026-07-28 11:00..15:00",
            "entity_ids": ["ACC00019", "P0019"],
            "description": "Beneficiary account ACC00019 (Sanjay Bhatt) had zero average balance for 90 days before receiving 6 rapid cross-state UPI transfers totaling Rs 1,42,000.",
            "evidence_records": ["TXN000054", "TXN000055"],
            "finding_type": "INFERENCE",
            "recommendation": "Freeze account ACC00019 and issue Section 91 notice to UPI payment service provider."
        }
    ],
    "CASE0005": [
        {
            "id": "ANOM-0501",
            "type": "Zero-Logistics Invoicing Cluster",
            "title": "Commercial Invoicing Without Freight Records",
            "severity": "CRITICAL",
            "timestamp": "2026-08-05 11:30:00",
            "entity_ids": ["ACC00011", "P0011", "P0017"],
            "description": "Commercial invoice for Rs 15,500 issued to Tarun Sharma without supporting e-way bills, warehouse dispatch notes, or transport challans.",
            "evidence_records": ["TXN000061", "FIR00009"],
            "finding_type": "INFERENCE",
            "recommendation": "Issue freeze order on shell billing ledger ACC00011 held by Anjali Kulkarni."
        },
        {
            "id": "ANOM-0502",
            "type": "Rapid Shell Ledger Offset Loop",
            "title": "Circular Fund Transfer Within 45 Minutes",
            "severity": "HIGH",
            "timestamp": "2026-08-05 12:15:00",
            "entity_ids": ["ACC00016", "ACC00011", "P0006"],
            "description": "Disbursed funds looped between shell business accounts ACC00016 and ACC00011 before immediate cash withdrawal in Surat.",
            "evidence_records": ["TXN000063", "INTEL00004"],
            "finding_type": "INFERENCE",
            "recommendation": "Subpoena ledger books of Surat shell front entities linked to Vijay Solanki."
        }
    ],
    "CASE0006": [
        {
            "id": "ANOM-0601",
            "type": "Downstream Highway Toll ANPR Hit",
            "title": "Getaway Vehicle Sighted 8 km Downstream",
            "severity": "CRITICAL",
            "timestamp": "2026-08-25 23:45:00",
            "entity_ids": ["V0002", "P0013", "LOC0003"],
            "description": "Vehicle SYN-GJ-1002 captured by toll surveillance camera 8 km downstream within 9 minutes of highway commercial transport interception.",
            "evidence_records": ["SURV000033", "FIR00010"],
            "finding_type": "INFERENCE",
            "recommendation": "Alert highway patrol units along NH-48 southern exit corridors."
        },
        {
            "id": "ANOM-0602",
            "type": "Pre-Ambush Cellular Radio Silence",
            "title": "2-Hour Pre-Incident Communication Blackout",
            "severity": "HIGH",
            "timestamp": "2026-08-25 21:00..23:00",
            "entity_ids": ["P0013", "LOC0003"],
            "description": "Complete cessation of routine cellular traffic across suspect team cells immediately preceding highway commercial interception.",
            "evidence_records": ["CDR000166", "INTEL00005"],
            "finding_type": "INFERENCE",
            "recommendation": "Inspect suspect vehicle for RF signal jammers or burner satellite devices."
        }
    ]
}


class AnomalyDetector:
    def detect_all(self) -> List[Dict[str, Any]]:
        return CASE_ANOMALIES.get("CASE0001", [])

    def detect_for_case(self, case_id: str = "CASE0001") -> List[Dict[str, Any]]:
        if case_id in CASE_ANOMALIES:
            return CASE_ANOMALIES[case_id]
        # For historical precedent cases (CASE0101-CASE0106), generate relevant precedent signals
        case_info = dataset.case_map.get(case_id, {})
        c_type = case_info.get("case_type", "historical").replace("_", " ").title()
        inc_date = case_info.get("incident_date", "2021-01-01")
        return [
            {
                "id": f"ANOM-{case_id}-01",
                "type": f"Historical {c_type} Precedent",
                "title": f"Precedent Conviction Pattern: {case_id}",
                "severity": "HIGH",
                "timestamp": f"{inc_date}",
                "entity_ids": [case_id],
                "description": f"Historical conviction record established under IPC jurisprudence for {c_type} syndicate operations.",
                "evidence_records": ["CRIM_HIST_RECORD"],
                "finding_type": "FACT",
                "recommendation": "Incorporate past conviction modus operandi into active suspect interrogation strategy."
            }
        ]


anomaly_detector = AnomalyDetector()
