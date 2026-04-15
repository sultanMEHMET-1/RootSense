#!/usr/bin/env python3
"""Small smoke-test client for the local RootSense Flask API."""

from __future__ import annotations

import sys

import requests


BASE_URL = "http://127.0.0.1:5000"


def show_response(label: str, response: requests.Response) -> None:
    print(label)
    print("-" * len(label))
    print(f"Status: {response.status_code}")
    try:
        print(response.json())
    except ValueError:
        print(response.text)
    print()


def main() -> int:
    try:
        show_response("GET /health", requests.get(f"{BASE_URL}/health", timeout=5))
        show_response("GET /api/risk", requests.get(f"{BASE_URL}/api/risk", timeout=15))
        show_response(
            "POST /api/advice",
            requests.post(
                f"{BASE_URL}/api/advice",
                json={"question": "Should I irrigate today?"},
                timeout=30,
            ),
        )
        return 0
    except requests.RequestException as exc:
        print(f"API smoke test failed: {exc}")
        print("Start the server with: python farm_advisor_api.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
