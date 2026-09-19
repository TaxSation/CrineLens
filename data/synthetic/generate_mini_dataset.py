#!/usr/bin/env python3
"""
CrimeLens mini dataset generator (all data is synthetic).

Usage:  python3 generate_mini_dataset.py [output_dir]

Deterministic (seed 189). Same column names as the larger SIH 2026 PS 189
dataset, with a few additive columns and files (see README.txt).
Hand-planted patterns are logged in truth_planted_patterns.csv.
"""
import csv
import math
import os
import random
import sys
from datetime import datetime, timedelta

SEED = 189
rng = random.Random(SEED)
OUT = sys.argv[1] if len(sys.argv) > 1 else "crimelens_mini_dataset"
os.makedirs(OUT, exist_ok=True)

START, END = datetime(2026, 6, 1), datetime(2026, 9, 1)  # END exclusive


def T(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def fmt(d):
    return d.strftime("%Y-%m-%d %H:%M:%S")


HOUR_W = [1] * 6 + [4] * 3 + [8] * 4 + [7] * 5 + [8] * 4 + [3] * 2
DOW_W = [1, 1, 1, 1, 1, 0.8, 0.6]


def rand_time(lo=START, hi=END):
    days = [lo + timedelta(days=i) for i in range((hi - lo).days)]
    day = rng.choices(days, weights=[DOW_W[d.weekday()] for d in days])[0]
    h = rng.choices(range(24), weights=HOUR_W)[0]
    return day.replace(hour=h, minute=rng.randrange(60), second=rng.randrange(60))


def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(["" if v is None else v for v in r])


# ------------------------------------------------------------------ master data
LOCS = [
    ("LOC0001", "Ahmedabad_Zone_1", "Ahmedabad", 23.0225, 72.5714, "market"),
    ("LOC0002", "Ahmedabad_Zone_5", "Ahmedabad", 23.0395, 72.5660, "warehouse"),
    ("LOC0003", "Ahmedabad_Zone_9", "Ahmedabad", 22.9950, 72.6000, "highway"),
    ("LOC0004", "Gandhinagar_Zone_2", "Gandhinagar", 23.2156, 72.6369, "office"),
    ("LOC0005", "Surat_Zone_3", "Surat", 21.1702, 72.8311, "bank"),
    ("LOC0006", "Surat_Zone_7", "Surat", 21.2000, 72.8400, "hotel"),
    ("LOC0007", "Vadodara_Zone_4", "Vadodara", 22.3072, 73.1812, "restaurant"),
    ("LOC0008", "Vadodara_Zone_6", "Vadodara", 22.3200, 73.1700, "residential"),
]
LOC_IDS = [l[0] for l in LOCS]
CAM = {l[0]: "CAM%03d" % (i + 1) for i, l in enumerate(LOCS)}

PERSONS = [  # id, name, age, gender, home, occupation
    ("P0001", "Kiran Desai", 41, "M", "LOC0001", "business"),
    ("P0002", "Meera Patel", 34, "F", "LOC0002", "consultant"),
    ("P0003", "Rahul Mehta", 38, "M", "LOC0001", "trader"),
    ("P0004", "Anil Trivedi", 47, "M", "LOC0004", "self_employed"),
    ("P0005", "Nisha Shah", 36, "F", "LOC0002", "consultant"),
    ("P0006", "Vijay Solanki", 52, "M", "LOC0005", "business"),
    ("P0007", "Pooja Joshi", 29, "F", "LOC0003", "employee"),
    ("P0008", "Harsh Vyas", 33, "M", "LOC0001", "driver"),
    ("P0009", "Imran Qureshi", 44, "M", "LOC0007", "business"),
    ("P0010", "Sunita Rathod", 39, "F", "LOC0008", "trader"),
    ("P0011", "Deepak Chauhan", 50, "M", "LOC0007", "self_employed"),
    ("P0012", "Farida Sheikh", 31, "F", "LOC0006", "employee"),
    ("P0013", "Manoj Parmar", 45, "M", "LOC0008", "driver"),
    ("P0014", "Latika Nair", 27, "F", "LOC0006", "student"),
    ("P0015", "Sanjay Bhatt", 55, "M", "LOC0004", "consultant"),
    ("P0016", "Anjali Kulkarni", 30, "F", "LOC0005", "employee"),
    ("P0017", "Tarun Sharma", 23, "M", "LOC0003", "student"),
    ("P0018", "Bhavna Modi", 42, "F", "LOC0002", "self_employed"),
    ("P0019", "Yash Kothari", 36, "M", "LOC0006", "unknown"),
    ("P0020", "R. Mehta", 38, "M", "LOC0001", "trader"),  # alias record of P0003
]
HOME = {p[0]: p[4] for p in PERSONS}
NET_A = ["P0001", "P0002", "P0003", "P0004", "P0005", "P0006", "P0007", "P0008", "P0020"]
NET_B = ["P0009", "P0010", "P0011", "P0012", "P0013", "P0014"]
IND = ["P0015", "P0016", "P0017", "P0018", "P0019"]
NET = {**{p: "NET_A" for p in NET_A}, **{p: "NET_B" for p in NET_B}, **{p: "INDEPENDENT" for p in IND}}
NO_PAIR = {frozenset(("P0003", "P0020"))}  # same real person, never call each other

ORGS = [
    ("O001", "BlueStar_01", "business", "LOC0001"),
    ("O002", "Vertex_02", "company", "LOC0004"),
    ("O003", "Meridian_03", "business", "LOC0007"),
]
MEMBERS = [
    ("M001", "O001", "P0001", "owner"), ("M002", "O001", "P0003", "employee"),
    ("M003", "O001", "P0020", "employee"), ("M004", "O002", "P0004", "director"),
    ("M005", "O002", "P0015", "employee"), ("M006", "O003", "P0009", "owner"),
    ("M007", "O003", "P0011", "employee"),
]
VEHICLES = [
    ("V0001", "SYN-GJ-1001", "suv", "P0001"), ("V0002", "SYN-GJ-1002", "car", "P0002"),
    ("V0003", "SYN-GJ-1003", "suv", "P0009"), ("V0004", "SYN-GJ-1004", "suv", "P0004"),
    ("V0005", "SYN-GJ-1005", "car", "P0011"), ("V0006", "SYN-GJ-1006", "bike", "P0013"),
    ("V0007", "SYN-GJ-1007", "car", "P0015"), ("V0008", "SYN-GJ-1008", "van", "P0008"),
]
VEH_OF = {v[3]: v[0] for v in VEHICLES}

# phones: PH00nn = primary phone of person Pnn. P0020 (alias) shares P0003's number.
PRIMARY = {p[0]: "PH%04d" % int(p[0][1:]) for p in PERSONS}
PHONES = []
for p in PERSONS:
    n = int(p[0][1:])
    number = "9000010%03d" % n if n != 20 else "+91 90000 10003"
    PHONES.append((PRIMARY[p[0]], number, p[0], "mobile"))
PHONES += [
    ("PH0021", "9000010105", "P0005", "secondary"),
    ("PH0022", "9000010111", "P0011", "secondary"),
    ("PH0023", "9000010201", "P0001", "business"),
    ("PH0024", "9000010209", "P0009", "business"),
]

ACC = {p[0]: "ACC%05d" % int(p[0][1:]) for p in PERSONS}
ACC_OWNER = {v: k for k, v in ACC.items()}
ACC_OWNER["ACC00021"] = "P0005"
ACCOUNTS = []
for i, p in enumerate(PERSONS):
    typ = "current" if p[5] in ("business", "trader") else "savings"
    status = "frozen" if p[0] == "P0019" else "active"
    ACCOUNTS.append((ACC[p[0]], p[0], "SynthBank_" + "ABC"[i % 3], typ, status))
ACCOUNTS.append(("ACC00021", "P0005", "SynthBank_B", "current", "active"))

CASES = [
    ("CASE0001", "extortion", "2026-08-20", "LOC0002", "under_investigation"),
    ("CASE0002", "vehicle_theft", "2026-07-04", "LOC0007", "under_investigation"),
    ("CASE0003", "burglary", "2026-06-18", "LOC0002", "closed"),
    ("CASE0004", "cybercrime", "2026-07-28", "LOC0004", "open"),
    ("CASE0005", "fraud", "2026-08-05", "LOC0005", "open"),
    ("CASE0006", "robbery", "2026-08-25", "LOC0003", "open"),
    ("CASE0101", "extortion", "2021-03-14", "LOC0001", "closed"),
    ("CASE0102", "fraud", "2022-07-09", "LOC0004", "closed"),
    ("CASE0103", "vehicle_theft", "2020-11-02", "LOC0007", "closed"),
    ("CASE0104", "burglary", "2023-05-21", "LOC0002", "closed"),
    ("CASE0105", "robbery", "2019-09-17", "LOC0005", "closed"),
    ("CASE0106", "cybercrime", "2024-02-11", "LOC0003", "closed"),
]
HISTORY = [  # person, case, crime, year, outcome
    ("P0001", "CASE0101", "extortion", 2021, "convicted"),
    ("P0004", "CASE0101", "extortion", 2021, "convicted"),
    ("P0004", "CASE0102", "fraud", 2022, "acquitted"),
    ("P0006", "CASE0102", "fraud", 2022, "convicted"),
    ("P0009", "CASE0103", "vehicle_theft", 2020, "convicted"),
    ("P0011", "CASE0103", "vehicle_theft", 2020, "convicted"),
    ("P0008", "CASE0104", "burglary", 2023, "acquitted"),
    ("P0013", "CASE0105", "robbery", 2019, "convicted"),
    ("P0015", "CASE0106", "cybercrime", 2024, "pending"),
]

# ------------------------------------------------------------------ CDR
cdr = []


def add_call(t, a, b, call_type=None, dur=None, cell=None, ph_a=None, ph_b=None, tag=""):
    call_type = call_type or ("sms" if rng.random() < 0.35 else "voice")
    if call_type == "sms":
        dur = 0
    elif dur is None:
        dur = int(min(1500, max(8, rng.lognormvariate(math.log(120), 0.9))))
    cell = cell or (HOME[a] if rng.random() < 0.7 else rng.choice(LOC_IDS))
    cdr.append(dict(t=t, a=a, b=b, dur=dur, cell=cell, type=call_type,
                    pa=ph_a or PRIMARY[a], pb=ph_b or PRIMARY[b], tag=tag))


def wpair(members, weights):
    while True:
        a, b = rng.choices(members, weights=weights, k=2)
        if a != b and frozenset((a, b)) not in NO_PAIR:
            return a, b


A_W = [4, 2, 1.5, 2.5, 2, 1.5, 1.5, 1, 1]
B_W = [4, 2, 2, 1.5, 1.5, 1]
for _ in range(70):
    a, b = wpair(NET_A, A_W)
    add_call(rand_time(), a, b)
for _ in range(44):
    a, b = wpair(NET_B, B_W)
    add_call(rand_time(), a, b)
for _ in range(8):
    a, b = rng.sample(IND, 2)
    add_call(rand_time(), a, b)
for a, b, n in [("P0015", "P0004", 3), ("P0016", "P0006", 2), ("P0018", "P0002", 2),
                ("P0017", "P0007", 2), ("P0019", "P0007", 3), ("P0019", "P0012", 3),
                ("P0007", "P0005", 3)]:
    tag = "PAT11" if "P0019" in (a, b) or (a, b) == ("P0007", "P0005") else ""
    for _ in range(n):
        x, y = (a, b) if rng.random() < 0.5 else (b, a)
        add_call(rand_time(), x, y, tag=tag)
for b in ["P0001", "P0004", "P0002", "P0006", "P0001", "P0008"]:  # alias P0020 inside NET_A
    a, c = ("P0020", b) if rng.random() < 0.5 else (b, "P0020")
    add_call(rand_time(START, T("2026-08-17 00:00:00")), a, c, tag="PAT04")

# PAT01 bridge: P0005 (NET_A) talks to NET_B on a secondary phone since June
for b in ["P0009"] * 4 + ["P0010"] * 3 + ["P0012"] * 3:
    t = rand_time(START, T("2026-08-14 00:00:00"))
    if rng.random() < 0.5:
        add_call(t, "P0005", b, ph_a="PH0021", tag="PAT01;PAT11" if b == "P0012" else "PAT01")
    else:
        add_call(t, b, "P0005", ph_b="PH0021", tag="PAT01;PAT11" if b == "P0012" else "PAT01")

# PAT02 communication spike in the 48h before the incident (2026-08-20)
core, cw = ["P0001", "P0002", "P0004", "P0006"], [4, 2, 2.5, 1.5]
for _ in range(30):
    a, b = wpair(core, cw)
    add_call(T("2026-08-18 00:00:00") + timedelta(seconds=rng.randrange(48 * 3600)), a, b, tag="PAT02")
add_call(T("2026-08-18 15:20:00"), "P0003", "P0001", "voice", 240, tag="PAT02;PAT04")
add_call(T("2026-08-19 10:42:00"), "P0020", "P0004", "voice", 185, tag="PAT02;PAT04")
add_call(T("2026-08-19 22:15:00"), "P0004", "P0020", "voice", 96, tag="PAT02;PAT04")

# PAT06 new cross-community edges (first ever NET_A <-> NET_B contact outside the bridge)
add_call(T("2026-08-15 20:18:00"), "P0001", "P0009", "voice", 210, tag="PAT06")
add_call(T("2026-08-16 09:40:00"), "P0009", "P0001", "voice", 145, tag="PAT06")
add_call(T("2026-08-17 17:05:00"), "P0001", "P0009", "sms", tag="PAT06")
add_call(T("2026-08-19 21:55:00"), "P0009", "P0001", "voice", 330, tag="PAT06")
add_call(T("2026-08-16 10:12:00"), "P0004", "P0011", "voice", 120, ph_b="PH0022", tag="PAT06")
add_call(T("2026-08-17 13:31:00"), "P0011", "P0004", "voice", 88, ph_a="PH0022", tag="PAT06")
add_call(T("2026-08-18 22:47:00"), "P0004", "P0011", "voice", 275, ph_b="PH0022", tag="PAT06;PAT02")
add_call(T("2026-08-19 19:20:00"), "P0011", "P0004", "voice", 190, ph_a="PH0022", tag="PAT06;PAT02")
# PAT12 claim in FIR00001 (Anil Trivedi called the complainant) is backed by this record
add_call(T("2026-08-17 11:15:00"), "P0004", "P0018", "voice", 95, tag="PAT12")

cdr.sort(key=lambda r: r["t"])
for i, r in enumerate(cdr, 1):
    r["id"] = "CDR%06d" % i

# ------------------------------------------------------------------ transactions
txns = []


def add_txn(t, s, r, amt, ttype=None, loc=None, tag=""):
    ttype = ttype or rng.choices(["UPI", "IMPS", "NEFT", "cash_transfer"], weights=[45, 20, 25, 10])[0]
    loc = loc or (HOME[ACC_OWNER[s]] if rng.random() < 0.8 else rng.choice(LOC_IDS))
    txns.append(dict(t=t, s=s, r=r, amt=amt, type=ttype, loc=loc, tag=tag))


def base_amt():
    return round(min(30000, max(150, rng.lognormvariate(math.log(3200), 0.8))), 2)


def acc_pair(members):
    while True:
        a, b = rng.sample(members, 2)
        if frozenset((a, b)) not in NO_PAIR:
            return ACC[a], ACC[b]


for _ in range(16):
    s, r = acc_pair(NET_A)
    add_txn(rand_time(), s, r, base_amt())
for _ in range(12):
    s, r = acc_pair(NET_B)
    add_txn(rand_time(), s, r, base_amt())
for _ in range(6):
    s, r = acc_pair(["P0015", "P0016", "P0017", "P0018"])
    add_txn(rand_time(), s, r, base_amt())
add_txn(T("2026-07-02 11:20:14"), "ACC00021", "ACC00010", 6200.00, "UPI", tag="PAT01")
add_txn(T("2026-07-19 15:45:40"), "ACC00009", "ACC00021", 4800.00, "NEFT", tag="PAT01")
add_txn(T("2026-07-15 10:30:22"), "ACC00007", "ACC00021", 2500.00, "UPI", tag="PAT11")
add_txn(T("2026-08-06 13:05:09"), "ACC00021", "ACC00012", 3900.00, "UPI", tag="PAT11")
add_txn(T("2026-07-27 10:14:33"), "ACC00007", "ACC00015", 48000.00, "UPI", tag="CASE0004")
add_txn(T("2026-07-25 16:02:51"), "ACC00017", "ACC00015", 7000.00, "UPI", tag="CASE0004")
add_txn(T("2026-07-29 12:48:05"), "ACC00018", "ACC00015", 12500.00, "IMPS", tag="CASE0004")
add_txn(T("2026-08-04 15:30:44"), "ACC00017", "ACC00016", 15500.00, "NEFT", tag="CASE0005")
# PAT03 layering chain on 2026-08-19, each hop keeps ~97% of the previous amount
add_txn(T("2026-08-19 09:12:04"), "ACC00001", "ACC00004", 95000.00, "IMPS", "LOC0001", "PAT03;PAT12")
add_txn(T("2026-08-19 11:40:37"), "ACC00004", "ACC00021", 92400.00, "UPI", "LOC0004", "PAT03")
add_txn(T("2026-08-19 15:05:19"), "ACC00021", "ACC00011", 90100.00, "NEFT", "LOC0002", "PAT03")
add_txn(T("2026-08-19 18:30:52"), "ACC00011", "ACC00016", 87500.00, "cash_transfer", "LOC0007", "PAT03")
# PAT09 anomalous night-time cash transfer
add_txn(T("2026-08-12 02:47:33"), "ACC00016", "ACC00008", 248000.00, "cash_transfer", "LOC0003", "PAT09")
# PAT10 four just-under-10,000 transfers from one account within four hours
for ts, r, amt, ty in [("10:05:22", "ACC00010", 9800.00, "UPI"), ("11:12:48", "ACC00012", 9600.00, "IMPS"),
                       ("12:26:09", "ACC00014", 9700.00, "UPI"), ("13:40:31", "ACC00009", 9500.00, "UPI")]:
    add_txn(T("2026-08-14 " + ts), "ACC00013", r, amt, ty, "LOC0008", "PAT10")
txns.sort(key=lambda r: r["t"])
for i, r in enumerate(txns, 1):
    r["id"] = "TXN%06d" % i

# ------------------------------------------------------------------ surveillance
surv = []


def add_surv(t, loc, person, veh, etype, conf, tag=""):
    surv.append(dict(t=t, loc=loc, person=person, veh=veh, type=etype, conf=conf, tag=tag))


for _ in range(24):
    p = rng.choice([x[0] for x in PERSONS if x[0] != "P0020"])
    loc = HOME[p] if rng.random() < 0.65 else rng.choice(LOC_IDS)
    veh = VEH_OF.get(p)
    roll = rng.random()
    if veh and roll < 0.30:
        ev, pp, vv = "person_vehicle_cooccurrence", p, veh
    elif veh and roll < 0.45:
        ev, pp, vv = "vehicle_detected", None, veh
    elif roll < 0.55:
        ev, pp, vv = "loitering", p, None
    elif roll < 0.63:
        ev, pp, vv = "unusual_movement", p, None
    else:
        ev, pp, vv = "person_detected", p, None
    add_surv(rand_time(), loc, pp, vv, ev, round(rng.uniform(0.75, 0.99), 3))
# PAT05 cross-network co-location on the highway zone, days before the incident
add_surv(T("2026-08-17 22:05:12"), "LOC0003", "P0001", "V0001", "person_vehicle_cooccurrence", 0.93, "PAT05;PAT12")
add_surv(T("2026-08-17 22:11:40"), "LOC0003", None, "V0003", "vehicle_detected", 0.88, "PAT05;PAT12")
add_surv(T("2026-08-17 22:17:05"), "LOC0003", "P0009", None, "person_detected", 0.91, "PAT05")
add_surv(T("2026-08-17 22:24:30"), "LOC0003", "P0005", None, "person_detected", 0.86, "PAT05")
# PAT07 location conflict: FIR00002 puts P0006 in Surat at ~21:30; camera has him in Ahmedabad at 21:40
add_surv(T("2026-08-19 21:40:15"), "LOC0001", "P0006", None, "person_detected", 0.90, "PAT07")
# PAT11 hidden link: P0007 and P0012 in the same Surat zone within 18 minutes
add_surv(T("2026-08-10 14:02:00"), "LOC0006", "P0007", None, "person_detected", 0.87, "PAT11")
add_surv(T("2026-08-10 14:20:30"), "LOC0006", "P0012", None, "person_detected", 0.89, "PAT11")
# PAT13 presence at the CASE0001 scene on the incident date
add_surv(T("2026-08-20 19:40:00"), "LOC0002", None, "V0004", "vehicle_detected", 0.85, "PAT13")
add_surv(T("2026-08-20 19:55:00"), "LOC0002", "P0002", None, "loitering", 0.82, "PAT13")
add_surv(T("2026-08-20 20:10:00"), "LOC0002", "P0001", None, "person_detected", 0.90, "PAT13")
surv.sort(key=lambda r: r["t"])
for i, r in enumerate(surv, 1):
    r["id"] = "SURV%06d" % i
    r["video"] = "synthetic_video_clip_%03d.mp4" % i

# ------------------------------------------------------------------ text sources
FIRS = [  # case, time, station, language, text, persons mentioned, tag
    ("CASE0001", "2026-08-21 09:40:00", "PS_05", "en",
     "Complainant Bhavna Modi reported that on the evening of 20 August two men in a white SUV, registration "
     "SYN-GJ-1004, arrived at her shop near Ahmedabad_Zone_5 and demanded Rs 90,000. She named one of the men "
     "as Anil Trivedi and said he had called her from 9000010004 earlier that week.", ["P0018", "P0004"], "PAT12"),
    ("CASE0001", "2026-08-21 14:10:00", "PS_05", "en",
     "Witness reported that Vijay Solanki was seen near Surat_Zone_3 at about 9:30 pm on 19 August, "
     "the day before the incident.", ["P0006"], "PAT07"),
    ("CASE0001", "2026-08-22 11:00:00", "PS_05", "en",
     "Investigation notes mention that Kiran Desai met Imran Qureshi near Ahmedabad_Zone_9 on the night of "
     "17 August. A vehicle with registration SYN-GJ-1003 was also noted.", ["P0001", "P0009"], "PAT05;PAT12"),
    ("CASE0001", "2026-08-23 10:15:00", "PS_05", "en",
     "A transaction of Rs 95,000 from the account of Kiran Desai to Anil Trivedi on 19 August was identified "
     "during the preliminary investigation.", ["P0001", "P0004"], "PAT03;PAT12"),
    ("CASE0001", "2026-08-23 16:45:00", "PS_05", "hi",
     "जांच में सामने आया कि आर. मेहता ने 19 अगस्त को अनिल त्रिवेदी से फोन पर बात की थी।",
     ["P0020", "P0004"], "PAT04"),
    ("CASE0002", "2026-07-05 08:30:00", "PS_12", "en",
     "Deepak Chauhan reported that his car, registration SYN-GJ-1005, was stolen from Vadodara_Zone_4 "
     "overnight. Neighbours noticed Farida Sheikh near the parking area.", ["P0011", "P0012"], ""),
    ("CASE0003", "2026-06-18 21:30:00", "PS_05", "en",
     "Burglary reported at a shop in Ahmedabad_Zone_5. The watchman recalled seeing Harsh Vyas driving a van "
     "earlier in the evening.", ["P0008"], ""),
    ("CASE0004", "2026-07-29 10:05:00", "PS_08", "en",
     "Complainant Pooja Joshi lost Rs 48,000 in an online payment fraud. The funds were traced to an account "
     "held by Sanjay Bhatt.", ["P0007", "P0015"], "CASE0004"),
    ("CASE0005", "2026-08-06 12:20:00", "PS_03", "en",
     "Tarun Sharma filed a complaint against Anjali Kulkarni over a fake invoice for Rs 15,500. Payment was "
     "made to her account on 4 August.", ["P0017", "P0016"], "CASE0005"),
    ("CASE0006", "2026-08-25 23:10:00", "PS_07", "en",
     "Robbery reported on the Ahmedabad_Zone_9 highway. A witness noted the attackers' car, registration "
     "SYN-GJ-1002.", [], ""),
]
INTELS = [  # case, date, classification, confidence, text, tag
    ("CASE0001", "2026-08-22", "analyst", "high",
     "Analyst notes a sharp rise in calls between Kiran Desai, Meera Patel, Anil Trivedi and Vijay Solanki "
     "in the two days before the incident.", "PAT02"),
    ("CASE0001", "2026-08-22", "field_source", "medium",
     "Field source states that Nisha Shah acts as a go-between for Kiran Desai and Imran Qureshi.", "PAT01"),
    ("CASE0001", "2026-08-23", "field_source", "medium",
     "Field source links vehicle SYN-GJ-1006 to Farida Sheikh.", "PAT08"),
    ("CASE0001", "2026-08-24", "analyst", "high",
     "Analyst notes unusual transfer activity on 19 August involving several accounts linked to Kiran Desai.",
     "PAT03"),
    ("CASE0001", "2026-08-24", "internal", "low",
     "Unverified tip suggests Pooja Joshi and Farida Sheikh know each other.", "PAT11"),
    ("CASE0002", "2026-07-06", "field_source", "medium",
     "Source reports that the stolen car was seen heading towards Surat.", ""),
    ("CASE0003", "2026-06-20", "internal", "low",
     "Possible involvement of a driver known to Harsh Vyas.", ""),
    ("CASE0004", "2026-07-30", "analyst", "medium",
     "The account of Sanjay Bhatt received funds from several unrelated senders within one week.", "CASE0004"),
    ("CASE0005", "2026-08-08", "analyst", "medium",
     "Anjali Kulkarni appears in more than one case this month.", ""),
    ("CASE0006", "2026-08-26", "field_source", "high",
     "Source confirms a car matching SYN-GJ-1002 was used near Ahmedabad_Zone_9 on the night of 25 August.", ""),
]
POSTS = [  # person, time, platform, text, loc, sentiment, tag
    ("P0001", "2026-06-05 19:10:00", "A", "Long day at the office. Heading home.", "LOC0001", "neutral", ""),
    ("P0002", "2026-06-12 12:30:00", "B", "Lunch with the team near Ahmedabad_Zone_5.", "LOC0002", "positive", ""),
    ("P0009", "2026-06-20 18:45:00", "A", "New shipment arrived at the warehouse today.", "LOC0007", "positive", ""),
    ("P0010", "2026-06-28 09:15:00", "B", "Market is slow this week.", "LOC0008", "negative", ""),
    ("P0004", "2026-07-03 21:20:00", "A", "Need to speak with Kiran tomorrow.", "LOC0004", "neutral", ""),
    ("P0011", "2026-07-08 16:00:00", "B", "Someone took my car from the parking. Not happy.", "LOC0007", "negative", ""),
    ("P0014", "2026-07-12 20:30:00", "A", "Weekend trip to Surat with friends!", "LOC0006", "positive", ""),
    ("P0017", "2026-07-15 11:45:00", "B", "Exams over, finally.", "LOC0003", "positive", ""),
    ("P0006", "2026-07-19 22:05:00", "A", "Business is picking up.", "LOC0005", "positive", ""),
    ("P0012", "2026-07-23 14:10:00", "B", "Anyone available around Surat_Zone_7 this weekend?", "LOC0006", "neutral", ""),
    ("P0015", "2026-07-27 08:50:00", "A", "Payment received, thanks.", "LOC0004", "positive", ""),
    ("P0007", "2026-08-02 13:25:00", "B", "Visiting a friend in Surat soon.", "LOC0003", "neutral", "PAT11"),
    ("P0016", "2026-08-04 17:40:00", "A", "Invoice sent. Waiting for payment.", "LOC0005", "neutral", ""),
    ("P0019", "2026-08-10 09:30:00", "B", "Heading to Surat_Zone_7 for the day.", "LOC0006", "neutral", "PAT11"),
    ("P0013", "2026-08-14 12:00:00", "A", "Busy morning running errands.", "LOC0008", "neutral", "PAT10"),
    ("P0001", "2026-08-14 21:15:00", "A", "New contact made. Good things ahead.", "LOC0001", "positive", "PAT06"),
    ("P0009", "2026-08-14 22:30:00", "B", "Met someone interesting today.", "LOC0007", "positive", "PAT06"),
    ("P0001", "2026-08-17 18:30:00", "A", "Meeting near Ahmedabad_Zone_9 tonight.", "LOC0003", "neutral", "PAT05"),
    ("P0009", "2026-08-17 19:05:00", "B", "On my way to Ahmedabad.", "LOC0007", "neutral", "PAT05"),
    ("P0005", "2026-08-17 21:40:00", "B", "Busy night ahead.", "LOC0002", "neutral", "PAT05"),
    ("P0020", "2026-08-18 20:00:00", "A", "Working late at BlueStar_01.", "LOC0001", "neutral", "PAT04"),
    ("P0002", "2026-08-18 23:10:00", "A", "Cannot sleep, too much going on.", "LOC0002", "negative", ""),
    ("P0006", "2026-08-19 21:35:00", "A", "Dinner in Ahmedabad with old friends.", "LOC0001", "positive", "PAT07"),
    ("P0004", "2026-08-19 20:05:00", "A", "Everything is set for tomorrow.", "LOC0004", "neutral", "PAT02"),
    ("P0018", "2026-08-20 22:40:00", "B", "Scared after what happened at my shop today.", "LOC0002", "negative", ""),
    ("P0010", "2026-08-21 10:20:00", "B", "Some people are asking questions. Staying quiet.", "LOC0008", "negative", ""),
]

# ------------------------------------------------------------------ relationships (convenience view)
rels = []


def add_rel(st, sid, rt, tt, tid, ts, src):
    rels.append((st, sid, rt, tt, tid, ts, src))


for r in cdr:
    add_rel("person", r["a"], "COMMUNICATES_WITH", "person", r["b"], fmt(r["t"]), r["id"])
for r in surv:
    if r["person"]:
        add_rel("person", r["person"], "APPEARS_AT", "location", r["loc"], fmt(r["t"]), r["id"])
for a in ACCOUNTS:
    add_rel("person", a[1], "OWNS_ACCOUNT", "account", a[0], None, "bank_accounts")
for v in VEHICLES:
    add_rel("person", v[3], "OWNS_VEHICLE", "vehicle", v[0], None, "vehicles")
for p in PHONES:
    add_rel("person", p[2], "OWNS_PHONE", "phone", p[0], None, "phone_numbers")
for m in MEMBERS:
    add_rel("person", m[2], "WORKED_FOR", "organization", m[1], None, "organization_members")
for r in txns:
    add_rel("account", r["s"], "TRANSFERRED_TO", "account", r["r"], fmt(r["t"]), r["id"])
for i, f in enumerate(FIRS, 1):
    for p in f[5]:
        add_rel("person", p, "ASSOCIATED_WITH_CASE", "case", f[0], f[1], "FIR%05d" % i)
for i, h in enumerate(HISTORY, 1):
    add_rel("person", h[0], "ASSOCIATED_WITH_CASE", "case", h[1], None, "HIST%05d" % i)
rels.sort(key=lambda r: (r[5] is None, r[5] or ""))

# ------------------------------------------------------------------ write tables
write("persons.csv", ["person_id", "name", "age", "gender", "home_location_id", "occupation"], PERSONS)
write("organizations.csv", ["organization_id", "organization_name", "organization_type", "location_id"], ORGS)
write("organization_members.csv", ["membership_id", "organization_id", "person_id", "role"], MEMBERS)
write("locations.csv", ["location_id", "location_name", "city", "latitude", "longitude", "location_type"], LOCS)
write("vehicles.csv", ["vehicle_id", "registration_no", "vehicle_type", "owner_person_id"], VEHICLES)
write("phone_numbers.csv", ["phone_id", "phone_number", "owner_person_id", "phone_type"], PHONES)
write("bank_accounts.csv", ["account_id", "account_holder_person_id", "bank_name", "account_type", "account_status"], ACCOUNTS)
write("cases.csv", ["case_id", "case_type", "incident_date", "primary_location_id", "status"], CASES)
write("criminal_history.csv", ["history_id", "person_id", "case_id", "crime_type", "year", "outcome"],
      [("HIST%05d" % i,) + h for i, h in enumerate(HISTORY, 1)])
write("fir_reports.csv",
      ["fir_id", "case_id", "report_time", "police_station", "report_text", "source_type", "language"],
      [("FIR%05d" % i, f[0], f[1], f[2], f[4], "synthetic_fir", f[3]) for i, f in enumerate(FIRS, 1)])
write("intelligence_reports.csv",
      ["intelligence_report_id", "case_id", "report_date", "source_classification", "report_text", "confidence"],
      [("INTEL%05d" % i, x[0], x[1], x[2], x[4], x[3]) for i, x in enumerate(INTELS, 1)])
write("social_media_intelligence.csv",
      ["post_id", "person_id", "timestamp", "platform", "text", "location_id", "sentiment"],
      [("POST%06d" % i, x[0], x[1], "synthetic_social_" + x[2], x[3], x[4], x[5]) for i, x in enumerate(POSTS, 1)])
write("cdr.csv",
      ["cdr_id", "caller_person_id", "receiver_person_id", "timestamp", "duration_seconds", "cell_location_id",
       "call_type", "caller_phone_id", "receiver_phone_id"],
      [(r["id"], r["a"], r["b"], fmt(r["t"]), r["dur"], r["cell"], r["type"], r["pa"], r["pb"]) for r in cdr])
write("financial_transactions.csv",
      ["transaction_id", "sender_account_id", "receiver_account_id", "timestamp", "amount", "transaction_type",
       "location_id"],
      [(r["id"], r["s"], r["r"], fmt(r["t"]), "%.2f" % r["amt"], r["type"], r["loc"]) for r in txns])
write("surveillance_events.csv",
      ["surveillance_id", "camera_id", "timestamp", "location_id", "person_id", "vehicle_id", "event_type",
       "video_reference", "detection_confidence"],
      [(r["id"], CAM[r["loc"]], fmt(r["t"]), r["loc"], r["person"], r["veh"], r["type"], r["video"], r["conf"])
       for r in surv])
write("relationships.csv",
      ["relationship_id", "source_entity_type", "source_entity_id", "relationship_type", "target_entity_type",
       "target_entity_id", "timestamp", "source_record_id"],
      [("REL%06d" % i,) + r for i, r in enumerate(rels, 1)])

# ------------------------------------------------------------------ ground truth (NOT model input)
write("synthetic_network_truth.csv", ["person_id", "synthetic_network"], [(p[0], NET[p[0]]) for p in PERSONS])
write("truth_entity_resolution.csv", ["canonical_person_id", "person_id", "note"],
      [("P0003", "P0003", "primary record"),
       ("P0003", "P0020", "alias record: 'R. Mehta', same number, same org, same home area")])
write("truth_hidden_links.csv", ["person_a", "person_b", "basis"],
      [("P0007", "P0012", "no direct call; common neighbours P0005 and P0019; same Surat zone 2026-08-10; "
                          "money path ACC00007>ACC00021>ACC00012")])


def ids(rows, pat, key="id"):
    return ";".join(r[key] for r in rows if pat in r["tag"].split(";"))


def ids_list(rows, prefix, pat, tagidx):
    return ";".join("%s%05d" % (prefix, i) for i, r in enumerate(rows, 1) if pat in r[tagidx].split(";"))


def all_ids(pat):
    parts = [ids(cdr, pat), ids(txns, pat), ids(surv, pat),
             ids_list(FIRS, "FIR", pat, 6), ids_list(INTELS, "INTEL", pat, 5)]
    parts.append(";".join("POST%06d" % i for i, x in enumerate(POSTS, 1) if pat in x[6].split(";")))
    return ";".join(p for p in parts if p)


PATTERNS = [
    ("PAT01", "bridge_node", "P0005", "2026-06-01..2026-08-14",
     "NET_A member P0005 calls NET_B (P0009, P0010, P0012) on secondary phone PH0021 and moves money to NET_B.",
     "P0005 is in the top 3 by betweenness (rank 2 of 20) and is the only member linking both communities before 2026-08-15."),
    ("PAT02", "communication_spike", "P0001;P0002;P0004;P0006;P0003;P0020", "2026-08-18..2026-08-19",
     "35 calls among the core group in the 48h before the CASE0001 incident vs about 0.5 per day earlier.",
     "'What Changed?' flags the window; spike shown against the June-July baseline."),
    ("PAT03", "transaction_chain", "ACC00001>ACC00004>ACC00021>ACC00011>ACC00016", "2026-08-19",
     "Four hops in nine hours, each keeping about 97% of the previous amount, ending in a cash transfer.",
     "Path finder returns the chain; near-equal amounts and short gaps raise the lead."),
    ("PAT04", "alias", "P0003;P0020", "whole period",
     "'R. Mehta' (P0020) is the same person as 'Rahul Mehta' (P0003): same number in two formats, same "
     "organisation, same home area, same age. FIR00005 (Hindi) names the alias.",
     "Entity resolution proposes a merge of P0020 into P0003 with reasons; a human confirms."),
    ("PAT05", "co_location", "P0001;P0009;P0005", "2026-08-17 22:05..22:24",
     "Three people from two networks (plus vehicle V0003) at Ahmedabad_Zone_9 within 19 minutes.",
     "Flagged as a cross-community co-location three days before the incident."),
    ("PAT06", "new_cross_community_edge", "P0001;P0009;P0004;P0011", "2026-08-15..2026-08-19",
     "First direct contact between NET_A and NET_B outside the bridge; P0011 uses new phone PH0022.",
     "Appears as new edges in the last 7 days and not in the 30-90 day baseline."),
    ("PAT07", "conflicting_evidence_location", "P0006", "2026-08-19 21:30..21:40",
     "FIR00002 places P0006 in Surat_Zone_3 at ~21:30; a camera and a social post place him in Ahmedabad_Zone_1 "
     "within ten minutes (about 210 km apart).",
     "Contradiction flagged; both claims kept with sources; no automatic winner."),
    ("PAT08", "conflicting_evidence_ownership", "V0006;P0012;P0013", "2026-08-23",
     "INTEL00003 links vehicle SYN-GJ-1006 to Farida Sheikh; the vehicle registry lists Manoj Parmar as owner.",
     "Ownership conflict flagged with both sources."),
    ("PAT09", "anomalous_transaction", "ACC00016>ACC00008", "2026-08-12 02:47",
     "Rs 248,000 cash transfer at 02:47, about 45 times the median transaction amount.",
     "Anomaly score high; shown with amount, hour and account history."),
    ("PAT10", "rapid_split_transfers", "ACC00013", "2026-08-14 10:05..13:40",
     "Four transfers of 9,500-9,800 to four different accounts within four hours.",
     "Flagged as a repeated-amount burst; no legal threshold is assumed."),
    ("PAT11", "hidden_link", "P0007;P0012", "2026-07-15..2026-08-10",
     "No direct contact, but common neighbours P0005 and P0019, same Surat zone within 18 minutes, and a "
     "two-step money path via ACC00021.",
     "Should surface among cross-community candidates once common neighbours, co-location and the money path are combined. Common neighbours alone rank it below some within-network pairs."),
    ("PAT12", "corroborated_claim", "P0004;P0018;P0001;P0009", "2026-08-17..2026-08-23",
     "FIR00001 (call from P0004), FIR00003 (meeting and vehicle) and FIR00004 (Rs 95,000) are each backed by "
     "a CDR, surveillance or transaction record.",
     "Copilot answers 'show evidence for...' with the matching structured records."),
    ("PAT13", "incident_scene_presence", "P0001;P0002;V0004", "2026-08-20 19:40..20:10",
     "Two persons and V0004 (owner P0004) seen at the CASE0001 incident location.",
     "Shown on the timeline and map for the incident date."),
]
write("truth_planted_patterns.csv",
      ["pattern_id", "pattern_type", "entities", "time_window", "description", "expected_system_behaviour",
       "record_ids"],
      [p + (all_ids(p[0]),) for p in PATTERNS])

print("wrote", len(os.listdir(OUT)), "files to", OUT)
