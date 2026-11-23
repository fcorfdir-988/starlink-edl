#!/usr/bin/env python3
"""Build Starlink prefix lists usable as External Dynamic Lists (EDL) on a firewall.

Source:  Starlink's official geofeed (RFC 8805), https://geoip.starlinkisp.net/feed.csv
Output:  starlink-ipv4.txt and starlink-ipv6.txt, one aggregated prefix per line.

The files are only rewritten when their content changes, and the script refuses to
publish an abnormally small list (truncated download or changed feed format), so the
previous files stay in place if anything goes wrong.
"""
import ipaddress
import pathlib
import sys
import time
import urllib.request

URL = "https://geoip.starlinkisp.net/feed.csv"
MIN_V4, MIN_V6 = 1000, 1000          # sanity check on the number of feed lines per family
MAX_ENTRIES = 50000                  # capacity of a PAN-OS IP-type EDL
HEADER = [
    "# Starlink (SpaceX) prefixes from the official geofeed https://geoip.starlinkisp.net/feed.csv",
    "# Aggregated, no duplicates. Meant to be used as an External Dynamic List (IP type).",
]


def fetch() -> str:
    """Download the geofeed, with three attempts."""
    last = None
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(URL, headers={"User-Agent": "starlink-edl-updater"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8")
        except Exception as e:                      # noqa: BLE001
            last = e
            time.sleep(5 * attempt)
    sys.exit(f"download failed: {last}")


def parse(text: str):
    """Return the IPv4 and IPv6 networks listed in the first CSV column."""
    v4, v6 = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        prefix = line.split(",", 1)[0].strip()
        try:
            net = ipaddress.ip_network(prefix, strict=False)
        except ValueError:
            continue
        (v4 if net.version == 4 else v6).append(net)
    return v4, v6


def write_if_changed(path: pathlib.Path, nets, label: str) -> bool:
    body = "\n".join(HEADER + [f"# {label}: {len(nets)} prefixes"] + [str(n) for n in nets]) + "\n"
    if path.exists() and path.read_text() == body:
        return False
    path.write_text(body)
    return True


def main() -> None:
    v4, v6 = parse(fetch())
    if len(v4) < MIN_V4 or len(v6) < MIN_V6:
        sys.exit(f"suspicious feed: {len(v4)} IPv4 / {len(v6)} IPv6 "
                 f"(minimum {MIN_V4}/{MIN_V6}), nothing published")
    a4 = sorted(ipaddress.collapse_addresses(v4), key=lambda n: (int(n.network_address), n.prefixlen))
    a6 = sorted(ipaddress.collapse_addresses(v6), key=lambda n: (int(n.network_address), n.prefixlen))
    if len(a4) + len(a6) > MAX_ENTRIES:
        sys.exit(f"{len(a4) + len(a6)} entries: exceeds the EDL capacity ({MAX_ENTRIES})")
    here = pathlib.Path(__file__).resolve().parent
    c4 = write_if_changed(here / "starlink-ipv4.txt", a4, "IPv4")
    c6 = write_if_changed(here / "starlink-ipv6.txt", a6, "IPv6")
    print(f"IPv4: {len(v4)} -> {len(a4)} aggregated ({'changed' if c4 else 'unchanged'}) | "
          f"IPv6: {len(v6)} -> {len(a6)} aggregated ({'changed' if c6 else 'unchanged'})")


if __name__ == "__main__":
    main()
