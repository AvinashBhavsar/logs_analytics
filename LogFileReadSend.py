
#!/usr/bin/env python3
"""
Pick the most recently modified file in a directory (log file) and POST it to an API
as multipart/form-data. Uses requests. Exits with non-zero codes on errors.
"""

import os
import sys
import argparse
import requests
from typing import Optional

# ---------- CONFIG (edit) ----------
API_URL = "https://example.com/api/upload"     # <-- set your API endpoint
FIELD_NAME = "file"                             # form field name expected by API
HEADERS = {"Authorization": "Bearer YOUR_TOKEN"}  # set to {} if none
TIMEOUT = 60                                    # seconds
# ------------------------------------

def find_most_recent_file(directory: str) -> Optional[str]:
    try:
        entries = (os.path.join(directory, fn) for fn in os.listdir(directory))
    except FileNotFoundError:
        return None
    files = [p for p in entries if os.path.isfile(p)]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def send_file(path: str, url: str, field: str, headers: dict, timeout: int) -> requests.Response:
    with open(path, "rb") as fh:
        files = {field: (os.path.basename(path), fh)}
        resp = requests.post(url, headers=headers, files=files, timeout=timeout)
    resp.raise_for_status()
    return resp

def main():
    p = argparse.ArgumentParser(description="Send latest log file from a directory to an API")
    p.add_argument("directory", help="Directory containing log files")
    p.add_argument("--url", help="Override API URL", default=API_URL)
    p.add_argument("--field", help="Form field name", default=FIELD_NAME)
    p.add_argument("--no-auth", help="Remove configured headers (disable auth)", action="store_true")
    args = p.parse_args()

    if args.no_auth:
        headers = {}
    else:
        headers = HEADERS

    if not os.path.isdir(args.directory):
        print(f"Directory not found: {args.directory}", file=sys.stderr)
        sys.exit(2)

    path = find_most_recent_file(args.directory)
    if not path:
        print("No files found in directory.", file=sys.stderr)
        sys.exit(3)

    try:
        resp = send_file(path, args.url, args.field, headers, TIMEOUT)
    except requests.RequestException as e:
        print(f"Upload failed: {e}", file=sys.stderr)
        sys.exit(4)

    print(f"Uploaded: {os.path.basename(path)} -> {args.url} (status {resp.status_code})")
    print(resp.text)

if __name__ == "__main__":
    main()
