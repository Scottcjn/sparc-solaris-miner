#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RustChain Miner for SPARC Solaris
Supports UltraSPARC I/II/III/IV on Solaris 10

Christmas 2025 - Elyan Labs
"The Sun still shines on SPARC"
"""

from __future__ import print_function
import os
import sys
import time
import socket
import hashlib
import subprocess
import re

# Python 2/3 compatibility
try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import urlopen, Request, URLError, HTTPError
    from urllib import urlencode

try:
    import json
except ImportError:
    import simplejson as json

# Configuration
NODE_URL = "http://50.28.86.131:8088"  # HTTP for old TLS
NODE_URL_HTTPS = "https://50.28.86.131"
ATTEST_INTERVAL = 300  # 5 minutes
VERSION = "1.0.0-sparc"

# SPARC antiquity multipliers
SPARC_MULTIPLIERS = {
    "UltraSPARC-I": 1.8,
    "UltraSPARC-II": 1.6,
    "UltraSPARC-IIi": 1.6,
    "UltraSPARC-IIe": 1.5,
    "UltraSPARC-III": 1.4,
    "UltraSPARC-IIIi": 1.4,
    "UltraSPARC-IV": 1.3,
    "SPARC64": 1.5,
    "SPARC-T": 1.1,  # T-series, more modern
    "unknown": 1.2,
}


def get_sparc_cpu_info():
    """Detect SPARC CPU type and details"""
    cpu_info = {
        "arch": "sparc",
        "family": "UltraSPARC",
        "model": "unknown",
        "clock_mhz": 0,
        "ncpus": 1,
        "impl": "",
    }

    # Try prtconf first
    try:
        output = subprocess.check_output(["/usr/sbin/prtconf", "-v"],
                                         stderr=subprocess.STDOUT)
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")

        # Parse CPU model
        for line in output.split("\n"):
            if "UltraSPARC" in line or "SPARC" in line:
                # Extract model
                match = re.search(r"(UltraSPARC[^\s,]+|SPARC64[^\s,]*|SPARC-T\d+)", line)
                if match:
                    cpu_info["model"] = match.group(1)
                    break
    except Exception as e:
        print("prtconf failed: %s" % e)

    # Try psrinfo for clock speed and count
    try:
        output = subprocess.check_output(["/usr/sbin/psrinfo", "-v"],
                                         stderr=subprocess.STDOUT)
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")

        # Count CPUs
        cpu_info["ncpus"] = output.count("Status of virtual processor")
        if cpu_info["ncpus"] == 0:
            cpu_info["ncpus"] = output.count("on-line")

        # Get clock speed
        match = re.search(r"(\d+)\s*MHz", output)
        if match:
            cpu_info["clock_mhz"] = int(match.group(1))

        # Get implementation
        match = re.search(r"(UltraSPARC[^\s]+|SPARC64[^\s]*)", output)
        if match:
            cpu_info["impl"] = match.group(1)
            if not cpu_info["model"] or cpu_info["model"] == "unknown":
                cpu_info["model"] = match.group(1)
    except Exception as e:
        print("psrinfo failed: %s" % e)

    # Determine family for multiplier lookup
    model = cpu_info["model"]
    if "UltraSPARC-I" in model and "II" not in model:
        cpu_info["family"] = "UltraSPARC-I"
    elif "UltraSPARC-IIi" in model or "IIi" in model:
        cpu_info["family"] = "UltraSPARC-IIi"
    elif "UltraSPARC-IIe" in model or "IIe" in model:
        cpu_info["family"] = "UltraSPARC-IIe"
    elif "UltraSPARC-II" in model:
        cpu_info["family"] = "UltraSPARC-II"
    elif "UltraSPARC-IIIi" in model or "IIIi" in model:
        cpu_info["family"] = "UltraSPARC-IIIi"
    elif "UltraSPARC-III" in model:
        cpu_info["family"] = "UltraSPARC-III"
    elif "UltraSPARC-IV" in model:
        cpu_info["family"] = "UltraSPARC-IV"
    elif "SPARC64" in model:
        cpu_info["family"] = "SPARC64"
    elif "SPARC-T" in model or "T1" in model or "T2" in model:
        cpu_info["family"] = "SPARC-T"

    return cpu_info


def get_hostid():
    """Get Solaris hostid (unique to hardware)"""
    try:
        output = subprocess.check_output(["/usr/bin/hostid"],
                                         stderr=subprocess.STDOUT)
        if isinstance(output, bytes):
            output = output.decode("utf-8").strip()
        return output
    except:
        return "unknown"


def get_hardware_fingerprint():
    """Generate hardware fingerprint for SPARC"""
    fingerprint = {}

    # Get hostid (Solaris hardware serial)
    fingerprint["hostid"] = get_hostid()

    # Get prtconf hash
    try:
        output = subprocess.check_output(["/usr/sbin/prtconf"],
                                         stderr=subprocess.STDOUT)
        if isinstance(output, bytes):
            output = output.decode("utf-8", errors="replace")
        fingerprint["prtconf_hash"] = hashlib.sha256(output.encode()).hexdigest()[:16]
    except:
        fingerprint["prtconf_hash"] = "unknown"

    # Get OpenBoot PROM version
    try:
        output = subprocess.check_output(["/usr/sbin/prtconf", "-V"],
                                         stderr=subprocess.STDOUT)
        if isinstance(output, bytes):
            output = output.decode("utf-8").strip()
        fingerprint["obp_version"] = output
    except:
        fingerprint["obp_version"] = "unknown"

    # Check for virtualization
    fingerprint["is_zone"] = os.path.exists("/etc/zones") and os.path.exists("/.SUNWnative")
    fingerprint["is_ldom"] = os.path.exists("/dev/ldomsd")

    # Memory info
    try:
        output = subprocess.check_output(["/usr/sbin/prtconf"],
                                         stderr=subprocess.STDOUT)
        if isinstance(output, bytes):
            output = output.decode("utf-8")
        match = re.search(r"Memory size:\s*(\d+)", output)
        if match:
            fingerprint["memory_mb"] = int(match.group(1))
    except:
        fingerprint["memory_mb"] = 0

    return fingerprint


def check_vm_detection(fingerprint):
    """Check if running in VM/zone"""
    warnings = []

    if fingerprint.get("is_zone"):
        warnings.append("Running in Solaris Zone - minimal rewards")
    if fingerprint.get("is_ldom"):
        warnings.append("Running in LDOM - minimal rewards")
    if fingerprint.get("hostid") in ["unknown", "00000000", "ffffffff"]:
        warnings.append("Invalid hostid - may be VM")

    return warnings


def make_request(url, data=None, method="GET", proxy=None):
    """Make HTTP request with Python 2/3 compatibility"""
    headers = {
        "User-Agent": "RustChain-SPARC-Miner/%s" % VERSION,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if proxy:
        # Use proxy for HTTPS
        if url.startswith("https://"):
            url = proxy + "/" + url

    if data:
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode("utf-8")

    req = Request(url, data=data, headers=headers)
    if method == "POST" and data:
        req.add_header("Content-Length", len(data))

    try:
        response = urlopen(req, timeout=30)
        return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        print("HTTP Error %d: %s" % (e.code, e.reason))
        return None
    except URLError as e:
        print("URL Error: %s" % e.reason)
        return None
    except Exception as e:
        print("Request failed: %s" % e)
        return None


def submit_attestation(wallet, cpu_info, fingerprint, node_url, proxy=None):
    """Submit attestation to RustChain node"""

    # Build attestation payload
    payload = {
        "miner": wallet,
        "miner_id": "%s-%s" % (wallet, fingerprint.get("hostid", "sparc")),
        "nonce": int(time.time() * 1000),
        "device": {
            "model": cpu_info["model"],
            "arch": "sparc",
            "family": cpu_info["family"],
            "device_arch": cpu_info["family"].lower().replace("-", "_"),
            "clock_mhz": cpu_info["clock_mhz"],
            "ncpus": cpu_info["ncpus"],
        },
        "signals": {
            "hostid": fingerprint.get("hostid"),
            "prtconf_hash": fingerprint.get("prtconf_hash"),
            "obp_version": fingerprint.get("obp_version"),
            "memory_mb": fingerprint.get("memory_mb", 0),
            "is_zone": fingerprint.get("is_zone", False),
            "is_ldom": fingerprint.get("is_ldom", False),
        },
        "report": {
            "version": VERSION,
            "os": "Solaris",
            "os_version": get_solaris_version(),
        },
        "fingerprint": {
            "all_passed": not (fingerprint.get("is_zone") or fingerprint.get("is_ldom")),
            "checks": {
                "hostid": {"passed": fingerprint.get("hostid") not in ["unknown", "00000000"]},
                "prtconf": {"passed": fingerprint.get("prtconf_hash") != "unknown"},
                "anti_emulation": {
                    "passed": not (fingerprint.get("is_zone") or fingerprint.get("is_ldom")),
                    "data": {"is_zone": fingerprint.get("is_zone"), "is_ldom": fingerprint.get("is_ldom")}
                },
            }
        }
    }

    url = node_url + "/attest/submit"
    return make_request(url, data=payload, method="POST", proxy=proxy)


def get_solaris_version():
    """Get Solaris version string"""
    try:
        with open("/etc/release", "r") as f:
            return f.readline().strip()
    except:
        return "Solaris"


def print_banner(cpu_info, fingerprint):
    """Print startup banner"""
    multiplier = SPARC_MULTIPLIERS.get(cpu_info["family"], 1.2)

    print("")
    print("=" * 60)
    print("  RUSTCHAIN SPARC MINER v%s" % VERSION)
    print("  \"The Sun never sets on vintage hardware\"")
    print("=" * 60)
    print("")
    print("  Hardware Detected:")
    print("    CPU:        %s" % cpu_info["model"])
    print("    Clock:      %d MHz" % cpu_info["clock_mhz"])
    print("    CPUs:       %d" % cpu_info["ncpus"])
    print("    Hostid:     %s" % fingerprint.get("hostid", "unknown"))
    print("    Memory:     %d MB" % fingerprint.get("memory_mb", 0))
    print("    OBP:        %s" % fingerprint.get("obp_version", "unknown")[:40])
    print("")
    print("  Antiquity Bonus: %.1fx (%s)" % (multiplier, cpu_info["family"]))
    print("")

    # VM warnings
    warnings = check_vm_detection(fingerprint)
    if warnings:
        print("  WARNINGS:")
        for w in warnings:
            print("    ! %s" % w)
        print("")


def main():
    """Main miner loop"""
    import argparse

    parser = argparse.ArgumentParser(description="RustChain SPARC Miner")
    parser.add_argument("--wallet", required=True, help="Wallet name/ID")
    parser.add_argument("--proxy", help="TLS proxy URL (for HTTPS via old SSL)")
    parser.add_argument("--use-http", action="store_true", help="Use HTTP instead of HTTPS")
    parser.add_argument("--interval", type=int, default=300, help="Attestation interval (seconds)")
    parser.add_argument("--once", action="store_true", help="Attest once and exit")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually submit")
    parser.add_argument("--show-payload", action="store_true", help="Show attestation payload")

    args = parser.parse_args()

    # Detect hardware
    print("Detecting SPARC hardware...")
    cpu_info = get_sparc_cpu_info()
    fingerprint = get_hardware_fingerprint()

    # Print banner
    print_banner(cpu_info, fingerprint)

    # Determine node URL
    if args.use_http:
        node_url = NODE_URL
        print("  Using HTTP (less secure)")
    elif args.proxy:
        node_url = NODE_URL_HTTPS
        print("  Using HTTPS via proxy: %s" % args.proxy)
    else:
        node_url = NODE_URL_HTTPS
        print("  Using HTTPS direct")

    print("")
    print("  Wallet:  %s" % args.wallet)
    print("  Node:    %s" % node_url)
    print("")

    if args.show_payload:
        payload = {
            "miner": args.wallet,
            "device": {
                "model": cpu_info["model"],
                "arch": "sparc",
                "family": cpu_info["family"],
            },
            "signals": fingerprint,
        }
        print("Payload preview:")
        print(json.dumps(payload, indent=2))
        return

    if args.dry_run:
        print("DRY RUN - would submit attestation")
        return

    # Main loop
    print("Starting attestation loop (interval: %ds)" % args.interval)
    print("Press Ctrl+C to stop")
    print("")

    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print("[%s] Submitting attestation..." % timestamp)

        result = submit_attestation(
            args.wallet,
            cpu_info,
            fingerprint,
            node_url,
            proxy=args.proxy
        )

        if result:
            if result.get("ok"):
                print("  OK: Attestation accepted")
                if "next_window" in result:
                    print("  Next window: %s" % result["next_window"])
            else:
                print("  WARN: %s" % result.get("error", "Unknown error"))
        else:
            print("  FAIL: Could not reach node")

        if args.once:
            break

        print("  Sleeping %ds..." % args.interval)
        print("")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
