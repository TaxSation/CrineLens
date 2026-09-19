#!/usr/bin/env python3
"""
CrimeLens Unified Launcher
Runs the CrimeLens API and serves the frontend.
"""
import os
import sys
import uvicorn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    print(f"==================================================")
    print(f" Starting CrimeLens Prototype on http://{host}:{port}")
    print(f" SIH Problem Statement: 26189 | Team: Cyber Titans")
    print(f"==================================================")
    uvicorn.run("apps.api.main:app", host=host, port=port, log_level="info")
