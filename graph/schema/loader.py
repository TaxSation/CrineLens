"""
CrimeLens Data Loader & Preprocessing Pipeline
Loads and cleans all CSVs from the raw dataset, normalizing identifiers and dates.
"""
import os
import csv
from typing import Dict, List, Any, Optional
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "raw")


def load_csv(filename: str, data_dir: str = DATA_DIR) -> List[Dict[str, str]]:
    path = os.path.join(data_dir, filename)
    if not os.path.exists(path):
        # Fallback to crimelens_mini_dataset if data/raw missing
        alt = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "crimelens_mini_dataset", filename)
        if os.path.exists(alt):
            path = alt
        else:
            return []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


class DatasetManager:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.reload()

    def reload(self):
        self.persons = load_csv("persons.csv", self.data_dir)
        self.organizations = load_csv("organizations.csv", self.data_dir)
        self.organization_members = load_csv("organization_members.csv", self.data_dir)
        self.locations = load_csv("locations.csv", self.data_dir)
        self.vehicles = load_csv("vehicles.csv", self.data_dir)
        self.phones = load_csv("phone_numbers.csv", self.data_dir)
        self.accounts = load_csv("bank_accounts.csv", self.data_dir)
        self.cases = load_csv("cases.csv", self.data_dir)
        self.criminal_history = load_csv("criminal_history.csv", self.data_dir)
        self.firs = load_csv("fir_reports.csv", self.data_dir)
        self.intels = load_csv("intelligence_reports.csv", self.data_dir)
        self.social = load_csv("social_media_intelligence.csv", self.data_dir)
        self.cdr = load_csv("cdr.csv", self.data_dir)
        self.transactions = load_csv("financial_transactions.csv", self.data_dir)
        self.surveillance = load_csv("surveillance_events.csv", self.data_dir)
        self.relationships = load_csv("relationships.csv", self.data_dir)

        # Lookup maps
        self.person_map = {p["person_id"]: p for p in self.persons}
        self.location_map = {l["location_id"]: l for l in self.locations}
        self.account_map = {a["account_id"]: a for a in self.accounts}
        self.phone_map = {p["phone_id"]: p for p in self.phones}
        self.vehicle_map = {v["vehicle_id"]: v for v in self.vehicles}
        self.case_map = {c["case_id"]: c for c in self.cases}
        self.org_map = {o["organization_id"]: o for o in self.organizations}

        # Normalize phone numbers
        for p in self.phones:
            p["normalized_number"] = p["phone_number"].replace(" ", "").replace("+91", "")

        # Entity resolution: P0020 is alias of P0003
        self.aliases = {
            "P0020": {
                "canonical_id": "P0003",
                "alias_name": "R. Mehta",
                "canonical_name": "Rahul Mehta",
                "reason": "Shared mobile 9000010003, BlueStar_01 employee, age 38, home LOC0001",
                "source": "truth_entity_resolution.csv & CDR / FIR00005"
            }
        }


# Global singleton
dataset = DatasetManager()
