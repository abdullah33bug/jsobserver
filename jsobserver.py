#!/usr/bin/env python3
import os
import re
import time
import json
import requests
import jsbeautifier
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Configuration: add your slack token & slack channel id here
SLACK_TOKEN = "xoxb-100xxxxx-xxxxxx-xxxxxxx"
SLACK_CHANNEL_ID = "C0A1xxxxx"
if not SLACK_TOKEN or not SLACK_CHANNEL_ID:
    print("Error: SLACK_TOKEN and SLACK_CHANNEL_ID must be set")
    exit(1)

client = WebClient(token=SLACK_TOKEN)

# Path to directories; target & result
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TARGET_DIR = os.path.join(BASE_DIR, "target")
RESULT_DIR = os.path.join(BASE_DIR, "result")

os.makedirs(TARGET_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# jsobserver file for record scans history
mapping_file = os.path.join(BASE_DIR, "jsobserver.json")
# -------------------------------------------------------------------

# Load mapping of previous files (URL -> last file index)
if os.path.exists(mapping_file):
    with open(mapping_file, "r") as f:
        filemap = json.load(f)
else:
    filemap = {}

# number of retries are 5 for each js file
def fetch_with_retries(url, max_retries=5):
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, timeout=20)
            if resp.status_code == 200:
                return resp.text
            else:
                print(f"[!] Failed to GET {url} (status {resp.status_code}), attempt {attempt}/{max_retries}")
        except Exception as e:
            print(f"[!] Error fetching {url} on attempt {attempt}: {e}")
        time.sleep(30)
    print(f"[!] Giving up on {url} after {max_retries} attempts")
    return None

# fetching files from directory target to build a list
urls = []
for fname in os.listdir(TARGET_DIR):
    if fname.startswith("."):
        continue
    path = os.path.join(TARGET_DIR, fname)
    if os.path.isfile(path):
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)

existing = [
    f for f in os.listdir(RESULT_DIR)
    if f.lower().endswith(".txt") and f.split('.')[0].isdigit()
]
if existing:
    max_num = max(int(f.split('.')[0]) for f in existing)
else:
    max_num = 0

# Regex patterns
url_pattern = re.compile(r"https?://[^\'\"\s`]+")
path_pattern = re.compile(r'\/[^\s\'"]+')

# Endpoint validation
def is_valid_endpoint(p: str) -> bool:
    p_clean = p.strip()

    if re.search(r"\.(js|css|png|jpg|jpeg|svg|gif|webp|woff|woff2|ttf|map|ico|json)$", p_clean, re.IGNORECASE):
        return False
    if p_clean.startswith("/data:") or "data:image" in p_clean:
        return False
    if len(p_clean) > 300:
        return False
    if re.search(r'[A-Za-z0-9+/]{25,}={0,2}', p_clean):
        return False
    if re.search(r'[A-Fa-f0-9]{20,}', p_clean):
        return False

    static_indicators = [
        "/static/", "/assets/", "/images/", "/img/", "/cdn/", "/fonts/",
        "/_next/", "/chunks/", "/bundles/", "/node_modules/",
        "/sockjs-node", "/socket.io/"
    ]
    lower = p_clean.lower()
    for s in static_indicators:
        if s in lower:
            return False

    parts = [seg for seg in p_clean.split("/") if seg]
    if len(parts) < 2:
        return False
    if not re.search(r'[A-Za-z]', p_clean):
        return False
    if re.search(r'function\s*\(|=>|\bvar\b|\blet\b|\bconst\b', p_clean):
        return False
    if "?" in p_clean and len(p_clean.split("?")[0]) < 2:
        return False

    return True

# Process each target URL
for url in urls:
    print(f"\n[+] Processing {url}")
    content = fetch_with_retries(url)
    if not content:
        continue

    content = jsbeautifier.beautify(content)
    found = set()

    found.update(re.findall(url_pattern, content))

    for path in re.findall(path_pattern, content):
        if path.startswith("//"):
            continue
        path = path.rstrip('.,;)"\'`')
        if is_valid_endpoint(path):
            found.add(path)

    endpoints = sorted(found)

    max_num += 1
    out_fname = f"{max_num}.txt"
    out_path = os.path.join(RESULT_DIR, out_fname)

    with open(out_path, "w") as out:
        out.write(url + "\n")
        for ep in endpoints:
            out.write(ep + "\n")

    print(f"[+] Saved {len(endpoints)} endpoints to {out_fname}")

    prev_num = filemap.get(url)
    if prev_num:
        prev_path = os.path.join(RESULT_DIR, f"{prev_num}.txt")
        old_eps = []
        if os.path.exists(prev_path):
            with open(prev_path, "r") as f:
                old_eps = [line.strip() for line in f.readlines()[1:]]

        added = [ep for ep in endpoints if ep not in old_eps]

        if added:
            lines = [
                "JSObserver – JavaScript Change Alert 🚨",
                "New endpoints detected:",
            ]
            lines += [f"  - {ep}" for ep in added]
            lines += [
                f"JavaScript URL: {url}",
                f"Result file: {out_fname}"
            ]

            try:
                client.chat_postMessage(channel=SLACK_CHANNEL_ID, text="\n".join(lines))
                print("[+] Slack alert sent.")
            except SlackApiError as e:
                print(f"[!] Slack API error: {e.response['error']}")
        else:
            print("[*] No new endpoints found.")
    else:
        print("[*] No previous file to compare.")

    filemap[url] = max_num

# Save jsobserver state
with open(mapping_file, "w") as f:
    json.dump(filemap, f, indent=2)
