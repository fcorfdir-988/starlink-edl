#!/usr/bin/env python3
"""Genere des listes de prefixes Starlink utilisables comme External Dynamic List (EDL).

Source : geofeed officiel de Starlink (RFC 8805), https://geoip.starlinkisp.net/feed.csv
Sorties : starlink-ipv4.txt et starlink-ipv6.txt, un prefixe par ligne, agreges.
Le script ne modifie les fichiers que si le contenu change, et refuse de publier
une liste anormalement petite (telechargement tronque ou format change).
"""
import ipaddress
import pathlib
import sys
import time
import urllib.request

URL = "https://geoip.starlinkisp.net/feed.csv"
MIN_V4, MIN_V6 = 1000, 1000          # garde-fou sur le nombre de lignes du flux
MAX_ENTRIES = 50000                  # capacite d'une EDL PAN-OS de type IP
HEADER = [
    "# Starlink (SpaceX) - prefixes du geofeed officiel https://geoip.starlinkisp.net/feed.csv",
    "# Agreges (aucun doublon). Liste destinee a une External Dynamic List (type IP).",
]


def fetch() -> str:
    last = None
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(URL, headers={"User-Agent": "starlink-edl-updater"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8")
        except Exception as e:                      # noqa: BLE001
            last = e
            time.sleep(5 * attempt)
    sys.exit(f"telechargement impossible: {last}")


def parse(text: str):
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
        sys.exit(f"flux suspect: {len(v4)} IPv4 / {len(v6)} IPv6 (minimum {MIN_V4}/{MIN_V6}), rien n'est publie")
    a4 = sorted(ipaddress.collapse_addresses(v4), key=lambda n: (int(n.network_address), n.prefixlen))
    a6 = sorted(ipaddress.collapse_addresses(v6), key=lambda n: (int(n.network_address), n.prefixlen))
    if len(a4) + len(a6) > MAX_ENTRIES:
        sys.exit(f"{len(a4) + len(a6)} entrees: depasse la capacite d'une EDL ({MAX_ENTRIES})")
    here = pathlib.Path(__file__).resolve().parent
    c4 = write_if_changed(here / "starlink-ipv4.txt", a4, "IPv4")
    c6 = write_if_changed(here / "starlink-ipv6.txt", a6, "IPv6")
    print(f"IPv4: {len(v4)} -> {len(a4)} agreges ({'modifie' if c4 else 'inchange'}) | "
          f"IPv6: {len(v6)} -> {len(a6)} agreges ({'modifie' if c6 else 'inchange'})")


if __name__ == "__main__":
    main()
